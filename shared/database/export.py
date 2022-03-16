# OPENCORE - ADD
from shared.database.common import *

EXPORT_VERSION = '1.0'


class Export(Base):
    __tablename__ = 'export'

    id = Column(Integer, primary_key = True)
    created_time = Column(DateTime, default = datetime.datetime.utcnow)

    type = Column(String())  # "annotation_file" or ...

    # [Annotations, TF Records]
    kind = Column(String)

    archived = Column(Boolean, default = False)  # Hide from list

    masks = Column(Boolean)

    # directory, version (source control)
    source = Column(String)

    status = Column(String(), default = "init")
    status_text = Column(String())

    percent_complete = Column(Float, default = 0.0)

    file_comparison_mode = Column(String())
    file_list_length = Column(Integer)

    description = Column(String())

    working_dir_id = Column(Integer, ForeignKey('working_dir.id'))
    working_dir = relationship("WorkingDir", back_populates = "export_list")

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", back_populates = "export_list")

    # This may be blank if automatically generate by project?
    user_id = Column(Integer, ForeignKey('userbase.id'))
    user = relationship("User", foreign_keys = [user_id])

    job_id = Column(Integer, ForeignKey('job.id'))
    job = relationship("Job")
    # A job may have many exports (even if it's just different kinds
    # {TFRECRODS, JSON, etc}.

    task_id = Column(Integer, ForeignKey('task.id'))
    task = relationship("Task")

    # Maybe always generate URLs on demand for this
    # given sensitivity of data?
    yaml_blob_name = Column(String())
    json_blob_name = Column(String())

    tf_records_blob_name = Column(String())
    ann_is_complete = Column(Boolean)

    def serialize(self, session = None):

        directory = None
        if self.working_dir:
            directory = self.working_dir.serialize()

        job = None
        if self.job:
            job = self.job.serialize_for_list_view()

        task = None
        if self.task:
            task = self.task.serialize_for_list_view_builder(session=session)

        return {
            'id': self.id,
            'kind': self.kind,
            'masks': self.masks,
            'source': self.source,
            'status': self.status,
            'status_text': self.status_text,
            'file_comparison_mode': self.file_comparison_mode,
            'percent_complete': self.percent_complete,
            'created_time': self.created_time,
            'directory': directory,
            'job': job,
            'task': task,
            'file_list_length': self.file_list_length,
            'ann_is_complete': self.ann_is_complete
        }

    # INSIDE export
    def serialize_for_inside_export_itself(self):

        directory = None
        if self.working_dir:
            directory = self.working_dir.serialize()

        job = None
        if self.job:
            job = self.job.serialize_for_list_view()

        project = None,
        if self.project:
            project = self.project.serialize_for_export()

        task = None
        if self.task:
            task = self.task.serialize_for_list_view_builder()

        user_created_email = None
        if self.user:
            user_created_email = self.user.email

        return {
            'id': self.id,
            'export_format_version': EXPORT_VERSION,
            'user_created_email': user_created_email,
            'created_time': str(self.created_time),
            'kind': self.kind,
            'masks': self.masks,
            'source': self.source,
            'file_comparison_mode': self.file_comparison_mode,
            'project': project,
            'directory': directory,
            'job': job,
            'task': task,
            'file_list_length': self.file_list_length,
            'ann_is_complete': self.ann_is_complete
        }

    def serialize_readme(
        self
    ):

        docs_high_level = "https://diffgram.com/docs/export-walkthrough"
        docs_low_level = "https://diffgram.com/docs/understanding-diffgrams-json-file-format"
        docs_coordinate_system = "https://diffgram.com/docs/export#coordinate-system"
        support = "support@diffgram.com"
        sdk = "https://github.com/diffgram/diffgram"
        new_to_diffgram = "Create a free account to play with: https://diffgram.com/user/data_platform/new"

        share_request = None
        if self.user:
            share_request = f"Request {self.user.email} to access the project to visually explore this data."

        return {
            'docs_high_level': docs_high_level,
            'docs_low_level': docs_low_level,
            'docs_coordinate_system': docs_coordinate_system,
            'support': support,
            'sdk': sdk,
            'new_to_diffgram': new_to_diffgram,
            'share_request': share_request,
            'diffgram': "Diffgram: https://diffgram.com. Data Annotation & Training Data Software"
        }

    def get_by_id(
        session,
        export_id):

        export = session.query(Export).filter(
            Export.id == export_id).first()

        return export
