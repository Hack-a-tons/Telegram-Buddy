# Amazon Q CLI Project Setup - Telegram Buddy AI

## Project Overview for Amazon Q

**Project Name**: Telegram Buddy AI  
**Primary Goal**: Build an AI agent that can participate in developer conversations, track context, detect action items, and answer project-related questions.  
**Development Environment**: macOS (local development)  
**Deployment Environment**: Ubuntu 24.04 server with Docker and docker-compose  
**Timeline**: Hackathon project (2.5 hours remaining)  

## Architecture Summary for Amazon Q

The system follows a modular architecture with these key components:

1. **Message Router**: Receives and normalizes messages from various sources
2. **Project Classifier Agent**: Uses AWS Strands to categorize messages by project
3. **Context Manager**: Maintains conversation history and tracks unresolved items
4. **Core Buddy Agent**: Main intelligence using AWS Strands Agents SDK
5. **Response Engine**: Determines when and how to respond
6. **Input/Output Connectors**: Starting with copy/paste, expandable to Telegram/Discord/Slack

## Phase 1: Core Implementation (Hackathon Focus)

### Required Dependencies
```
- Python 3.9+
- AWS Strands Agents SDK
- OpenAI or Anthropic API (for LLM)
- FastAPI (for web interface)
- Pydantic (for data models)
- python-dotenv (for environment variables)
- uvicorn (for local development server)
```

### Project Structure
```
telegram-buddy-ai/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI entry point
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── buddy_agent.py          # Main AWS Strands Agent
│   │   ├── classifier_agent.py     # Project classification
│   │   └── action_detector.py      # Action item detection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── message.py              # Message schema
│   │   ├── context.py              # Context models
│   │   └── project.py              # Project models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── context_manager.py      # Memory management
│   │   ├── message_router.py       # Message routing
│   │   └── response_engine.py      # Response logic
│   └── api/
│       ├── __init__.py
│       └── routes.py               # API endpoints
├── frontend/                       # Simple HTML/JS for copy/paste interface
│   ├── index.html
│   ├── script.js
│   └── style.css
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

### Core Features to Implement

#### 1. Message Models (Pydantic)
```python
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Optional

class Message(BaseModel):
    content: str
    timestamp: datetime
    source: str  # "copy_paste", "telegram", "discord"
    channel_id: str
    user_id: str
    message_id: str
    metadata: Dict = {}

class ProjectTag(BaseModel):
    project_id: str
    project_name: str
    confidence: float

class ActionItem(BaseModel):
    description: str
    mentioned_at: datetime
    assigned_to: Optional[str] = None
    status: str = "unresolved"
    project_id: str
```

#### 2. AWS Strands Agent Integration
- Use the Strands Agents SDK for the main intelligence
- Implement question-answering capabilities
- Add context awareness for project-specific queries
- Integrate with available pre-built tools

#### 3. Context Management
- Store conversation history in memory (for hackathon)
- Track unresolved action items
- Maintain project-specific context windows
- Implement simple search/retrieval

#### 4. API Endpoints (FastAPI)
```
POST /message        # Submit new message
GET /context/{project_id}   # Get project context
GET /actions/{project_id}   # Get unresolved action items
POST /query          # Ask the buddy a question
GET /projects        # List all projects
```

#### 5. Copy/Paste Interface
- Simple HTML form for message input
- Display conversation context
- Show detected action items
- Query interface for asking questions

### Environment Variables Required
```
# .env file
OPENAI_API_KEY=your_openai_key
# or
ANTHROPIC_API_KEY=your_anthropic_key

# AWS Strands Configuration
STRANDS_MODEL_PROVIDER=openai  # or anthropic
STRANDS_MODEL_NAME=gpt-4  # or claude-3-sonnet

# Application Settings
DEBUG=true
HOST=0.0.0.0
PORT=8000
```

### Docker Configuration

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY frontend/ ./frontend/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  telegram-buddy-ai:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./data:/app/data  # For persistent storage
    restart: unless-stopped

  # Optional: Add Redis for better caching later
  # redis:
  #   image: redis:7-alpine
  #   restart: unless-stopped
```

### Development Workflow

#### Local Development (macOS)
1. Create virtual environment
2. Install dependencies
3. Set up environment variables
4. Run with `uvicorn app.main:app --reload`
5. Access web interface at http://localhost:8000

#### Deployment (Ubuntu 24.04)
1. Clone repository
2. Set up environment variables
3. Run `docker-compose up -d`
4. Access at http://server-ip:8000

### Testing Strategy

#### Manual Testing Scenarios
1. **Basic Message Processing**: Copy/paste a developer conversation
2. **Context Tracking**: Verify conversation history is maintained
3. **Question Answering**: Ask "What are we working on?"
4. **Action Item Detection**: Include messages with unresolved tasks
5. **Project Classification**: Test with multi-project conversations

### Demo Script for Hackathon

#### Sample Input Messages
```
"Hey team, we need to finish the API integration by Friday. The authentication service is almost done but we still need to implement the rate limiting."

"@john can you review the pull request for the user dashboard? It's been sitting there for 3 days."

"The database migration is failing in staging. We should investigate this before the weekend."

"Great job on the login flow! The UI looks much better now."
```

#### Demo Flow
1. Show the copy/paste interface
2. Input sample conversation
3. Ask: "What tasks need to be completed?"
4. Ask: "What's the status of the API integration?"
5. Show detected action items
6. Demonstrate project context awareness

### Success Criteria for Hackathon
- ✅ Working copy/paste interface
- ✅ AWS Strands agent responds to queries
- ✅ Basic context tracking
- ✅ Action item detection
- ✅ Deployable with Docker
- ✅ Clear demo storyline

### Post-Hackathon Extensions
- Telegram bot integration
- Discord/Slack connectors
- Multi-project classification
- Persistent database storage
- Advanced memory management
- Proactive notifications

## Amazon Q Implementation Notes

When working with Amazon Q CLI:

1. **Start with the project structure** - Create all directories and files
2. **Implement models first** - Define data structures clearly
3. **Build core agent** - Focus on AWS Strands integration
4. **Add API layer** - FastAPI for web interface
5. **Create simple frontend** - Basic HTML/JS for demo
6. **Containerize** - Docker setup for deployment

The modular architecture ensures each component can be developed and tested independently, perfect for Amazon Q's iterative development approach.