"""
Retry logic with exponential backoff.

Handles retrying failed LLM calls and operations with configurable backoff.
"""

import asyncio
import random
from typing import Callable, TypeVar, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class RetryConfig:
    """Retry configuration."""
    max_retries: int = 3
    initial_wait: float = 1.0  # seconds
    backoff_factor: float = 2.0
    max_wait: float = 60.0
    jitter: bool = True


class RetryableOperation:
    """Manages retry logic for operations."""

    def __init__(self, config: RetryConfig):
        """
        Initialize retry manager.

        Args:
            config: Retry configuration
        """
        self.config = config

    async def execute(
        self,
        operation: Callable[..., Any],
        *args,
        **kwargs
    ) -> Any:
        """
        Execute operation with retry logic.

        Args:
            operation: Async function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Operation result

        Raises:
            Exception: If all retries exhausted
        """
        attempt = 0
        last_error = None
        
        while attempt <= self.config.max_retries:
            try:
                logger.debug(f"Executing operation (attempt {attempt + 1})")
                result = await operation(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"Operation succeeded after {attempt} retry/retries")
                
                return result
                
            except Exception as e:
                last_error = e
                attempt += 1
                
                if attempt <= self.config.max_retries:
                    wait_time = self._calculate_wait_time(attempt - 1)
                    logger.warning(
                        f"Operation failed (attempt {attempt}): {str(e)}. "
                        f"Retrying in {wait_time:.2f}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(
                        f"Operation failed after {self.config.max_retries} retries: {str(e)}"
                    )
        
        raise last_error

    def _calculate_wait_time(self, retry_count: int) -> float:
        """
        Calculate wait time for retry with exponential backoff.

        Args:
            retry_count: Number of retries so far (0-indexed)

        Returns:
            Wait time in seconds
        """
        wait_time = self.config.initial_wait * (
            self.config.backoff_factor ** retry_count
        )
        
        # Cap at max wait
        wait_time = min(wait_time, self.config.max_wait)
        
        # Add jitter if enabled
        if self.config.jitter:
            jitter = random.uniform(0, wait_time * 0.1)
            wait_time += jitter
        
        return wait_time

    @staticmethod
    def execute_sync(
        operation: Callable[..., T],
        config: Optional[RetryConfig] = None,
        *args,
        **kwargs
    ) -> T:
        """
        Execute operation synchronously with retry logic.

        Args:
            operation: Function to execute
            config: Retry configuration (uses default if not provided)
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Operation result
        """
        if config is None:
            config = RetryConfig()
        
        attempt = 0
        last_error = None
        
        while attempt <= config.max_retries:
            try:
                logger.debug(f"Executing operation (attempt {attempt + 1})")
                result = operation(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"Operation succeeded after {attempt} retry/retries")
                
                return result
                
            except Exception as e:
                last_error = e
                attempt += 1
                
                if attempt <= config.max_retries:
                    wait_time = RetryableOperation(config)._calculate_wait_time(
                        attempt - 1
                    )
                    logger.warning(
                        f"Operation failed (attempt {attempt}): {str(e)}. "
                        f"Retrying in {wait_time:.2f}s..."
                    )
                    asyncio.sleep(wait_time)
                else:
                    logger.error(
                        f"Operation failed after {config.max_retries} retries: {str(e)}"
                    )
        
        raise last_error


class CircuitBreaker:
    """Circuit breaker pattern for failing services."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Failures before opening circuit
            recovery_timeout: Time before attempting recovery
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        self.failures = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half_open

    async def execute(
        self,
        operation: Callable[..., Any],
        *args,
        **kwargs
    ) -> Any:
        """
        Execute operation with circuit breaker protection.

        Args:
            operation: Async function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Operation result

        Raises:
            Exception: If circuit is open or operation fails
        """
        if self.state == "open":
            if self._should_attempt_recovery():
                self.state = "half_open"
                logger.info("Circuit breaker entering half_open state")
            else:
                raise Exception("Circuit breaker is open")
        
        try:
            result = await operation(*args, **kwargs)
            
            if self.state == "half_open":
                self.state = "closed"
                self.failures = 0
                logger.info("Circuit breaker reset to closed")
            
            return result
            
        except Exception as e:
            self.failures += 1
            self.last_failure_time = asyncio.get_event_loop().time()
            
            if self.failures >= self.failure_threshold:
                self.state = "open"
                logger.error(f"Circuit breaker opened after {self.failures} failures")
            
            raise

    def _should_attempt_recovery(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self.last_failure_time is None:
            return False
        
        import time
        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.recovery_timeout

    def reset(self) -> None:
        """Reset circuit breaker."""
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"
        logger.info("Circuit breaker reset")
