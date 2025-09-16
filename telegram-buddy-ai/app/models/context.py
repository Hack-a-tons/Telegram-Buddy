from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime
from .message import Message, ActionItem

class ConversationContext(BaseModel):
    project_id: str
    messages: List[Message] = []
    action_items: List[ActionItem] = []
    last_updated: datetime
    summary: str = ""

class QueryRequest(BaseModel):
    question: str
    project_id: str = "default"

class QueryResponse(BaseModel):
    answer: str
    context_used: List[str] = []
    confidence: float = 0.0
