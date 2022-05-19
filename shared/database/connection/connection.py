from shared.database.common import *
from sqlalchemy import LargeBinary


INTEGRATION_VENDORS_SUPPORTED_FEATURES = {
    'google_gcp': {
        'files_import': True,
        'files_export': True,
    },
    'amazon_aws': {
        'files_import': True,
        'files_export': True
    },
    'microsoft_azure': {
        'files_import': True,
        'files_export': True
    },
    'labelbox': {
        'labeling_interface': True,
        'project_migration': True,
        'allowed_instance_types': ['box', 'polygon']
    },
    'scale_ai': {
        'labeling_interface': True,
        'outsource_service': True,
        'allowed_instance_types': ['box', 'polygon']
    },
    'datasaur': {
        'labeling_interface': True,
        'allowed_instance_types': ['text_tokens']
    },
    'diffgram': {
        'labeling_interface': True,
        'allowed_instance_types': ['box', 'polygon', 'line', 'point', 'tag', 'cuboid', 'ellipse', 'curve', 'custom', 'keypoint']
    },
    'minio': {
        'files_import': True,
        'files_export': True
    }
}


class Connection(Base):
    __tablename__ = 'connection_base'  # avoid reserved name conflict

    """

    """

    id = Column(Integer, primary_key=True)
    name = Column(String())
    archived = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)

    # In [project, org, diffgram_wide, future]
    permission_scope = Column(String, default="project")

    integration_name = Column(String())  # ie google_general , s3, scale_ai, ...
    integration_version = Column(Integer, default=1)  # ie for future migration

    private_id = Column(String())
    private_host = Column(String())
    disabled_ssl_verify = Column(Boolean(), default=False)

    # https://stackoverflow.com/questions/27197965/what-type-is-used-to-store-byte-strings-in-sqlalchemy
    private_secret_encrypted = Column(LargeBinary())  # aka api_key, sas_uri, etc.

    account_email = Column(String())  # ie for Google
    project_id_external = Column(String())  # ie for Google
    # _external because project_id is the internal project_id for Diffgram

    # Standard items

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", foreign_keys=[project_id])

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys=[member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys=[member_updated_id])

    time_created = Column(DateTime, default=datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate=datetime.datetime.utcnow)

    ####

    def serialize(self):

        return {
            'id': self.id,
            'name': self.name,
            'permission_scope': self.permission_scope,
            'project_id': self.project_id,
            'member_created_id': self.member_created_id,
            'member_updated': self.member_updated,
            'time_created': self.time_created,
            'time_updated': self.time_updated,
            'archived': self.archived,
            'private_id': self.private_id,
            'private_host': self.private_host,
            'disabled_ssl_verify': self.disabled_ssl_verify,
            'account_email': self.account_email,
            'project_id_external': self.project_id_external,
            'supported_features': INTEGRATION_VENDORS_SUPPORTED_FEATURES[self.integration_name],
            # use built in bool to return True/False so we don't reveal (even) the encrypted info
            'exists_private_secret': bool(self.private_secret_encrypted),
            'integration_name': self.integration_name,
            'integration_version': self.integration_version

        }

    @staticmethod
    def get_by_id(session,
                  id: int):

        return session.query(Connection).filter(
            Connection.id == id).first()

    @staticmethod
    def list(
            session,
            permission_scope: str,
            project=None,
            limit=100,
            return_kind="objects",
            date_to=None,
            date_from=None
    ):
        """


        """
        query = session.query(Connection)
        query = query.filter(Connection.archived == False)

        if permission_scope == "project" and project:
            query = query.filter(Connection.project_id == project.id)

        else:
            return False

        # TODO this is missing the "AND" joint thing for date_from
        if date_from:
            query = query.filter(Connection.time_created >= date_from)

        if date_to:
            query = query.filter(Connection.time_created <= date_to)

        if return_kind == "count":
            return query.limit(limit).count()

        if return_kind == "objects":
            return query.limit(limit).all()

    @staticmethod
    def new(
            member: 'Member' = None,
            project: 'Project' = None) -> 'Connection':

        return Connection(
            member_created=member,
            project=project
        )