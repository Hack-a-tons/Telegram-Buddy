from typing import Dict, List
from datetime import datetime
from ..models.message import Message, ActionItem
from ..models.context import ConversationContext

class ContextManager:
    def __init__(self):
        self.contexts: Dict[str, ConversationContext] = {}
    
    def add_message(self, message: Message, project_id: str = "default"):
        """Add message to project context"""
        if project_id not in self.contexts:
            self.contexts[project_id] = ConversationContext(
                project_id=project_id,
                last_updated=datetime.now()
            )
        
        context = self.contexts[project_id]
        context.messages.append(message)
        context.last_updated = datetime.now()
        
        # Keep only last 50 messages for memory efficiency
        if len(context.messages) > 50:
            context.messages = context.messages[-50:]
    
    def get_context(self, project_id: str = "default") -> ConversationContext:
        """Get conversation context for project"""
        if project_id not in self.contexts:
            return ConversationContext(
                project_id=project_id,
                last_updated=datetime.now()
            )
        return self.contexts[project_id]
    
    def add_action_items(self, action_items: List[ActionItem], project_id: str = "default"):
        """Add action items to project context"""
        if project_id not in self.contexts:
            self.contexts[project_id] = ConversationContext(
                project_id=project_id,
                last_updated=datetime.now()
            )
        
        context = self.contexts[project_id]
        context.action_items.extend(action_items)
        context.last_updated = datetime.now()
    
    def get_unresolved_actions(self, project_id: str = "default") -> List[ActionItem]:
        """Get unresolved action items"""
        context = self.get_context(project_id)
        return [item for item in context.action_items if item.status == "unresolved"]
    
    def list_projects(self) -> List[str]:
        """List all project IDs"""
        return list(self.contexts.keys())
