from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Optional

class Message(BaseModel):
    content: str
    timestamp: datetime
    source: str = "copy_paste"
    channel_id: str = "default"
    user_id: str = "user"
    message_id: str
    metadata: Dict = {}

class ActionItem(BaseModel):
    description: str
    mentioned_at: datetime
    assigned_to: Optional[str] = None
    status: str = "unresolved"
    project_id: str = "default"

class ProjectTag(BaseModel):
    project_id: str
    project_name: str
    confidence: float
