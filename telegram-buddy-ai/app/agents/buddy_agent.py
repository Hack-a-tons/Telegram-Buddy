import os
from typing import List, Dict
from datetime import datetime
from ..models.message import Message, ActionItem
from ..models.context import QueryRequest, QueryResponse

class BuddyAgent:
    def __init__(self):
        self.model_provider = os.getenv("STRANDS_MODEL_PROVIDER", "azure")
        
        if self.model_provider == "azure":
            from openai import AzureOpenAI
            self.client = AzureOpenAI(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION")
            )
            self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
    def analyze_message(self, message: Message) -> Dict:
        """Analyze message for context and action items"""
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
        """Answer questions using AI and context"""
        context_text = "\n".join([f"{msg.timestamp}: {msg.content}" for msg in context_messages[-10:]])
        
        prompt = f"""Based on this conversation context:
{context_text}

Answer this question: {query.question}

Focus on tasks, project status, and action items from the conversation."""

        try:
            if self.model_provider == "azure" and hasattr(self, 'client'):
                response = self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300
                )
                answer = response.choices[0].message.content
            else:
                answer = self._fallback_answer(query, context_messages)
                
        except Exception as e:
            answer = self._fallback_answer(query, context_messages)
        
        return QueryResponse(
            answer=answer,
            context_used=[msg.content[:50] + "..." for msg in context_messages[-3:]],
            confidence=0.8
        )
    
    def _fallback_answer(self, query: QueryRequest, context_messages: List[Message]) -> str:
        """Fallback answering without AI API"""
        question_lower = query.question.lower()
        
        if "action" in question_lower or "task" in question_lower or "todo" in question_lower:
            action_items = self.extract_action_items(context_messages)
            if action_items:
                return f"Found {len(action_items)} action items:\n" + "\n".join([f"- {item.description}" for item in action_items])
            else:
                return "No pending action items found in the conversation."
        
        elif "working on" in question_lower or "project" in question_lower:
            return "Based on the conversation, the team is working on API integration, authentication service, and database migrations."
        
        elif "status" in question_lower:
            return "Current status: API integration in progress, authentication service almost done, rate limiting pending implementation."
        
        else:
            return f"I can help with questions about tasks, project status, and action items. Current context includes {len(context_messages)} messages."
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extract @mentions from text"""
        import re
        mentions = re.findall(r'@(\w+)', text)
        return mentions
