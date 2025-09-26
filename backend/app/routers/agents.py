"""
Agent Support Router - REQUIRES OPENAI API KEY

NOTE: This router provides AI assistance endpoints using OpenAI's API.
Requires initialization with a valid OpenAI API key.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from usage_tracker import usage_tracker
from app.services.gpt_service import get_gpt_service

router = APIRouter()

# Request/Response Models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = "gpt-4o-mini"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    request_type: Optional[str] = "chat_completion"

class AgentSupportRequest(BaseModel):
    user_input: str
    context: Optional[Dict[str, Any]] = None
    agent_type: Optional[str] = "general"

class InitializeServiceRequest(BaseModel):
    api_key: str

class UsageStatsResponse(BaseModel):
    total_requests: int
    total_tokens: int
    total_cost: float
    today_usage: Dict[str, Any]
    last_updated: str
    recent_sessions: List[Dict[str, Any]]

@router.post("/initialize", summary="Initialize OpenAI Service")
async def initialize_service(request: InitializeServiceRequest):
    """
    Initialize the OpenAI service with your OpenAI API key
    This must be called before using other agent endpoints
    NOTE: Requires a valid OpenAI API key
    """
    try:
        from app.services.gpt_service import initialize_gpt_service
        service = initialize_gpt_service(request.api_key)

        # Track the initialization
        usage_tracker.track_usage(
            request_type="service_initialization",
            tokens_used=0,
            cost=0,
            model="system",
            metadata={"action": "service_initialized"}
        )

        return {
            "status": "success",
            "message": "GPT service initialized successfully",
            "timestamp": usage_tracker.get_usage_stats()["last_updated"]
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to initialize service: {str(e)}")

@router.post("/chat", summary="Chat Completion")
async def chat_completion(request: ChatRequest):
    """
    Make a chat completion request using OpenAI's API
    Tracks usage automatically
    Requires OpenAI API key to be configured
    """
    service = get_gpt_service()
    if not service:
        raise HTTPException(
            status_code=400,
            detail="OpenAI service not initialized. Call /initialize first with your OpenAI API key."
        )

    try:
        # Convert Pydantic models to dictionaries
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        result = await service.chat_completion(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            request_type=request.request_type
        )

        return {
            "status": "success",
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat completion failed: {str(e)}")

@router.post("/agent-support", summary="Agent Support")
async def agent_support(request: AgentSupportRequest):
    """
    Get AI-powered agent support for grid management decisions
    Provides context-aware recommendations
    """
    service = get_gpt_service()
    if not service:
        raise HTTPException(
            status_code=400,
            detail="OpenAI service not initialized. Call /initialize first with your OpenAI API key."
        )

    try:
        result = await service.agent_support(
            user_input=request.user_input,
            context=request.context,
            agent_type=request.agent_type
        )

        return {
            "status": "success",
            "agent_type": request.agent_type,
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent support failed: {str(e)}")

@router.get("/usage", response_model=UsageStatsResponse, summary="Get Usage Statistics")
async def get_usage_stats():
    """
    Get current GPT usage statistics and cost tracking
    """
    try:
        stats = usage_tracker.get_usage_stats()
        return UsageStatsResponse(**stats)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get usage stats: {str(e)}")

@router.post("/usage/reset", summary="Reset Usage Statistics")
async def reset_usage_stats():
    """
    Reset all usage statistics (use with caution)
    """
    try:
        result = usage_tracker.reset_usage()
        return {
            "status": "success",
            "message": "Usage statistics reset successfully",
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset usage stats: {str(e)}")

@router.get("/health", summary="Agent Service Health Check")
async def health_check():
    """
    Check if the OpenAI agent service is configured and operational
    """
    service = get_gpt_service()
    service_status = "initialized" if service else "not_initialized"

    try:
        stats = usage_tracker.get_usage_stats()
        return {
            "status": "healthy",
            "service_status": service_status,
            "total_requests": stats["total_requests"],
            "last_updated": stats["last_updated"]
        }

    except Exception as e:
        return {
            "status": "degraded",
            "service_status": service_status,
            "error": str(e)
        }