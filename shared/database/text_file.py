from shared.database.common import *

import json


class TextFile(Base):
    __tablename__ = 'text_file'

    id = Column(BIGINT, primary_key = True)

    original_filename = Column(String(250))
    description = Column(String(250))

    soft_delete = Column(Boolean, default = False)

    mask_joint_url = Column(String())
    mask_joint_blob_name = Column(String())

    is_inference = Column(Boolean, default = False)

    annotation_status = Column(String())  # "complete" "init" "in_progress" ?

    is_annotation_example = Column(Boolean, default = False)
    url_annotation_example = Column(String())

    url_public = Column(String())

    url_signed = Column(String())
    url_signed_blob_path = Column(String())

    url_signed_expiry = Column(Integer)

    tokens_url_signed = Column(String())
    tokens_url_signed_blob_path = Column(String())

    tokens_url_signed_expiry = Column(Integer)

    url_signed_expiry_force_refresh = Column(Integer)
    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    def get_text_tokens(self, tokenizer_type):
        from shared.data_tools_core import data_tools
        data = data_tools.get_string_from_blob(self.tokens_url_signed_blob_path)
        data_dict = json.loads(data)
        result = data_dict[tokenizer_type]
        return result

    def get_text(self):
        """
            Download Raw text from blob.
        :return:
        """
        from shared.data_tools_core import data_tools
        data = data_tools.get_string_from_blob(self.tokens_url_signed_blob_path)
        return data

    def get_by_id(session, id):
        return session.query(TextFile).filter(TextFile.id == id).first()

    # For annotation assignments
    def serialize_for_example(self):
        text = {
            'is_annotation_example': self.is_annotation_example,
            'url_annotation_example': self.url_annotation_example,
            'url_annotation_example_thumb': self.url_annotation_example_thumb
        }
        return text

    def serialize(self, session, connection_id = None, bucket_name = None, regen_url = True):
        if regen_url:
            from shared.url_generation import blob_regenerate_url
            blob_regenerate_url(blob_object = self,
                                session = session,
                                connection_id = connection_id,
                                bucket_name = bucket_name)

        text = {
            'original_filename': self.original_filename,
            'soft_delete': self.soft_delete,
            'url_signed': self.url_signed,
            'url_signed_blob_path': self.url_signed_blob_path,
            'id': self.id,
            'is_inference': self.is_inference,
            'tokens_url_signed': self.tokens_url_signed,
            'is_annotation_example': self.is_annotation_example,
            'annotation_status': self.annotation_status
        }
        return text

    def regenerate_tokens_urls(self, session, new_offset_in_seconds, connection_id = None, bucket_name = None):
        """
            Refresh signed URL for tokens Blob of the text file.
        :param session:
        :return:
        """
        from shared.url_generation import blob_regenerate_url
        blob_regenerate_url(blob_object = self,
                            session = session,
                            connection_id = connection_id,
                            bucket_name = bucket_name)