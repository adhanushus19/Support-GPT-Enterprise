import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from src.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="agent")  # admin, manager, agent
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    approvals = relationship("ResponseApproval", back_populates="agent")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(100), index=True, nullable=False)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="open")  # open, in_progress, resolved
    priority = Column(String(50), nullable=False, default="medium")  # low, medium, high, urgent
    sentiment = Column(String(50), nullable=True)  # positive, neutral, negative
    department = Column(String(100), nullable=True)  # billing, technical, returns, etc.
    sla_hours = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    approvals = relationship("ResponseApproval", back_populates="ticket", cascade="all, delete-orphan")


class SessionMemory(Base):
    __tablename__ = "session_memories"

    session_id = Column(String(100), primary_key=True, index=True)
    customer_id = Column(String(100), index=True, nullable=False)
    conversation_history = Column(JSON, nullable=False, default=list)  # List of message dicts: [{"role": "user", "content": "..."}]
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class KnowledgeDoc(Base):
    __tablename__ = "knowledge_docs"

    id = Column(String(100), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    version = Column(String(50), nullable=False, default="v1")
    category = Column(String(100), nullable=False)
    metadata_json = Column(JSON, nullable=True)  # Extra fields
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ResponseApproval(Base):
    __tablename__ = "response_approvals"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    drafted_response = Column(Text, nullable=False)
    modified_response = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="pending")  # pending, approved, modified, rejected
    agent_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    latency_seconds = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    ticket = relationship("Ticket", back_populates="approvals")
    agent = relationship("User", back_populates="approvals")
