from sqlalchemy.orm import Session
from . import models, schemas


def get_notification(db: Session, user_id: int):
    return db.query(models.Notification).filter(models.Notification.id == user_id).first()


def create_notification(db: Session, notification: schemas.NotificationCreate):
    db_notification = models.Notification(**notification.model_dump())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


def update_notification(db: Session, user_id: int, notification: schemas.NotificationUpdate):
    db_notification = db.query(models.Notification).filter(models.Notification.id == user_id).first()
    if db_notification:
        for key, value in notification.model_dump(exclude_unset=True).items():
            setattr(db_notification, key, value)
        db.commit()
        db.refresh(db_notification)
    return db_notification


def delete_notification(db: Session, user_id: int):
    db_notification = db.query(models.Notification).filter(models.Notification.id == user_id).first()
    if db_notification:
        db.delete(db_notification)
        db.commit()
    return db_notification
      
            

