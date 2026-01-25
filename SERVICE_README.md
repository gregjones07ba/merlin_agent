# Merlin DM Service Configuration

# Example configuration for running the DM service

## Running the Service

```bash
python merlin_dm_service.py \
    --api-url "https://your-api-gateway-url.amazonaws.com" \
    --game-id "game_001" \
    --model "microsoft/Phi-3-mini-4k-instruct" \
    --device mps \
    --poll-interval 5 \
    --temperature 0.7 \
    --max-tokens 256
```

## Configuration Options

- `--api-url`: The API Gateway URL from your CDK deployment
- `--game-id`: Unique identifier for the game session
- `--model`: HuggingFace model ID (or local path to a model)
- `--device`: Computing device (mps/cuda/cpu, defaults to auto-detect)
- `--poll-interval`: How often to check for new messages (in seconds)
- `--temperature`: Creativity of responses (0.0 = deterministic, 1.0 = very creative)
- `--max-tokens`: Maximum length of generated responses

## Requirements

Make sure you have these packages installed:

```bash
pip install torch transformers requests
```

## Architecture

The service works as follows:

1. **Initialize**: Loads the LLM model and fetches existing game history
2. **Poll**: Every N seconds, checks the API for new player messages
3. **Generate**: When a new player message is found, generates a DM response using the LLM
4. **Post**: Sends the DM response back to the API
5. **Repeat**: Continues polling indefinitely

## Testing Locally

You can test the API integration without the full service:

```python
from merlin_dm_service import MerlinDMService

# Create service (doesn't start polling yet)
service = MerlinDMService(
    api_base_url="https://your-api.amazonaws.com",
    game_id="test_game",
    model_id="microsoft/Phi-3-mini-4k-instruct"
)

# Manually test fetching messages
messages = service.get_messages()
print(f"Found {len(messages)} messages")

# Manually test posting a message
service.post_message("Welcome to the adventure!")

# Or run the full service
service.run()
```

## Production Deployment

For production, you might want to:

1. **Containerize**: Create a Docker container for the service
2. **Run on EC2/ECS**: Deploy to AWS for always-on availability
3. **Add monitoring**: Use CloudWatch for logs and health checks
4. **Handle multiple games**: Run multiple instances or use threading
5. **Add authentication**: Secure API calls with API keys or IAM

## Differences from run_instruct_mps_chat7.py

| Feature | Interactive Script | DM Service |
|---------|-------------------|------------|
| Interface | Terminal/console | HTTP API |
| Interaction | User types directly | Polls for messages |
| History | In-memory only | Synced with database |
| Deployment | Local machine | Server/container |
| Multiple users | Single user | Multiple players |
| Persistence | Session-based | Database-backed |
