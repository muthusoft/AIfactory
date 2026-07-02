"""
LiteLLM wrapper providing unified LLM access across multiple providers.

This module abstracts all LLM interactions through LiteLLM, allowing seamless
switching between OpenAI, Anthropic, Google, Ollama, and other providers.
"""

import os
import json
import time
from typing import Optional, Any
from dataclasses import dataclass
from datetime import datetime
import litellm
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """LLM configuration."""
    provider: str
    api_key: Optional[str]
    model: str
    temperature: float = 0.7
    max_tokens: int = 4000
    top_p: float = 1.0


@dataclass
class LLMCallResult:
    """Result of an LLM call."""
    content: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    latency: float
    cost: float
    timestamp: datetime
    retry_count: int = 0


class LLMProvider:
    """Unified LLM provider using LiteLLM."""

    def __init__(self, config: LLMConfig, max_retries: int = 3):
        """
        Initialize the LLM provider.

        Args:
            config: LLM configuration
            max_retries: Maximum number of retries for failed requests
        """
        self.config = config
        self.max_retries = max_retries
        
        # Set API key if provided
        if config.api_key:
            self._set_api_key(config.provider, config.api_key)
        
        # Set LiteLLM parameters
        litellm.temperature = config.temperature
        litellm.max_tokens = config.max_tokens
        
        logger.info(
            f"LLM Provider initialized: provider={config.provider}, "
            f"model={config.model}"
        )

    def _set_api_key(self, provider: str, api_key: str) -> None:
        """Set API key for the provider."""
        key_map = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'gemini': 'GOOGLE_API_KEY',
            'openrouter': 'OPENROUTER_API_KEY',
        }
        
        env_key = key_map.get(provider, f'{provider.upper()}_API_KEY')
        os.environ[env_key] = api_key

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=60)
    )
    async def call(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMCallResult:
        """
        Call the LLM with the given prompt.

        Args:
            prompt: User prompt
            system_prompt: System prompt
            temperature: Temperature override
            max_tokens: Max tokens override
            **kwargs: Additional parameters

        Returns:
            LLMCallResult with response and metadata
        """
        start_time = time.time()
        retry_count = kwargs.pop('retry_count', 0)
        
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Add user prompt
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        try:
            # Build model identifier
            model = self._get_model_identifier()
            
            # Call LiteLLM
            response = await litellm.acompletion(
                model=model,
                messages=messages,
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens,
                top_p=self.config.top_p,
                **kwargs
            )
            
            # Extract response
            content = response.choices[0].message.content
            
            # Calculate tokens and cost
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            cost = self._calculate_cost(input_tokens, output_tokens)
            
            latency = time.time() - start_time
            
            result = LLMCallResult(
                content=content,
                model=self.config.model,
                provider=self.config.provider,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency=latency,
                cost=cost,
                timestamp=datetime.now(),
                retry_count=retry_count
            )
            
            logger.info(
                f"LLM call succeeded: model={self.config.model}, "
                f"tokens={input_tokens+output_tokens}, "
                f"latency={latency:.2f}s"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            if retry_count < self.max_retries:
                logger.info(f"Retrying LLM call (attempt {retry_count + 1})")
                kwargs['retry_count'] = retry_count + 1
                await time.sleep(2 ** retry_count)  # Exponential backoff
                return await self.call(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
            raise

    def _get_model_identifier(self) -> str:
        """Get the full model identifier for LiteLLM."""
        if self.config.provider in ['openai']:
            return self.config.model
        elif self.config.provider in ['anthropic']:
            return f"claude-{self.config.model}"
        elif self.config.provider in ['gemini']:
            return f"gemini/{self.config.model}"
        elif self.config.provider in ['ollama']:
            return f"ollama/{self.config.model}"
        else:
            return f"{self.config.provider}/{self.config.model}"

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate estimated cost of the LLM call."""
        # This would be expanded with actual pricing per model
        # Placeholder implementation
        return 0.0

    def __repr__(self) -> str:
        return (
            f"LLMProvider(provider={self.config.provider}, "
            f"model={self.config.model})"
        )
