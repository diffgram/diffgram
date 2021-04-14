# OPENCORE - ADD
from shared.database.common import *


class NotificationUser(Base):
    """
        
    """

    __tablename__ = 'notification_user'

    notification_id = Column(Integer, ForeignKey('notification.id'), primary_key=True)
    notification = relationship("Notification", foreign_keys=[notification_id])

    user_id = Column(Integer, ForeignKey('userbase.id'), primary_key=True)
    user = relationship("User",  foreign_keys=[user_id])

    is_read = Column(Boolean, default=False)

    time_created = Column(DateTime, default=None, nullable=True)

    @staticmethod
    def new(session=None,
            add_to_session=False,
            flush_session=False,
            notification_id=None,
            user_id=None,
            is_read=False):

        notification = NotificationUser(
            notification_id=notification_id,
            user_id=user_id,
            is_read=is_read)
        if add_to_session:
            session.add(notification)
        if flush_session:
            session.flush()
        return notification

    @staticmethod
    def get_by_id(session, notification_id=None, user_id=None):
        return session.query(NotificationUser).filter(
            NotificationUser.notification_id == notification_id,
            NotificationUser.user_id == user_id
        ).first()

