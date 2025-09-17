# Telegram Buddy AI

AI agent for developer conversations with action item detection and context management.

## Features

- Copy/paste web interface for message input
- Telegram bot integration for real-time conversation tracking
- Azure OpenAI integration for intelligent responses
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
# Edit .env with your Azure OpenAI and Telegram bot credentials
```

3. **Run web interface:**
```bash
uvicorn app.main:app --reload
```

4. **Run Telegram bot (separate terminal):**
```bash
python telegram_runner.py
```

5. **Access interface:**
- Web: http://localhost:8000
- Telegram: Add your bot to a group and send `/start`

## Docker Deployment (Ubuntu Server)

1. **Setup:**
```bash
git clone <repository>
cd telegram-buddy-ai
cp .env.example .env
# Edit .env with your API keys and bot token
```

2. **Deploy:**
```bash
./deploy.sh
```

3. **Access:**
- Web interface: http://your-server:8000
- Telegram bot: Automatically running

4. **Monitor:**
```bash
cd docker
docker-compose logs web          # Web interface logs
docker-compose logs telegram-bot # Telegram bot logs
docker-compose logs -f           # Follow all logs
```

5. **Stop:**
```bash
cd docker
docker-compose down
```

## Environment Variables

Required in `.env` file:

```bash
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_API_VERSION=2025-01-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather

# Application
STRANDS_MODEL_PROVIDER=azure
DEBUG=true
HOST=0.0.0.0
PORT=8000
```

## Usage

### Web Interface
1. **Add Messages:** Paste developer conversations into the message input
2. **Ask Questions:** Query the buddy about tasks, status, or project details
3. **View Actions:** See detected action items from conversations
4. **Check Context:** Review conversation history and context

### Telegram Bot
1. **Add bot to group:** Invite your bot to a developer group
2. **Activate:** Send `/start` in the group
3. **Automatic tracking:** Bot tracks all messages and detects action items
4. **Commands:**
   - `/ask <question>` - Ask about project status
   - `/status` - Show conversation summary
   - `/actions` - List unresolved action items
   - `/help` - Show help message

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
- **Telegram Bot** for real-time conversation tracking
- **Azure OpenAI** integration for AI capabilities
- **Pydantic** models for data validation
- **Simple HTML/JS** frontend
- **Docker** containerization with multi-service setup
- **Modular** design for easy extension

## Deployment Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Web Service   │    │ Telegram Bot    │
│   (Port 8000)   │    │   Service       │
│                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │   FastAPI   │ │    │ │ Bot Handler │ │
│ │   Routes    │ │    │ │   Logic     │ │
│ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────┬───────────┘
                     │
            ┌─────────────────┐
            │ Shared Services │
            │                 │
            │ • Context Mgr   │
            │ • Buddy Agent   │
            │ • Azure OpenAI  │
            └─────────────────┘
```
