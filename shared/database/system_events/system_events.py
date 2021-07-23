# OPENCORE - ADD
from shared.database.common import *
from shared.shared_logger import get_shared_logger
logger = get_shared_logger()


class SystemEvents(Base):
    """
        SyncActionsQueue will keep all pending sync actions for be peformed. For example
        task creations, file copies, file moves, etc...
    """
    __tablename__ = 'system_events'
    id = Column(BIGINT, primary_key=True)

    kind = Column(String)

    description = Column(String())

    install_fingerprint = Column(String)

    previous_version = Column(String)

    diffgram_version = Column(String)

    host_os = Column(String)

    storage_backend = Column(String)

    service_name = Column(String)

    startup_time = Column(DateTime, default=None, nullable = True)

    shut_down_time = Column(DateTime, default=None, nullable = True)

    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    @staticmethod
    def system_startup_events_check(session, service_name):
        """
            Checks multiple system settings changes and logs them if any changes detected.
        :param session:
        :return:
        """
        # Record Startup Time



    @staticmethod
    def check_version_upgrade(session):
        """
            Checks the current version in the system and generates an event
            if version has changed.
        :param session:
        :return:
        """
        raise NotImplementedError

    @staticmethod
    def check_os_change(session):
        """
            Checks the current version in the system and generates an event
            if version has changed.
        :param session:
        :return:
        """
        raise NotImplementedError

    @staticmethod
    def new(session,
            kind=None,
            description=None,
            install_fingerprint=None,
            previous_version=None,
            diffgram_version=None,
            host_os=None,
            storage_backend=None,
            service_name=None,
            startup_time=None,
            shut_down_time=None,
            created_date=None):

        raise NotImplementedError