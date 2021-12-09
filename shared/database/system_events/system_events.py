# OPENCORE - ADD
import analytics
import requests
from shared.helpers.sessionMaker import session_scope
from shared.database.common import *
from shared.shared_logger import get_shared_logger
from packaging import version
import traceback

logger = get_shared_logger()


class SystemEvents(Base):
    """
        SyncActionsQueue will keep all pending sync actions for be peformed. For example
        task creations, file copies, file moves, etc...
    """
    __tablename__ = 'system_events'
    id = Column(BIGINT, primary_key = True)

    kind = Column(String)

    description = Column(String())

    install_fingerprint = Column(String)

    previous_version = Column(String)

    diffgram_version = Column(String)

    host_os = Column(String)

    storage_backend = Column(String)

    service_name = Column(String)

    startup_time = Column(DateTime, default = None, nullable = True)

    shut_down_time = Column(DateTime, default = None, nullable = True)

    created_date = Column(DateTime, default = datetime.datetime.utcnow)

    @staticmethod
    def system_startup_events_check(service_name):
        """
            Checks multiple system settings changes and logs them if any changes detected.
        :param session:
        :return:
        """
        if settings.DIFFGRAM_INSTALL_FINGERPRINT is None:
            logger.error(
                'DIFFGRAM_INSTALL_FINGERPRINT is not Set as an ENV variable. \n'
                'Please set it by running install.py script again. Value will be stored in .env file.')
            return False
        if settings.DIFFGRAM_VERSION_TAG is None:
            logger.error(
                'DIFFGRAM_VERSION_TAG is not Set as an ENV variable. \n'
                'Please set it by running install.py script again. Value will be stored in .env file.')
            return False
        if settings.DIFFGRAM_HOST_OS is None:
            logger.error(
                'DIFFGRAM_HOST_OS is not Set as an ENV variable. \n'
                'Please set it by running install.py script again. Value will be stored in .env file.')
            return False

        with session_scope() as session:
            # Record Startup Time
            SystemEvents.new(
                session = session,
                kind = 'system_startup',
                description = 'Diffgram System startup for {} service'.format(service_name),
                install_fingerprint = settings.DIFFGRAM_INSTALL_FINGERPRINT,
                previous_version = None,
                diffgram_version = settings.DIFFGRAM_VERSION_TAG,
                host_os = settings.DIFFGRAM_HOST_OS,
                storage_backend = settings.DIFFGRAM_STATIC_STORAGE_PROVIDER,
                service_name = service_name,
                startup_time = datetime.datetime.utcnow(),
                shut_down_time = None,
                created_date = datetime.datetime.utcnow()
            )
            session.commit()
            SystemEvents.check_version_upgrade(session = session, service_name = service_name)
            SystemEvents.check_os_change(session = session, service_name = service_name)
            return True

    @staticmethod
    def check_version_upgrade(session, service_name):
        """
            Checks the current version in the system and generates an event
            if version has changed.
        :param session:
        :return:
        """
        logger.info('Checking for version upgrades [{}]'.format(service_name))
        latest_recorded_version_event = session.query(SystemEvents).filter(
            SystemEvents.kind == 'version_upgrade'
        ).order_by('created_date').first()

        if latest_recorded_version_event is None:
            # Initial upgrade
            system_event = SystemEvents.new(
                session = session,
                kind = 'version_upgrade',
                description = 'Diffgram System startup for {} service'.format(service_name),
                install_fingerprint = settings.DIFFGRAM_INSTALL_FINGERPRINT,
                previous_version = None,
                diffgram_version = settings.DIFFGRAM_VERSION_TAG,
                host_os = settings.DIFFGRAM_HOST_OS,
                storage_backend = settings.DIFFGRAM_STATIC_STORAGE_PROVIDER,
                service_name = service_name,
                startup_time = datetime.datetime.utcnow(),
                shut_down_time = None,
                created_date = datetime.datetime.utcnow()
            )
            session.commit()
            return system_event

        else:
            # Determine if current version in env variable is greater than last recorded version.
            recorded_version = latest_recorded_version_event.diffgram_version
            version_to_check = settings.DIFFGRAM_VERSION_TAG
            if version.parse(version_to_check) > version.parse(recorded_version):
                logger.info('New version detected: [{}]'.format(version_to_check))
                system_event = SystemEvents.new(
                    session = session,
                    kind = 'version_upgrade',
                    description = 'Diffgram System startup for {} service'.format(service_name),
                    install_fingerprint = settings.DIFFGRAM_INSTALL_FINGERPRINT,
                    previous_version = None,
                    diffgram_version = version_to_check,
                    host_os = settings.DIFFGRAM_HOST_OS,
                    storage_backend = settings.DIFFGRAM_STATIC_STORAGE_PROVIDER,
                    service_name = service_name,
                    startup_time = datetime.datetime.utcnow(),
                    shut_down_time = None,
                    created_date = datetime.datetime.utcnow()
                )
                session.commit()
                return system_event
            elif version_to_check < recorded_version:
                logger.info('Downgrade version detected: [{}]'.format(version_to_check))
                system_event = SystemEvents.new(
                    session = session,
                    kind = 'version_downgrade',
                    description = 'Diffgram System startup for {} service'.format(service_name),
                    install_fingerprint = settings.DIFFGRAM_INSTALL_FINGERPRINT,
                    previous_version = None,
                    diffgram_version = version_to_check,
                    host_os = settings.DIFFGRAM_HOST_OS,
                    storage_backend = settings.DIFFGRAM_STATIC_STORAGE_PROVIDER,
                    service_name = service_name,
                    startup_time = datetime.datetime.utcnow(),
                    shut_down_time = None,
                    created_date = datetime.datetime.utcnow()
                )
                session.commit()
                return system_event
            else:
                # On equal versions, we do nothing.
                return None

    @staticmethod
    def check_os_change(session, service_name):
        """
            Checks the current version in the system and generates an event
            if version has changed.
        :param session:
        :return:
        """
        latest_recorded_version_event = session.query(SystemEvents).filter(
            SystemEvents.kind == 'os_change'
        ).order_by('created_date').first()

        if latest_recorded_version_event is not None:
            if latest_recorded_version_event.host_os != settings.DIFFGRAM_HOST_OS:
                system_event = SystemEvents.new(
                    session = session,
                    kind = 'os_change',
                    description = 'OS Init for {} service from {} to {}'.format(service_name,
                                                                                latest_recorded_version_event.host_os,
                                                                                settings.DIFFGRAM_HOST_OS),
                    install_fingerprint = settings.DIFFGRAM_INSTALL_FINGERPRINT,
                    previous_version = None,
                    diffgram_version = settings.DIFFGRAM_VERSION_TAG,
                    host_os = settings.DIFFGRAM_HOST_OS,
                    storage_backend = settings.DIFFGRAM_STATIC_STORAGE_PROVIDER,
                    service_name = service_name,
                    startup_time = None,
                    shut_down_time = None,
                    created_date = datetime.datetime.utcnow()
                )
                session.commit()
                return system_event
        else:
            system_event = SystemEvents.new(
                session = session,
                kind = 'os_change',
                description = 'OS Change for {} service'.format(service_name),
                install_fingerprint = settings.DIFFGRAM_INSTALL_FINGERPRINT,
                previous_version = None,
                diffgram_version = settings.DIFFGRAM_VERSION_TAG,
                host_os = settings.DIFFGRAM_HOST_OS,
                storage_backend = settings.DIFFGRAM_STATIC_STORAGE_PROVIDER,
                service_name = service_name,
                startup_time = None,
                shut_down_time = None,
                created_date = datetime.datetime.utcnow()
            )
            session.commit()
            return system_event

    def serialize(self):
        return {
            'id': self.id,
            'kind': self.kind,
            'description': self.description,
            'install_fingerprint': self.install_fingerprint,
            'previous_version': self.previous_version,
            'diffgram_version': self.diffgram_version,
            'host_os': self.host_os,
            'storage_backend': self.storage_backend,
            'service_name': self.service_name,
            'startup_time': self.startup_time.strftime('%Y-%m-%d') if self.startup_time else None,
            'shut_down_time': self.shut_down_time.strftime('%Y-%m-%d') if self.shut_down_time else None,
            'created_date': self.created_date.strftime('%Y-%m-%d') if self.created_date else None,
        }

    def send_to_segment(self):
        """
            Sending system actions to segment. Here each user will be a install
            fingerprint to identify system events per Diffgram installation.
        :return:
        """
        if not self.install_fingerprint:
            return
        if not self.kind:
            return
        if not settings._ANALYTICS_WRITE_KEY or settings.DIFFGRAM_SYSTEM_MODE in ['sandbox', 'testing', 'testing_e2e']:
            return
        props = {
            'description': self.description,
            'host_os': self.host_os,
            'diffgram_version': self.diffgram_version,
            'service_name': self.service_name,
            'storage_backend': self.storage_backend,
            'created_at': self.created_date,
            'install_fingerprint': self.install_fingerprint,
        }
        try:
            analytics.track(
                user_id = self.install_fingerprint,
                event = self.kind,
                properties = props,
                context = {
                    'os': self.host_os,
                    'app': {
                        'name': self.service_name,
                        'version': self.diffgram_version,
                        'build': self.diffgram_version,
                    }
                }
            )
            return True
        except Exception as e:
            logger.error('Error sending event to segment: {}'.format(str(e)))
            logger.error(traceback.format_exc())
            pass

    def send_to_eventhub(self):
        """
            Sends the current event to Diffgram's EventHub for anonymous data tracking.
        :return:
        """
        if settings.DIFFGRAM_SYSTEM_MODE in ['sandbox', 'testing', 'testing_e2e']:
            return
        try:
            event_data = self.serialize()
            event_data['event_type'] = 'system'
            result = requests.post(settings.EVENTHUB_URL, json = event_data)
            if result.status_code == 200:
                logger.info("Sent event: {} to Diffgram Eventhub".format(self.id))
                return True
            else:
                print(result, result.text)
                logger.error(
                    "Error sending {} to Diffgram Eventhub. Status Code: ".format(self.id, result.status_code))
        except Exception as e:
            logger.error("Exception sending {} to Diffgram Eventhub: ".format(str(e)))

    @staticmethod
    def new(session,
            kind = None,
            description = None,
            install_fingerprint = None,
            previous_version = None,
            diffgram_version = None,
            host_os = None,
            storage_backend = None,
            service_name = None,
            startup_time = None,
            shut_down_time = None,
            created_date = None,
            add_to_session = True,
            flush_session = True):

        event = SystemEvents(
            kind = kind,
            description = description,
            install_fingerprint = install_fingerprint,
            previous_version = previous_version,
            diffgram_version = diffgram_version,
            host_os = host_os,
            storage_backend = storage_backend,
            service_name = service_name,
            startup_time = startup_time,
            shut_down_time = shut_down_time,
            created_date = created_date,
        )
        if add_to_session:
            session.add(event)
        if flush_session:
            session.flush()

        event.send_to_segment()
        event.send_to_eventhub()
        return event
