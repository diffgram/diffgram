# OPENCORE - ADD
from shared.database.common import *
from shared.shared_logger import get_shared_logger
logger = get_shared_logger()


class SyncActionsQueue(Base):
    """
        SyncActionsQueue will keep all pending sync actions for be peformed. For example
        task creations, file copies, file moves, etc...
    """
    __tablename__ = 'sync_actions_queue'
    id = Column(BIGINT, primary_key=True)

    sync_event_id = Column(Integer, ForeignKey('sync_event.id'))
    sync_event = relationship("SyncEvent", foreign_keys=[sync_event_id])

    @staticmethod
    def enqueue(session, sync_event):
        logger.info(f"Sending sync event to queue - ID: {sync_event.id}")
        elm = SyncActionsQueue(sync_event=sync_event)
        session.add(elm)
        return elm
