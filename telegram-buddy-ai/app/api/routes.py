from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
import uuid

from ..models.message import Message, ActionItem
from ..models.context import QueryRequest, QueryResponse, ConversationContext
from ..agents.buddy_agent import BuddyAgent
from ..services.context_manager import ContextManager

router = APIRouter()
buddy_agent = None
context_manager = ContextManager()

def get_buddy_agent():
    global buddy_agent
    if buddy_agent is None:
        buddy_agent = BuddyAgent()
    return buddy_agent

@router.post("/message")
async def submit_message(content: str, project_id: str = "default"):
    """Submit a new message for processing"""
    message = Message(
        content=content,
        timestamp=datetime.now(),
        message_id=str(uuid.uuid4())
    )
    
    # Add to context
    context_manager.add_message(message, project_id)
    
    # Extract action items
    action_items = get_buddy_agent().extract_action_items([message])
    if action_items:
        context_manager.add_action_items(action_items, project_id)
    
    return {
        "message_id": message.message_id,
        "processed": True,
        "action_items_found": len(action_items)
    }

@router.get("/context/{project_id}")
async def get_context(project_id: str) -> ConversationContext:
    """Get conversation context for project"""
    return context_manager.get_context(project_id)

@router.get("/actions/{project_id}")
async def get_actions(project_id: str) -> List[ActionItem]:
    """Get unresolved action items for project"""
    return context_manager.get_unresolved_actions(project_id)

@router.post("/query")
async def query_buddy(query: QueryRequest) -> QueryResponse:
    """Ask the buddy agent a question"""
    context = context_manager.get_context(query.project_id)
    response = get_buddy_agent().answer_question(query, context.messages)
    return response

@router.get("/projects")
async def list_projects() -> List[str]:
    """List all projects"""
    projects = context_manager.list_projects()
    return projects if projects else ["default"]
