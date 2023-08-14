from shared.database.common import *


class GeoAsset(Base):
    __tablename__ = 'geo_asset'

    id = Column(BIGINT, primary_key = True)

    original_filename = Column(String())
    description = Column(String())
    type = Column(String())  # ['layer', 'attachment']
    soft_delete = Column(Boolean, default = False)

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project")

    file_id = Column(Integer, ForeignKey('file.id'))
    file = relationship("File")

    url_signed = Column(String())
    url_signed_blob_path = Column(String())

    url_signed_expiry = Column(Integer)

    url_signed_expiry_force_refresh = Column(Integer)

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    @staticmethod
    def get_by_id(session, id):
        return session.query(GeoAsset).filter(GeoAsset.id == id).first()

    @staticmethod
    def new(session,
            file_id,
            project_id,
            original_filename = None,
            url_signed_blob_path = None,
            description = None,
            type = 'layer',
            soft_delete = False,
            add_to_session = True,
            flush_session = True
            ):

        point_cloud = GeoAsset(
            original_filename = original_filename,
            url_signed_blob_path = url_signed_blob_path,
            description = description,
            file_id = file_id,
            project_id = project_id,
            type = type,
            soft_delete = soft_delete
        )
        if add_to_session:
            session.add(point_cloud)
        if flush_session:
            session.flush()

        return point_cloud

    def serialize(self, session, connection_id = None, bucket_name = None, regen_url = True):
        if regen_url:
            from shared.url_generation import blob_regenerate_url
            blob_regenerate_url(blob_object = self,
                                session = session,
                                connection_id = connection_id,
                                bucket_name = bucket_name)
        data = {
            'id': self.id,
            'original_filename': self.original_filename,
            'description': self.description,
            'soft_delete': self.soft_delete,
            'file_id': self.file_id,
            'url_signed': self.url_signed,
            'url_signed_blob_path': self.url_signed_blob_path,
            'url_signed_expiry_force_refresh': self.url_signed_expiry_force_refresh,
            'time_created': self.time_created,
            'time_updated': self.time_updated,
        }
        return data
