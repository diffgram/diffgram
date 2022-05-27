# OPENCORE - ADD
from shared.database.common import *
from shared.database.common import data_tools
from shared.settings import settings
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
        data = data_tools.get_string_from_blob(self.tokens_url_signed_blob_path)
        data_dict = json.loads(data)
        result = data_dict[tokenizer_type]
        return result

    def get_text(self):
        """
            Download Raw text from blob.
        :return:
        """
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

    def serialize(self, session):

        self.regenerate_url(session)

        text = {
            'original_filename': self.original_filename,
            'soft_delete': self.soft_delete,
            'url_signed': self.url_signed,
            'id': self.id,
            'is_inference': self.is_inference,
            'tokens_url_signed': self.tokens_url_signed,
            'is_annotation_example': self.is_annotation_example,
            'annotation_status': self.annotation_status
        }
        return text


    def regenerate_tokens_urls(self, session, new_offset_in_seconds):
        """
            Refresh signed URL for tokens Blob of the text file.
        :param session:
        :return:
        """
        if self.tokens_url_signed_blob_path:
            self.tokens_url_signed = data_tools.build_secure_url(self.tokens_url_signed_blob_path,
                                                                    new_offset_in_seconds)
            #self.tokens_url_signed_expiry = time.time() + new_offset_in_seconds
            session.add(self)

    def regenerate_url(self, session):
        """
            Refresh signed URL for the raw Text blob.
        :param session:
        :return:
        """
        should_regenerate, new_offset_in_seconds = data_tools.determine_if_should_regenerate_url(self, session)
        if should_regenerate is True:
            self.url_signed = data_tools.build_secure_url(self.url_signed_blob_path, new_offset_in_seconds)
            self.url_signed_expiry = time.time() + new_offset_in_seconds
            session.add(self)

            self.regenerate_tokens_urls(session, new_offset_in_seconds)
