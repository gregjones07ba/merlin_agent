#!/usr/bin/env python3
"""
Example: How to use the MerlinDMService class programmatically
"""

from merlin_dm_service import MerlinDMService
import time

api_gateway_url = "https://usffibi052.execute-api.us-east-1.amazonaws.com/prod/api/v1/1/messages"
game_id = 1234567890
model_id = "microsoft/Phi-3-mini-4k-instruct"

def example_basic_usage():
    """
    Basic example: Create a service and run it.
    """
    print("Example 1: Basic Service Setup\n")

    # example

    service = MerlinDMService(
        api_base_url=api_gateway_url,
        game_id=game_id,
        model_id=model_id,
        device="mps",  # or "cuda" or "cpu"
        poll_interval=5,
        temperature=0.7,
    )
    
    # This will run forever - use Ctrl+C to stop
    # service.run()
    
    print("Service created successfully!")
    print(f"API URL: {service.api_base_url}")
    print(f"Game ID: {service.game_id}")
    print(f"Model: microsoft/Phi-3-mini-4k-instruct")
    print(f"Device: {service.device}")


def example_custom_system_prompt():
    """
    Example: Use a custom DM personality.
    """
    print("\nExample 2: Custom DM Personality\n")
    
    # Create a comedic DM
    comedic_dm_prompt = """
    You are a hilarious Dungeon Master who runs fantasy adventures with a comedic twist.
    Everything is slightly absurd. Describe situations with humor, make witty observations,
    and give NPCs funny quirks. But still maintain a coherent story and challenge the players.
    Keep responses concise and end with a prompt for action.
    """
    
    service = MerlinDMService(
        api_base_url=api_gateway_url,
        game_id=game_id,
        model_id=model_id,
        system_prompt=comedic_dm_prompt,
        temperature=0.9,  # Higher for more creative responses
    )
    
    print("Comedic DM service created!")
    print(f"System prompt: {comedic_dm_prompt[:100]}...")


def example_manual_control():
    """
    Example: Manually control when to poll and respond.
    """
    print("\nExample 3: Manual Control\n")
    
    service = MerlinDMService(
        api_base_url=api_gateway_url,
        game_id="manual_game",
        model_id=model_id,
    )
    
    # Instead of service.run(), manually control:
    
    # 1. Fetch messages
    messages = service.get_messages()
    print(f"Fetched {len(messages)} messages")
    
    # 2. Process new messages once
    service.process_new_messages()
    
    # 3. Post a custom message
    service.post_message("Welcome, brave adventurer!")
    
    print("Manual operations completed!")


def example_test_generation():
    """
    Example: Test the LLM generation without API calls.
    """
    print("\nExample 4: Test Generation (No API)\n")
    
    service = MerlinDMService(
        api_base_url="https://dummy-url.com",  # Not actually used
        game_id="test",
        model_id=model_id,
    )
    
    # Manually build a conversation
    from merlin_dm_service import Turn
    
    service.history = [
        Turn(role="user", content="I enter the dark tavern."),
    ]
    
    # Generate a response
    prompt = service._build_prompt(service.history)
    response = service.generate_response(prompt)
    
    print("Player: I enter the dark tavern.")
    print(f"DM: {response}")


def example_different_models():
    """
    Example: Using different models.
    """
    print("\nExample 5: Different Models\n")
    
    # Small, fast model for quick responses
    fast_service = MerlinDMService(
        api_base_url="https://your-api-gateway-url.amazonaws.com",
        game_id="fast_game",
        model_id="microsoft/Phi-3-mini-4k-instruct",
        max_new_tokens=128,
    )
    
    # Larger model for richer narratives
    rich_service = MerlinDMService(
        api_base_url="https://your-api-gateway-url.amazonaws.com",
        game_id="rich_game",
        model_id="mistralai/Mistral-7B-Instruct-v0.2",
        max_new_tokens=512,
        temperature=0.8,
    )
    
    print("Fast service: Phi-3-mini (128 tokens)")
    print("Rich service: Mistral-7B (512 tokens)")


if __name__ == "__main__":
    print("=" * 60)
    print("Merlin DM Service - Usage Examples")
    print("=" * 60)
    
    example_basic_usage()
    example_custom_system_prompt()
    example_manual_control()
    # example_test_generation()  # Uncomment to test generation
    example_different_models()
    
    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)
    print("\nTo actually run the service:")
    print("python merlin_dm_service.py --api-url <url> --game-id <id>")
