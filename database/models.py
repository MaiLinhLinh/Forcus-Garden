from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, default="Student")
    total_trees = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)  # callable - evaluated at insert time
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")

class Session(Base):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    subject = Column(String, nullable=False)
    target_duration_mins = Column(Integer, nullable=False)
    actual_duration_secs = Column(Integer, default=0)  # Thời gian thực học tính bằng GIÂY (chính xác)
    actual_duration_mins = Column(Integer, default=0)  # Giữ lại để tương thích cũ
    status = Column(String, default="in_progress")  # "in_progress", "success", "failed"
    started_at = Column(DateTime, default=datetime.now)  # callable
    ended_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="sessions")
    study_zone = relationship("StudyZone", back_populates="session", uselist=False, cascade="all, delete-orphan")
    distractions = relationship("Distraction", back_populates="session", cascade="all, delete-orphan")

class StudyZone(Base):
    __tablename__ = 'study_zones'
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    allowed_keywords = Column(Text, nullable=False)  # JSON string, e.g. '["chrome", "vscode"]'
    session = relationship("Session", back_populates="study_zone")

class Distraction(Base):
    __tablename__ = 'distractions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    app_name = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)  # callable
    duration_seconds = Column(Integer, default=0)
    session = relationship("Session", back_populates="distractions")
