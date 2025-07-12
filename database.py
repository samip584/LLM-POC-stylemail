"""
Database models and configuration for StyleMail nudge system.
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://stylemail:stylemail123@localhost:5432/stylemail_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Employee(Base):
    """Employee information"""
    __tablename__ = "employees"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    department = Column(String)
    position = Column(String)
    manager_id = Column(String, ForeignKey("employees.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    nudges = relationship("Nudge", back_populates="employee")
    summaries = relationship("NudgeSummary", back_populates="employee")
    emails = relationship("NudgeEmail", back_populates="employee")


class Nudge(Base):
    """Individual nudge records for employees"""
    __tablename__ = "nudges"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)
    nudge_type = Column(String, nullable=False)  # performance, attendance, peer_review, etc.
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    instructions = Column(Text)
    
    # Metrics
    metric_name = Column(String)  # e.g., "attendance_rate", "performance_score"
    metric_value = Column(Float)
    threshold = Column(Float)
    operator = Column(String)  # e.g., "less_than", "greater_than"
    unit = Column(String)  # e.g., "%", "hours", "count"
    
    # Date ranges
    date_range_from = Column(DateTime)
    date_range_to = Column(DateTime)
    prior_date_range_from = Column(DateTime)
    prior_date_range_to = Column(DateTime)
    
    # Additional context
    extra_metadata = Column(Text)  # JSON string for extra data
    status = Column(String, default="active")  # active, resolved, dismissed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", back_populates="nudges")


class AttendanceRecord(Base):
    """Track employee attendance with timestamps"""
    __tablename__ = "attendance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    clock_in = Column(DateTime)
    clock_out = Column(DateTime)
    status = Column(String)  # on_time, late, early, absent
    minutes_late = Column(Integer, default=0)
    minutes_early = Column(Integer, default=0)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class NudgeSummary(Base):
    """Generated summaries for employee nudges"""
    __tablename__ = "nudge_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)
    summary = Column(Text, nullable=False)
    nudge_snippet = Column(Text)  # Quick reference to which nudges were summarized
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", back_populates="summaries")


class NudgeEmail(Base):
    """Generated emails for employee nudges"""
    __tablename__ = "nudge_emails"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    nudge_snippet = Column(Text)  # Quick reference to which nudges were included
    sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", back_populates="emails")


def init_db():
    """Initialize the database - create all tables"""
    Base.metadata.create_all(bind=engine)
    print("[database] Database tables created successfully")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
