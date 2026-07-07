from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./gentrace.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True, index=True)
    full_name     = Column(String, nullable=False)
    email         = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow)
    members       = relationship("FamilyMember", back_populates="user", cascade="all, delete")
    predictions   = relationship("PredictionHistory", back_populates="user", cascade="all, delete")


class FamilyMember(Base):
    __tablename__ = "family_members"
    id            = Column(Integer, primary_key=True, index=True)
    user_id       = Column(Integer, ForeignKey("users.id"), nullable=False)
    relation      = Column(String, nullable=False)   # e.g. Father, Mother, PGF …
    gender        = Column(String)
    age           = Column(Integer)
    has_diabetes  = Column(Integer, default=0)
    diabetes_severity = Column(Integer, default=0)   # 0-3
    diabetes_onset    = Column(Integer, default=0)
    has_hypertension  = Column(Integer, default=0)
    has_heart_disease = Column(Integer, default=0)
    heart_severity    = Column(Integer, default=0)
    heart_onset       = Column(Integer, default=0)
    has_hair_loss     = Column(Integer, default=0)
    user              = relationship("User", back_populates="members")


class PredictionHistory(Base):
    __tablename__ = "prediction_history"
    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=False)
    predicted_at    = Column(DateTime, default=datetime.utcnow)
    diabetes_risk   = Column(Float)
    hypertension_risk = Column(Float)
    heart_risk      = Column(Float)
    hair_loss_norwood = Column(Integer)
    onset_diabetes  = Column(Float)
    onset_heart     = Column(Float)
    shap_json       = Column(Text)
    recommendation  = Column(Text)
    user            = relationship("User", back_populates="predictions")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
