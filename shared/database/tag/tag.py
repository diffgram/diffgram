from shared.database.common import *
import re
import random

tag_format = "^[a-zA-Z0-9_-]{1,40}$"


class Tag(Base):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key = True)

    name = Column('name', String(64))

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project")

    archived = Column(Boolean)

    color_hex = Column(String())    # FFFFFF   without leading hashtag "#"

    time_created = Column(DateTime, default=datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate=datetime.datetime.utcnow)


    def serialize(self):
        return {
            'name': self.name,
            'archived': self.archived,
            'color_hex': self.color_hex,
            'id': self.id
        }

    def valid_tag(string):
        if not re.match(tag_format, string):
            return False

    @staticmethod
    def get_random_color():
        return "%06x" % random.randint(0, 0xFFFFFF)


    @staticmethod
    def get(name: str,
            project_id: int,
            session):
        
        tag = session.query(Tag).filter(
            Tag.name == name,
            Tag.project_id == project_id).first()

        return tag


    @staticmethod
    def get_from_junction_table_object(
            junction_tag_list: list,
            session):
        
        tag_id_list = []
        for junction in junction_tag_list:
            tag_id_list.append(junction.tag_id)

        tag_list = session.query(Tag).filter(
            Tag.id.in_(tag_id_list)).all()

        return tag_list

    @staticmethod
    def marshal_serialized_from_junction(
            junction_tag_list, 
            session):

        tag_list = Tag.get_from_junction_table_object(
            junction_tag_list = junction_tag_list,
            session = session)

        tag_list_serailized = []
        for tag in tag_list:
            tag_list_serailized.append(tag.serialize())

        return tag_list_serailized


    @staticmethod
    def get_many(
            name_list: list,
            project_id: int,
            session):
        
        tag = session.query(Tag).filter(
            Tag.name.in_(name_list),
            Tag.project_id == project_id).first()

        return tag


    @staticmethod
    def get_or_new(
            name: str,
            project_id: int,
            session):

        tag = Tag.get(name = name,
                      project_id = project_id,
                      session = session)

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

        if Tag.valid_tag(name) is False:
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
            tag = self,
            project_id = self.project_id
            )

        return jobtag


    def add_to_dataset(
            self,
            dataset_id: int,
            session
            ):

        dataset_tag = DatasetTag.get(
            dataset_id = dataset_id,
            tag = self,
            project_id = self.project_id,
            session = session
        )

        if not dataset_tag:
            dataset_tag = DatasetTag.new(
                dataset_id = dataset_id,
                tag = self,
                project_id = self.project_id
                )

        return dataset_tag


    @staticmethod
    def get_by_project(project_id: int, 
                       session):
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

    time_created = Column(DateTime, default=datetime.datetime.utcnow)


    @staticmethod
    def new(job_id: int,
            project_id: int,
            tag
            ):

        jobtag = JobTag(
            job_id=job_id,
            tag=tag,
            project_id=project_id
        )

        return jobtag


    @staticmethod
    def get_many(
            tag_id_list: list,
            project_id: int,
            session):
        
        jobtag = session.query(JobTag).filter(
            JobTag.tag_id.in_(tag_id_list),
            JobTag.project_id == project_id).all()

        return jobtag


    @staticmethod
    def get_by_job_id(
            job_id: int,
            project_id: int,
            session):
        
        junction_tag_list = session.query(JobTag).filter(
            JobTag.job_id == job_id,
            JobTag.project_id == project_id).all()

        return junction_tag_list




class DatasetTag(Base):
    __tablename__ = 'dataset_tag'

    dataset_id = Column(Integer, ForeignKey('working_dir.id'), primary_key = True)
    tag_id = Column(Integer, ForeignKey('tag.id'), primary_key = True)
    project_id = Column(Integer, ForeignKey('project.id'), primary_key = True)

    dataset = relationship("WorkingDir")
    tag = relationship("Tag")
    project = relationship("Project")

    time_created = Column(DateTime, default=datetime.datetime.utcnow)


    @staticmethod
    def new(dataset_id: int,
            project_id: int,
            tag
            ):

        dataset_tag = DatasetTag(
            dataset_id=dataset_id,
            tag=tag,
            project_id=project_id
        )

        return dataset_tag


    @staticmethod
    def delete(self):
        session.delete(self)


    @staticmethod
    def get_by_tag_ids(
            tag_id_list: list,
            project_id: int,
            session):
        
        dataset_tag_list = session.query(DatasetTag).filter(
            DatasetTag.tag_id.in_(tag_id_list),
            DatasetTag.project_id == project_id).all()

        return dataset_tag_list

    @staticmethod
    def get(dataset_id: int,
            project_id: int,
            tag,
            session
            ):

        return session.query(DatasetTag).filter(
            DatasetTag.dataset_id == dataset_id,
            DatasetTag.tag==tag,
            DatasetTag.project_id == project_id).first()


    @staticmethod
    def get_by_dataset_id(
            dataset_id: int,
            project_id: int,
            session):
        
        dataset_tag_list = session.query(DatasetTag).filter(
            DatasetTag.dataset_id == dataset_id,
            DatasetTag.project_id == project_id).all()

        return dataset_tag_list


