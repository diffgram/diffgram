from shared.database.common import *
from shared.shared_logger import get_shared_logger
from shared.regular.regular_methods import commit_with_rollback

logger = get_shared_logger()


class SystemConfigs(Base):
    """
        Global configurations for the diffgram installation.
    """
    __tablename__ = 'system_configs'
    id = Column(BIGINT, primary_key = True)

    logo_id = Column(Integer, ForeignKey('image.id'))
    logo = relationship("Image")


    def serialize(self, session):
        logo_data = None
        if self.logo_id:
            logo_data = self.logo.serialize_for_source_control(session = session, regen_url = True)
        return {
            'id': self.id,
            'logo_id': self.logo_id,
            'logo': logo_data
        }

    @staticmethod
    def set_logo(session, image_id: int):
        """
            Saves the config blob path from logo and generates signed URL.
        :param session:
        :param blob_path:
        :return: Updated configs object
        """
        configs = SystemConfigs.get_configs(session = session)
        if not configs:
            configs = SystemConfigs.new(session = session)
        configs.logo_id = image_id
        session.add(configs)
        return configs
    @staticmethod
    def get_configs(session):
        result = session.query(SystemConfigs).first()
        if not result:
            result = SystemConfigs.new(session = session)
        return result
    @staticmethod
    def new(session,
            logo_id: int = None,
            add_to_session = True,
            flush_session = True):

        configs = SystemConfigs(
            logo_id = logo_id,
        )
        if add_to_session:
            session.add(configs)
        if flush_session:
            session.flush()

        # Try commit
        commit_with_rollback(session)

        return configs
