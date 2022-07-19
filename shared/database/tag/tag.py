from shared.database.common import *
import re
import random

tag_format = "^[a-zA-Z0-9_-]{1,40}$"
KEYWORD_RE = re.compile(r + tag_format)


class Tag(Base):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key = True)

    name = Column('name', String(64))

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project")

    archived = Column(Boolean)

    color_hex = Column(String())    # FFFFFF   without leading hashtag "#"

    created_time = Column(DateTime, default=datetime.datetime.utcnow)
    last_time = Column(DateTime, onupdate=datetime.datetime.utcnow)


    def serialize(self):
        return {
            'name': self.name,
            'archived': self.archived,
            'color_hex': self.color_hex,
            'id': self.id
        }

    def valid_tag(string):
        if not KEYWORD_RE.match(string):
            return False

    @staticmethod
    def get_random_color():
        return "%06x" % random.randint(0, 0xFFFFFF)


    @staticmethod
    def get(name: str,
            project_id: int):
        
        tag = session.query(Tag).filter(
            Tag.name == name,
            Tag.project_id == project_id).first()

        return tag


    @staticmethod
    def get_many(
            name_list: list,
            project_id: int):
        
        tag = session.query(Tag).filter(
            Tag.name.in_(name_list),
            Tag.project_id == project_id).first()

        return tag


    @staticmethod
    def get_or_new(
            name: str,
            project_id: int):

        tag = Tag.get(name = name,
                      project_id = project_id)

        if tag: return tag

        tag = Tag.new(
                name = name,
                project_id = project_id)

        return tag


    @staticmethod
    def new(
            name: str,
            project_id: int,            
            color_hex: str = None):

        if valid_tag(name) is False:
            return "Invalid tag format, format is regular expression of: " + tag_format

        tag = Tag()
        tag.name = name
        tag.project_id = project_id

        if color_hex is None:
            tag.color_hex = Tag.get_random_color()

        return tag


    def add_to_job(
            self,
            job_id: int
            ):

        jobtag = JobTag.new(
            job_id = job_id,
            tag = tag,
            project_id = self.project_id
            )

        return jobtag


    @staticmethod
    def get_by_project(project_id: int):
        tag_list = session.query(Tag).filter(
            Tag.project_id == project_id).all()
        return tag_list




class JobTag(Base):
    __tablename__ = 'job_tag'

    job_id = Column(Integer, ForeignKey('job.id'), primary_key = True)
    tag_id = Column(Integer, ForeignKey('tag.id'), primary_key = True)
    project_id = Column(Integer, ForeignKey('project.id'), primary_key = True)

    job = relationship("Job")
    tag = relationship("Tag")
    project = relationship("Project")

    created_time = Column(DateTime, default=datetime.datetime.utcnow)


    @staticmethod
    def new(job_id: int,
            tag_id: int,
            project_id: int,
            tag
            ):

        jobtag = JobTag(
            job_id=job_id,
            tag_id=tag_id,
            tag=tag,
            project_id=project_id
        )

        return jobtag


    @staticmethod
    def get_many(
            name_list: list,
            project_id: int):
        
        jobtag = session.query(JobTag).filter(
            JobTag.name.in_(name_list),
            JobTag.project_id == project_id).first()

        return jobtag

