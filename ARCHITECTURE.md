# Merlin Architecture Overview

## System Components

```
┌─────────────────┐
│   merlin_web    │  Web Frontend (Your work)
│  (React/Vue?)   │  
└────────┬────────┘
         │ HTTP
         ↓
┌─────────────────┐
│  API Gateway    │  REST API
│  /api/v1/...    │  (merlin_infra)
└────────┬────────┘
         │
    ┌────┴────┐
    ↓         ↓
┌────────┐  ┌────────┐
│Lambda  │  │Lambda  │  (merlin_api)
│GET     │  │POST    │
└───┬────┘  └───┬────┘
    └─────┬─────┘
          ↓
    ┌──────────┐
    │ DynamoDB │  Message Storage
    │ messages │
    └──────────┘
          ↑
          │ Poll & Post
    ┌─────┴──────┐
    │merlin_agent│  AI DM Service (Your work)
    │  (LLM)     │
    └────────────┘
```

## Data Flow

### 1. Player Sends Message
```
Player (Web) → API Gateway → postMessage Lambda → DynamoDB
                                                      ↓
                                                  {game, seq, user, effect}
```

### 2. AI DM Responds
```
merlin_agent polls API → getMessages Lambda → DynamoDB
                                                 ↓
                                           Read messages
                                                 ↓
                                        Generate response (LLM)
                                                 ↓
merlin_agent posts → API Gateway → postMessage Lambda → DynamoDB
```

### 3. Player Sees Response
```
Web polls/refreshes → API Gateway → getMessages Lambda → DynamoDB → Display
```

## Message Structure

Each message in DynamoDB:

```json
{
  "game": "game_001",          // Partition key
  "seq": 5,                    // Sort key (auto-incrementing)
  "id": "uuid-here",           // Unique message ID
  "user.id": 123,              // User/Player ID (0 = DM)
  "user.type": "player",       // "player" or "dm"
  "effect": "{\"text\": \"I attack the dragon!\"}"  // JSON string
}
```

## API Endpoints

### GET `/api/v1/{game}/messages`
Fetch messages from a game.

**Query Parameters:**
- `start` (optional): Get messages after this sequence number
- `end` (optional): Get messages before this sequence number

**Response:**
```json
{
  "messages": [
    {
      "id": "uuid",
      "seq": 5,
      "user": {"id": 1, "type": "player"},
      "effect": {"text": "I attack the dragon!"}
    }
  ]
}
```

### POST `/api/v1/{game}/messages`
Add a new message to a game.

**Request Body:**
```json
{
  "id": "uuid",
  "user": {"id": 1, "type": "player"},
  "effect": {"text": "I attack the dragon!"}
}
```

**Response:**
```json
{}
```

## Integration Points

### For merlin_agent (AI DM)
- Poll `GET /api/v1/{game}/messages?start={last_seq}` every few seconds
- When new player messages found:
  - Generate AI response using LLM
  - Post response via `POST /api/v1/{game}/messages`

### For merlin_web (Frontend)
- Display messages by fetching `GET /api/v1/{game}/messages`
- Send player input via `POST /api/v1/{game}/messages`
- Poll for new messages (or use WebSocket if added later)

## Development Workflow

1. **Deploy Infrastructure** (merlin_infra)
   - Run CDK to create API Gateway, Lambda, DynamoDB
   - Get API Gateway URL

2. **Test API** (merlin_api)
   - Use `test_api_client.py` to verify endpoints
   - Post test messages, fetch messages

3. **Run AI Service** (merlin_agent)
   - Start `merlin_dm_service.py` with API URL
   - Watch it respond to player messages

4. **Build Frontend** (merlin_web)
   - Connect to API Gateway
   - Display messages, send player input

## Local Development

### Testing Without Full Deployment

1. **Mock API**: Create a local Flask/FastAPI server that mimics the API
2. **Test DM**: Run `merlin_dm_service.py` against mock API
3. **Test Web**: Build UI against mock API

### Testing With Real AWS

1. Deploy infrastructure once
2. Share API Gateway URL between team members
3. Multiple developers can test against same backend

## Future Enhancements

- **WebSockets**: Real-time updates instead of polling
- **Authentication**: User login and game ownership
- **Multiple DMs**: Support different AI personalities per game
- **Game State**: Track inventory, stats, location beyond messages
- **Dice Integration**: DM service handles dice rolls automatically
- **Rich Effects**: Support images, sound effects, stat changes in messages
