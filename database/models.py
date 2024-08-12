from sqlalchemy import Boolean, Column, Integer, String
from .database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    notifications_are_active = Column(Boolean, unique=False, default=False)
    selected_crypto = Column(String)
    selected_time = Column(Integer)
    timezone = Column(String)
