from sqlalchemy import Column, String, DateTime, SmallInteger, Integer, Enum
from app.core.database import Base
import enum


class TokenEnum(str, enum.Enum):
    refresh = "refresh"
    access = "access"


class UserAuthToken(Base):
    __tablename__ = "users_auth_token"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, index=True)
    type = Column(Enum(TokenEnum), nullable=False)
    status = Column(SmallInteger, default=1)
    user_id = Column(Integer, nullable=False)
    expires_at = Column(DateTime)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
