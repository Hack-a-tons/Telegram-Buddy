# Telegram Buddy AI

AI agent for developer conversations with action item detection and context management.

## Features

- Copy/paste web interface for message input
- AWS Strands agent integration for Q&A
- Action item detection from conversations
- Simple context management
- Docker deployment for Ubuntu

## Quick Start (macOS Development)

1. **Setup environment:**
```bash
cd telegram-buddy-ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Run locally:**
```bash
uvicorn app.main:app --reload
```

4. **Access interface:**
Open http://localhost:8000

## Docker Deployment (Ubuntu)

1. **Setup:**
```bash
git clone <repository>
cd telegram-buddy-ai
cp .env.example .env
# Edit .env with your API keys
```

2. **Deploy:**
```bash
cd docker
docker-compose up -d
```

3. **Access:**
Open http://your-server:8000

## Usage

1. **Add Messages:** Paste developer conversations into the message input
2. **Ask Questions:** Query the buddy about tasks, status, or project details
3. **View Actions:** See detected action items from conversations
4. **Check Context:** Review conversation history and context

## Demo Script

Try these sample messages:
```
"Hey team, we need to finish the API integration by Friday. The authentication service is almost done but we still need to implement the rate limiting."

"@john can you review the pull request for the user dashboard? It's been sitting there for 3 days."

"The database migration is failing in staging. We should investigate this before the weekend."
```

Then ask:
- "What tasks need to be completed?"
- "What's the status of the API integration?"
- "Show me the action items"

## Architecture

- **FastAPI** backend with REST API
- **Pydantic** models for data validation
- **AWS Strands** integration for AI capabilities
- **Simple HTML/JS** frontend
- **Docker** containerization
- **Modular** design for easy extension
