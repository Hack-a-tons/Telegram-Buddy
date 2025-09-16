# app/services/context_manager.py
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

from ..models.message import Message
from ..models.context import ConversationContext

logger = logging.getLogger(__name__)

class ActionItem:
    """Simple action item class"""
    def __init__(self, description: str, mentioned_at: datetime, assigned_to: Optional[str] = None):
        self.description = description
        self.mentioned_at = mentioned_at
        self.assigned_to = assigned_to
        self.status = "unresolved"

class ContextManager:
    def __init__(self):
        self.contexts: Dict[str, ConversationContext] = {}
        self.action_items: Dict[str, List[ActionItem]] = {}
    
    def add_message(self, message: Message, projects: Optional[List] = None):
        """Add a message to the context for a channel"""
        channel_id = message.channel_id
        
        if channel_id not in self.contexts:
            self.contexts[channel_id] = ConversationContext(
                channel_id=channel_id,
                messages=[],
                project_id="default",  # Add default project_id
                last_updated=datetime.now()  # Add current timestamp
            )
        
        # Add message to context
        self.contexts[channel_id].messages.append(message)
        
        # Limit context size (keep last 100 messages)
        if len(self.contexts[channel_id].messages) > 100:
            self.contexts[channel_id].messages = self.contexts[channel_id].messages[-100:]
        
        # Detect action items
        self._detect_action_items(message)
        
        logger.info(f"Added message to context for channel {channel_id}")
    
    def get_context(self, channel_id: str, lookback_hours: int = 24) -> ConversationContext:
        """Get conversation context for a channel"""
        if channel_id not in self.contexts:
            self.contexts[channel_id] = ConversationContext(
                channel_id=channel_id,
                messages=[],
                project_id="default",  # Add default project_id
                last_updated=datetime.now()  # Add current timestamp
            )
        
        context = self.contexts[channel_id]
        
        # Filter messages by lookback period if specified
        if lookback_hours > 0:
            cutoff_time = datetime.now() - timedelta(hours=lookback_hours)
            recent_messages = [
                msg for msg in context.messages 
                if msg.timestamp > cutoff_time
            ]
            # Create a filtered context object
            filtered_context = ConversationContext(
                channel_id=channel_id,
                messages=recent_messages,
                project_id="default",  # Add default project_id
                last_updated=datetime.now()  # Add current timestamp
            )
            return filtered_context
        
        return context
    
    def get_unresolved_items(self, channel_id: str) -> List[ActionItem]:
        """Get unresolved action items for a channel"""
        return self.action_items.get(channel_id, [])
    
    def _detect_action_items(self, message: Message):
        """Simple action item detection"""
        content = message.content.lower()
        
        # Keywords that suggest action items
        action_keywords = [
            'need to', 'should', 'must', 'todo', 'task', 'action',
            'deadline', 'by tomorrow', 'by friday', 'urgent', 'asap',
            'please', 'can you', 'could you', 'remember to'
        ]
        
        # Assignment patterns
        assignment_patterns = ['@', 'assigned to', 'responsibility of']
        
        if any(keyword in content for keyword in action_keywords):
            channel_id = message.channel_id
            
            if channel_id not in self.action_items:
                self.action_items[channel_id] = []
            
            # Extract assigned person if mentioned
            assigned_to = None
            if '@' in message.content:
                # Simple extraction - you could make this more sophisticated
                words = message.content.split()
                for word in words:
                    if word.startswith('@'):
                        assigned_to = word[1:]  # Remove @ symbol
                        break
            
            action_item = ActionItem(
                description=message.content,
                mentioned_at=message.timestamp,
                assigned_to=assigned_to
            )
            
            self.action_items[channel_id].append(action_item)
            
            # Limit action items (keep last 50)
            if len(self.action_items[channel_id]) > 50:
                self.action_items[channel_id] = self.action_items[channel_id][-50:]
            
            logger.info(f"Detected action item in channel {channel_id}: {message.content[:50]}...")
    
    def mark_action_resolved(self, channel_id: str, action_index: int):
        """Mark an action item as resolved"""
        if channel_id in self.action_items and 0 <= action_index < len(self.action_items[channel_id]):
            self.action_items[channel_id][action_index].status = "resolved"
            logger.info(f"Marked action {action_index} as resolved in channel {channel_id}")
    
    def get_recent_messages(self, channel_id: str, count: int = 10) -> List[Message]:
        """Get recent messages from a channel"""
        context = self.get_context(channel_id)
        return context.messages[-count:] if context.messages else []