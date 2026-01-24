# merlin_agent

## merlin_infra and merlin_api
A serverless backend infrastructure on AWS for the AI-based DM (Dungeon Master) app called Merlin.

### 🏗️ merlin_infra - Infrastructure as Code
This uses AWS CDK (Cloud Development Kit) to define and deploy all the AWS resources. The main file is merlin_stack.py, which creates:

1. **DynamoDB Table** (messages)
- **Purpose:** Stores all game messages
- **Structure**:
    - **Partition key**: game (string) - identifies which game session
    - **Sort key**: seq (number) - message sequence number for ordering
  
    Each message includes: id, user info (id & type), and effect (the actual message content)

2. **Two Lambda Functions** (serverless compute)
- **getMessages**: Retrieves messages from a game
- **postMessage**: Adds new messages to a game

3. **API Gateway REST API**
Creates a public HTTP API with the structure:

    - **GET /api/v1/{game}/messages** - fetch messages (with optional start and end query params)
    - **POST /api/v1/{game}/messages** - add a new message
  
4. **S3 Bucket**
Stores the Lambda function code (zip files)


### 📡 merlin_api - The Backend Logic
This contains the actual Python code that runs in the Lambda functions:

- **getMessages Lambda**
Retrieves up to 10 messages from a specific game

    - **Query options**:
        - **No params**: gets the 10 most recent messages
        - **start param**: gets messages after sequence number
        - **end param**: gets messages before sequence number
        - **start & end**: gets messages in that range

    **Returns**: Array of message objects with id, seq, user info, and effect

- **postMessage Lambda**
Adds a new message to a game

  - Queries for the latest message in the game
  - Assigns the next sequence number (seq)
  - Stores the message in DynamoDB
  - Retry logic: Has built-in retry mechanism for concurrent writes
  <br/>
  - **Input format**: Game ID + payload containing message details

### 🔄 How It All Works Together
Web/Agent → API Gateway → Lambda → DynamoDB

Messages are stored with auto-incrementing sequence numbers per game

The API supports pagination/filtering by sequence numbers

Each message has:
 - Unique id (UUID)
 - user info (player/AI identification)
 - effect (the actual message content - like "I cast Fireball!")


### 🚀 Deployment Process
Refer to Readme under merlin_infra

