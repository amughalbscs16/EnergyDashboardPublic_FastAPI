"""
GPT-5 Nano Integration Service
Provides AI agent support with usage tracking
"""

import os
import openai
from typing import Dict, Any, List, Optional
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path to import usage tracker
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from usage_tracker import usage_tracker

class GPTService:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize GPT Service

        Args:
            api_key: OpenAI API key. If not provided, will look for OPENAI_API_KEY env var
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY env var or pass api_key parameter.")

        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)

        # GPT-5 nano pricing (estimated - adjust based on actual pricing)
        self.pricing = {
            "input_tokens": 0.000001,  # $1 per 1M input tokens
            "output_tokens": 0.000002  # $2 per 1M output tokens
        }

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate the cost of a request based on token usage"""
        input_cost = input_tokens * self.pricing["input_tokens"]
        output_cost = output_tokens * self.pricing["output_tokens"]
        return input_cost + output_cost

    async def chat_completion(self,
                            messages: List[Dict[str, str]],
                            model: str = "gpt-4o-mini",  # Using available model as placeholder
                            temperature: float = 0.7,
                            max_tokens: Optional[int] = None,
                            request_type: str = "chat_completion",
                            metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a chat completion request with usage tracking

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (will be gpt-5-nano when available)
            temperature: Response randomness (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            request_type: Type of request for tracking purposes
            metadata: Additional metadata to track

        Returns:
            Dictionary containing response and usage info
        """
        try:
            # Make the API call
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Extract usage information
            usage = response.usage
            input_tokens = usage.prompt_tokens
            output_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens

            # Calculate cost
            cost = self._calculate_cost(input_tokens, output_tokens)

            # Track usage
            tracking_metadata = {
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                **(metadata or {})
            }

            usage_stats = usage_tracker.track_usage(
                request_type=request_type,
                tokens_used=total_tokens,
                cost=cost,
                model=model,
                metadata=tracking_metadata
            )

            return {
                "response": response.choices[0].message.content,
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                    "cost": cost
                },
                "tracking": usage_stats,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            # Track failed requests too
            usage_tracker.track_usage(
                request_type=f"{request_type}_failed",
                tokens_used=0,
                cost=0,
                model=model,
                metadata={"error": str(e), **(metadata or {})}
            )
            raise e

    async def agent_support(self,
                          user_input: str,
                          context: Optional[Dict[str, Any]] = None,
                          agent_type: str = "general") -> Dict[str, Any]:
        """
        Provide agent support for user input with domain context

        Args:
            user_input: User's input or question
            context: Additional context (ERCOT data, weather, cohorts, etc.)
            agent_type: Type of agent support requested

        Returns:
            AI response with suggestions and analysis
        """

        # Build context-aware prompt
        system_prompt = self._build_system_prompt(agent_type, context)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]

        return await self.chat_completion(
            messages=messages,
            temperature=0.3,  # Lower temperature for more focused responses
            request_type=f"agent_support_{agent_type}",
            metadata={
                "agent_type": agent_type,
                "has_context": context is not None,
                "context_keys": list(context.keys()) if context else []
            }
        )

    def _build_system_prompt(self, agent_type: str, context: Optional[Dict[str, Any]]) -> str:
        """Build system prompt based on agent type and available context"""

        base_prompt = """You are an AI assistant for a Utility Human-in-the-Loop (HITL) Portal for demand response coordination in the Texas electrical grid. You help utility operators make informed decisions about load management and grid stability."""

        context_info = ""
        if context:
            context_info = "\\n\\nAvailable context data:\\n"
            if "ercot_data" in context:
                context_info += f"- ERCOT Grid Data: {len(context['ercot_data'])} data points available\\n"
            if "weather_data" in context:
                context_info += f"- Weather Data: {len(context['weather_data'])} forecasts available\\n"
            if "cohorts" in context:
                context_info += f"- Customer Cohorts: {len(context['cohorts'])} cohorts available\\n"
            if "dr_plans" in context:
                context_info += f"- DR Plans: {len(context['dr_plans'])} plans available\\n"

        agent_prompts = {
            "general": "Provide helpful analysis and recommendations for grid management decisions.",
            "planning": "Focus on demand response planning, optimization strategies, and resource allocation.",
            "analysis": "Provide detailed technical analysis of grid conditions, load patterns, and risk assessment.",
            "emergency": "Assist with emergency response procedures, load shedding decisions, and crisis management."
        }

        specific_prompt = agent_prompts.get(agent_type, agent_prompts["general"])

        return f"{base_prompt}\\n\\n{specific_prompt}{context_info}\\n\\nProvide concise, actionable recommendations based on the available data."

# Global service instance (will be initialized with API key)
gpt_service = None

def initialize_gpt_service(api_key: str):
    """Initialize the global GPT service with API key"""
    global gpt_service
    gpt_service = GPTService(api_key)
    return gpt_service

def get_gpt_service() -> Optional[GPTService]:
    """Get the global GPT service instance"""
    return gpt_service