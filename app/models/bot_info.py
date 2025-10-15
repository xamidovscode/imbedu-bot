from sqlalchemy import Column, Integer, String
from app.core.db import Base

class BotInfo(Base):
    __tablename__ = "bot_tokens"

    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, nullable=False)
