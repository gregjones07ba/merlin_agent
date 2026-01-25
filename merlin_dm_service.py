#!/usr/bin/env python3
"""
Merlin DM Service - AI Dungeon Master that integrates with the Merlin API
Polls for new player messages and responds with AI-generated DM narration.
"""

import json
import logging
import time
import uuid
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from pathlib import Path

import requests
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Represents a message in the game"""
    id: str
    seq: int
    user_id: int
    user_type: str  # "player" or "dm"
    effect: Dict[str, Any]  # Contains 'text' and potentially other game effects


@dataclass
class Turn:
    """Represents a conversational turn for the LLM"""
    role: str  # "user" or "assistant"
    content: str


class MerlinDMService:
    """
    Service that monitors a game for player messages and generates DM responses.
    """
    
    def __init__(
        self,
        api_base_url: str,
        game_id: str,
        model_id: str,
        system_prompt: Optional[str] = None,
        device: Optional[str] = None,
        poll_interval: int = 5,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        max_new_tokens: int = 256,
    ):
        """
        Initialize the Merlin DM Service.
        
        Args:
            api_base_url: Base URL of the API (e.g., "https://api.example.com")
            game_id: The game ID to monitor
            model_id: HuggingFace model ID or local path
            system_prompt: System prompt for the DM persona
            device: Device to run on ("mps", "cuda", "cpu", or None for auto)
            poll_interval: Seconds between polling for new messages
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            max_new_tokens: Maximum tokens to generate
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.game_id = game_id
        self.poll_interval = poll_interval
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.max_new_tokens = max_new_tokens
        
        # Default DM system prompt
        self.system_prompt = system_prompt or (
            "You are a creative and engaging Dungeon Master guiding players through "
            "an epic fantasy adventure. Describe environments vividly, present interesting "
            "challenges, respond to player actions dynamically, and keep the story moving "
            "forward. Be concise but evocative. End responses with a natural prompt for "
            "player action."
        )
        
        # Set up device
        self.device = self._pick_device(device)
        logger.info(f"Using device: {self.device}")
        
        # Load model and tokenizer
        logger.info(f"Loading model: {model_id}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        dtype = torch.float16 if self.device == "mps" else torch.float32
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=dtype,
            device_map={"": self.device}
        )
        logger.info("Model loaded successfully")
        
        # Track the last message sequence number we've seen
        self.last_seq: int = -1
        
        # Maintain conversation history
        self.history: List[Turn] = []
    
    def _pick_device(self, user_choice: Optional[str]) -> str:
        """Automatically select the best available device."""
        if user_choice:
            return user_choice
        if torch.backends.mps.is_available():
            return "mps"
        if torch.cuda.is_available():
            return "cuda"
        return "cpu"
    
    def _build_prompt(self, turns: List[Turn]) -> str:
        """Build the prompt for the LLM using chat template or fallback."""
        if hasattr(self.tokenizer, "apply_chat_template"):
            try:
                messages = [{"role": "system", "content": self.system_prompt}]
                messages.extend([{"role": t.role, "content": t.content} for t in turns])
                return self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
            except Exception as e:
                logger.warning(f"Chat template failed, using manual format: {e}")
        
        # Fallback: manual prompt building
        parts = [self.system_prompt]
        for t in turns:
            if t.role == "user":
                parts.append(f"\n\nPlayer: {t.content}")
            else:
                parts.append(f"\n\nDM: {t.content}")
        parts.append("\n\nDM:")
        return "".join(parts)
    
    def get_messages(self, start_seq: Optional[int] = None) -> List[Message]:
        """
        Fetch messages from the API.
        
        Args:
            start_seq: Only fetch messages after this sequence number
            
        Returns:
            List of Message objects, ordered by sequence number
        """
        url = f"{self.api_base_url}/api/v1/{self.game_id}/messages"
        params = {}
        if start_seq is not None:
            params['start'] = start_seq
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            messages = []
            for msg_data in data.get('messages', []):
                messages.append(Message(
                    id=msg_data['id'],
                    seq=msg_data['seq'],
                    user_id=msg_data['user']['id'],
                    user_type=msg_data['user']['type'],
                    effect=msg_data['effect']
                ))
            
            # Sort by sequence number (API returns in reverse order)
            messages.sort(key=lambda m: m.seq)
            return messages
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch messages: {e}")
            return []
    
    def post_message(self, text: str, effect_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Post a DM message to the API.
        
        Args:
            text: The DM's message text
            effect_data: Additional effect data (dice rolls, stat changes, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        url = f"{self.api_base_url}/api/v1/{self.game_id}/messages"
        
        effect = {"text": text}
        if effect_data:
            effect.update(effect_data)
        
        payload = {
            "id": str(uuid.uuid4()),
            "user": {
                "id": 0,  # DM user ID
                "type": "dm"
            },
            "effect": effect
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Posted message successfully")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to post message: {e}")
            return False
    
    def generate_response(self, prompt_text: str) -> str:
        """
        Generate a response using the LLM.
        """
        inputs = self.tokenizer(prompt_text, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.05,
            )
        
        # Decode only the new tokens (skip the prompt)
        generated_text = self.tokenizer.decode(
            outputs[0][inputs['input_ids'].shape[1]:],
            skip_special_tokens=True
        )
        
        return generated_text.strip()
    
    def process_new_messages(self) -> None:
        """
        Check for new player messages and respond to them.
        """
        # Fetch messages after our last seen sequence
        messages = self.get_messages(start_seq=self.last_seq if self.last_seq >= 0 else None)
        
        if not messages:
            return
        
        # Filter to only player messages we haven't seen yet
        new_player_messages = [
            msg for msg in messages
            if msg.user_type == "player" and msg.seq > self.last_seq
        ]
        
        if not new_player_messages:
            # Update last_seq even if no player messages (might be our own DM messages)
            self.last_seq = max(msg.seq for msg in messages)
            return
        
        logger.info(f"Found {len(new_player_messages)} new player message(s)")
        
        # Process each new player message
        for msg in new_player_messages:
            player_text = msg.effect.get('text', '')
            logger.info(f"Player message (seq={msg.seq}): {player_text}")
            
            # Add to conversation history
            self.history.append(Turn(role="user", content=player_text))
            
            # Generate DM response
            prompt = self._build_prompt(self.history)
            dm_response = self.generate_response(prompt)
            logger.info(f"DM response: {dm_response}")
            
            # Add to history
            self.history.append(Turn(role="assistant", content=dm_response))
            
            # Post response to API
            if self.post_message(dm_response):
                logger.info("DM response posted successfully")
            else:
                logger.error("Failed to post DM response")
            
            # Update last seen sequence
            self.last_seq = msg.seq
    
    def run(self) -> None:
        """
        Main service loop - continuously poll for new messages and respond.
        """
        logger.info(f"Starting Merlin DM Service for game '{self.game_id}'")
        logger.info(f"Polling API every {self.poll_interval} seconds")
        logger.info("Press Ctrl+C to stop")
        
        # Initialize by fetching existing messages
        logger.info("Fetching existing game history...")
        messages = self.get_messages()
        if messages:
            logger.info(f"Found {len(messages)} existing messages")
            # Rebuild history from existing messages
            for msg in messages:
                text = msg.effect.get('text', '')
                if msg.user_type == "player":
                    self.history.append(Turn(role="user", content=text))
                elif msg.user_type == "dm":
                    self.history.append(Turn(role="assistant", content=text))
                self.last_seq = msg.seq
            logger.info(f"Loaded history up to seq={self.last_seq}")
        else:
            logger.info("No existing messages found - starting fresh game")
        
        # Main polling loop
        try:
            while True:
                try:
                    self.process_new_messages()
                except Exception as e:
                    logger.error(f"Error processing messages: {e}", exc_info=True)
                
                time.sleep(self.poll_interval)
                
        except KeyboardInterrupt:
            logger.info("\nShutting down Merlin DM Service")


def main():
    """
    Example usage - configure and run the service.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Merlin DM Service")
    parser.add_argument("--api-url", required=True, help="Base URL of the Merlin API")
    parser.add_argument("--game-id", required=True, help="Game ID to monitor")
    parser.add_argument("--model", default="microsoft/Phi-3-mini-4k-instruct",
                       help="Model ID or path")
    parser.add_argument("--device", choices=["mps", "cuda", "cpu"], default=None,
                       help="Device to use (default: auto)")
    parser.add_argument("--poll-interval", type=int, default=5,
                       help="Seconds between API polls")
    parser.add_argument("--temperature", type=float, default=0.7,
                       help="Sampling temperature")
    parser.add_argument("--max-tokens", type=int, default=256,
                       help="Maximum tokens to generate")
    
    args = parser.parse_args()
    
    service = MerlinDMService(
        api_base_url=args.api_url,
        game_id=args.game_id,
        model_id=args.model,
        device=args.device,
        poll_interval=args.poll_interval,
        temperature=args.temperature,
        max_new_tokens=args.max_tokens,
    )
    
    service.run()


if __name__ == "__main__":
    main()
