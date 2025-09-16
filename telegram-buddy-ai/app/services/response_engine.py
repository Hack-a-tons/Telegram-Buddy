# app/services/response_engine.py
import logging
from typing import Optional
from ..models.message import Message

logger = logging.getLogger(__name__)

class ResponseEngine:
    """Determines when and how the bot should respond to messages"""
    
    def __init__(self):
        self.response_threshold = 0.3  # Minimum confidence to respond
    
    def should_respond(self, message: Message, bot_mentioned: bool = False, analysis: Optional[dict] = None) -> bool:
        """
        Determine if the bot should respond to this message
        
        Args:
            message: The incoming message
            bot_mentioned: Whether the bot was explicitly mentioned
            analysis: Optional analysis results from other agents
            
        Returns:
            bool: True if bot should respond, False otherwise
        """
        try:
            content = message.content.lower().strip()
            
            # Always respond if bot is mentioned
            if bot_mentioned:
                logger.info(f"Bot mentioned, will respond to: {content[:50]}...")
                return True
            
            # Don't respond to very short messages
            if len(content) < 3:
                return False
            
            # Respond to direct questions
            question_indicators = ['?', 'what', 'how', 'why', 'when', 'where', 'who', 'which']
            if any(indicator in content for indicator in question_indicators):
                logger.info(f"Question detected, will respond to: {content[:50]}...")
                return True
            
            # Respond to help requests
            help_indicators = [
                'help', 'stuck', 'problem', 'issue', 'error', 'broken',
                'not working', 'failing', 'bug', 'debug'
            ]
            if any(indicator in content for indicator in help_indicators):
                logger.info(f"Help request detected, will respond to: {content[:50]}...")
                return True
            
            # Respond to status requests
            status_indicators = [
                'status', 'progress', 'update', 'what\'s happening',
                'where are we', 'current state'
            ]
            if any(indicator in content for indicator in status_indicators):
                logger.info(f"Status request detected, will respond to: {content[:50]}...")
                return True
            
            # Respond to task/action related messages
            task_indicators = [
                'todo', 'task', 'action', 'need to', 'should we',
                'deadline', 'priority', 'urgent', 'asap'
            ]
            if any(indicator in content for indicator in task_indicators):
                logger.info(f"Task-related message detected, will respond to: {content[:50]}...")
                return True
            
            # Don't respond to greetings, casual chat, or very common words
            ignore_patterns = [
                'hi', 'hello', 'hey', 'morning', 'afternoon', 'evening',
                'thanks', 'thank you', 'ok', 'okay', 'yes', 'no',
                'lol', 'haha', 'cool', 'nice', 'good', 'great'
            ]
            
            # If message is mostly ignored patterns, don't respond
            words = content.split()
            if len(words) <= 3 and any(word in ignore_patterns for word in words):
                return False
            
            # For longer messages, be more selective
            if len(content) > 100:
                # Only respond to longer messages if they seem technical/project-related
                technical_indicators = [
                    'code', 'api', 'database', 'server', 'deploy', 'bug',
                    'feature', 'pull request', 'commit', 'branch', 'merge',
                    'test', 'production', 'staging', 'error', 'exception'
                ]
                if any(indicator in content for indicator in technical_indicators):
                    return True
            
            # Default: don't respond to avoid spam
            logger.debug(f"No response criteria met for: {content[:50]}...")
            return False
            
        except Exception as e:
            logger.error(f"Error determining response: {e}")
            return False
    
    def format_response(self, response: str, target_platform: str = "telegram") -> str:
        """
        Format response for specific platform
        
        Args:
            response: Raw response text
            target_platform: Platform to format for (telegram, discord, slack)
            
        Returns:
            str: Formatted response
        """
        if not response:
            return ""
        
        # Clean up response
        response = response.strip()
        
        if target_platform == "telegram":
            # Telegram-specific formatting
            # Ensure response isn't too long (Telegram has 4096 char limit)
            if len(response) > 4000:
                response = response[:3900] + "... (truncated)"
            
            # Add some emoji for friendliness if it's a direct answer
            if response.startswith("The ") or response.startswith("Yes") or response.startswith("No"):
                response = f"🤖 {response}"
        
        return response
    
    def get_response_context(self, message: Message) -> dict:
        """
        Get context information that might be useful for generating responses
        
        Args:
            message: The message to analyze
            
        Returns:
            dict: Context information
        """
        return {
            "message_length": len(message.content),
            "has_question": "?" in message.content,
            "source": message.source,
            "user_info": message.metadata,
            "timestamp": message.timestamp
        }