from ..models.message import Message

class ResponseEngine:
    def __init__(self):
        pass
    
    def should_respond(self, message: Message, bot_mentioned: bool = False) -> bool:
        """Determine if the bot should respond to this message"""
        
        # Always respond if bot is mentioned
        if bot_mentioned:
            return True
        
        # Only respond to direct questions (with question marks)
        if "?" in message.content:
            return True
        
        # Don't respond to anything else - just track silently
        return False
