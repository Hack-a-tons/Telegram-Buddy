from ..models.message import Message

class ResponseEngine:
    def __init__(self):
        pass
    
    def should_respond(self, message: Message, bot_mentioned: bool = False) -> bool:
        """Determine if the bot should respond to this message"""
        content = message.content.lower()
        
        # Always respond if bot is mentioned
        if bot_mentioned:
            return True
        
        # Respond to questions
        question_indicators = ['?', 'what', 'how', 'why', 'when', 'where', 'who']
        if any(indicator in content for indicator in question_indicators):
            return True
        
        # Respond to help requests
        help_indicators = ['help', 'stuck', 'problem', 'issue', 'error']
        if any(indicator in content for indicator in help_indicators):
            return True
        
        # Don't respond to everything (avoid spam)
        return False
