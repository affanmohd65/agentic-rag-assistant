"""
Database models for semantic memory, conversation history, and metadata.
Uses PostgreSQL with SQLAlchemy ORM.
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, JSON, Boolean, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ConversationSession(Base):
    """Store conversation sessions for semantic memory."""
    __tablename__ = "conversation_sessions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    summary = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    messages = relationship("Message", back_populates="session")
    
    __table_args__ = (Index("idx_user_id", "user_id"),)


class Message(Base):
    """Store individual messages in a conversation."""
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("conversation_sessions.id"))
    role = Column(String)  # user, assistant
    content = Column(Text)
    embedding = Column(JSON, nullable=True)  # Store embedding vector
    tokens = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("ConversationSession", back_populates="messages")
    
    __table_args__ = (Index("idx_session_id", "session_id"),)


class SemanticMemory(Base):
    """Store semantic facts and relationships for knowledge base."""
    __tablename__ = "semantic_memory"
    
    id = Column(String, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(Text)
    embedding = Column(JSON, nullable=True)
    entity_type = Column(String)  # person, place, concept, etc.
    relationships = Column(JSON)  # Related entities
    confidence = Column(Float, default=1.0)
    source = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_key", "key"),
        Index("idx_entity_type", "entity_type"),
    )


class DocumentMetadata(Base):
    """Store document metadata for tracking and analytics."""
    __tablename__ = "document_metadata"
    
    id = Column(String, primary_key=True)
    filename = Column(String)
    file_path = Column(String)
    file_size = Column(Integer)
    content_hash = Column(String, unique=True)
    chunks_count = Column(Integer)
    indexed_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)
    
    __table_args__ = (Index("idx_filename", "filename"),)


class QueryCache(Base):
    """Cache for frequently asked queries to improve latency."""
    __tablename__ = "query_cache"
    
    id = Column(String, primary_key=True)
    query = Column(Text, unique=True)
    query_embedding = Column(JSON)
    response = Column(Text)
    reasoning_trace = Column(JSON)
    model_used = Column(String)
    tokens_used = Column(Integer)
    latency_ms = Column(Float)
    hit_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (Index("idx_query", "query"),)


class EvaluationScore(Base):
    """Store RAGAS evaluation scores for RAG pipeline quality."""
    __tablename__ = "evaluation_scores"
    
    id = Column(String, primary_key=True)
    query = Column(Text)
    response = Column(Text)
    retrieved_contexts = Column(JSON)
    
    # RAGAS Metrics
    faithfulness = Column(Float)
    answer_relevancy = Column(Float)
    context_recall = Column(Float)
    context_precision = Column(Float)
    
    # Additional Metrics
    latency_ms = Column(Float)
    model_used = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (Index("idx_timestamp", "timestamp"),)


# Create all tables
def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for FastAPI to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
