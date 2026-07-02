"""
Database connection and session management.

Provides SQLAlchemy session factory and connection pooling.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages database connections."""

    _engine = None
    _session_factory = None

    @classmethod
    def initialize(cls, database_url: str, echo: bool = False) -> None:
        """
        Initialize database connection.

        Args:
            database_url: SQLAlchemy database URL
            echo: Whether to echo SQL statements
        """
        # Use StaticPool for SQLite to avoid threading issues
        if "sqlite" in database_url:
            cls._engine = create_engine(
                database_url,
                echo=echo,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool
            )
        else:
            cls._engine = create_engine(
                database_url,
                echo=echo,
                pool_pre_ping=True  # Test connections before using
            )

        cls._session_factory = sessionmaker(bind=cls._engine)
        logger.info(f"Database initialized: {database_url}")

    @classmethod
    def get_session(cls) -> Session:
        """
        Get a database session.

        Returns:
            SQLAlchemy session
        """
        if cls._session_factory is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        return cls._session_factory()

    @classmethod
    def get_engine(cls):
        """Get database engine."""
        if cls._engine is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        return cls._engine

    @classmethod
    def close(cls) -> None:
        """Close database connections."""
        if cls._engine:
            cls._engine.dispose()
            logger.info("Database connections closed")


class SessionLocal:
    """Context manager for database sessions."""

    def __init__(self):
        self.session: Optional[Session] = None

    def __enter__(self) -> Session:
        self.session = DatabaseConnection.get_session()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.session:
            if exc_type is not None:
                self.session.rollback()
            else:
                self.session.commit()
            self.session.close()
