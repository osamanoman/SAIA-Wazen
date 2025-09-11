"""
SAIA AI Assistant Mixins

This module provides mixins for all AI assistants in the system,
reducing code duplication and ensuring consistent configuration.
"""

import os
from langchain_openai import ChatOpenAI


class SAIAAIAssistantMixin:
    """
    Mixin for all SAIA AI assistants.
    Provides common configuration and functionality.
    """

    # Common AI model configuration
    model = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
    temperature = 0.3  # Lower temperature for more consistent responses
    tool_max_concurrency = 1  # Prevent parallel tool execution

    # Circuit breaker configuration
    max_tool_calls_per_message = 3  # Limit tool calls to prevent infinite loops

    @property
    def username(self):
        """Get username for logging purposes."""
        return self._user.username if self._user else "Unknown User"

    def get_llm(self):
        """Get the LLM instance configured for Together AI."""
        model = self.get_model()
        temperature = self.get_temperature()
        model_kwargs = self.get_model_kwargs()

        # Configure Together AI
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            model_kwargs=model_kwargs,
            api_key=os.getenv('TOGETHER_API_KEY'),
            base_url=os.getenv('TOGETHER_BASE_URL', 'https://api.together.xyz/v1'),
            max_retries=2,
        )


    def invoke(self, *args, **kwargs):
        """Override invoke to add recursion limit and circuit breaker configuration"""
        config = kwargs.pop("config", {})
        config["recursion_limit"] = config.get("recursion_limit", 100)  # Higher recursion limit for complex assistants

        # Add circuit breaker to prevent infinite tool loops
        config["max_tool_calls"] = config.get("max_tool_calls", self.max_tool_calls_per_message)

        kwargs["config"] = config
        return super().invoke(*args, **kwargs)
