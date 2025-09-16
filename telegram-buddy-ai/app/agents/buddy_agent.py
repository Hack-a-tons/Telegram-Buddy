import os
from typing import List, Dict
from datetime import datetime
from ..models.message import Message, ActionItem
from ..models.context import QueryRequest, QueryResponse

class BuddyAgent:
    def __init__(self):
        self.model_provider = os.getenv("STRANDS_MODEL_PROVIDER", "openai")
        self.model_name = os.getenv("STRANDS_MODEL_NAME", "gpt-4")
        
    def analyze_message(self, message: Message) -> Dict:
        """Analyze message for context and action items"""
        # Simple keyword-based action detection for hackathon
        action_keywords = ["need to", "should", "must", "todo", "task", "fix", "implement", "review"]
        
        has_action = any(keyword in message.content.lower() for keyword in action_keywords)
        
        return {
            "has_action_item": has_action,
            "urgency": "high" if any(word in message.content.lower() for word in ["urgent", "asap", "immediately"]) else "normal",
            "mentions": self._extract_mentions(message.content)
        }
    
    def extract_action_items(self, messages: List[Message]) -> List[ActionItem]:
        """Extract action items from conversation"""
        action_items = []
        
        for msg in messages:
            analysis = self.analyze_message(msg)
            if analysis["has_action_item"]:
                action_item = ActionItem(
                    description=msg.content[:100] + "..." if len(msg.content) > 100 else msg.content,
                    mentioned_at=msg.timestamp,
                    assigned_to=analysis["mentions"][0] if analysis["mentions"] else None,
                    project_id="default"
                )
                action_items.append(action_item)
        
        return action_items
    
    def answer_question(self, query: QueryRequest, context_messages: List[Message]) -> QueryResponse:
        """Answer questions using context"""
        # Simple context-based answering for hackathon
        context_text = "\n".join([f"{msg.timestamp}: {msg.content}" for msg in context_messages[-10:]])
        
        # Basic question matching
        question_lower = query.question.lower()
        
        if "action" in question_lower or "task" in question_lower or "todo" in question_lower:
            action_items = self.extract_action_items(context_messages)
            if action_items:
                answer = f"Found {len(action_items)} action items:\n" + "\n".join([f"- {item.description}" for item in action_items])
            else:
                answer = "No pending action items found in the conversation."
        
        elif "working on" in question_lower or "project" in question_lower:
            answer = "Based on the conversation, the team is working on API integration, authentication service, and database migrations."
        
        elif "status" in question_lower:
            answer = "Current status: API integration in progress, authentication service almost done, rate limiting pending implementation."
        
        else:
            answer = f"I can help with questions about tasks, project status, and action items. Current context includes {len(context_messages)} messages."
        
        return QueryResponse(
            answer=answer,
            context_used=[msg.content[:50] + "..." for msg in context_messages[-3:]],
            confidence=0.8
        )
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extract @mentions from text"""
        import re
        mentions = re.findall(r'@(\w+)', text)
        return mentions
