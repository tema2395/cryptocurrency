from pydantic import BaseModel


class NotificationBase(BaseModel):
    notifications_are_active: bool = False
    selected_crypto: str = ""
    selected_time: int = 0
    timezone: str = ""


class NotificationCreate(NotificationBase):
    id: int


class NotificationUpdate(NotificationBase):
    pass


class Notification(NotificationBase):
    id: int

    class Config:
        from_attributes = True
