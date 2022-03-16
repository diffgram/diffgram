from shared.database.common import *
from sqlalchemy import asc, desc
from sqlalchemy import nullslast
from sqlalchemy import or_


class UserScript(Base):
    __tablename__ = 'userscript' 

    """
    Docs
    https://docs.google.com/document/d/1RFJMy0T8fI9B6he79V6mrwV2Vynth3v0Uwe_G8aZOtw/edit

    """

    id = Column(Integer, primary_key=True)

    archived = Column(Boolean, default=False)
    is_visible = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)

    ##############

    name = Column(String())
    code = Column(String())
    language = Column(String()) # eg javascript python
    external_src_list = Column(ARRAY(String()))
    use_instructions = Column(String())
    docs_link = Column(String())

    ##############

    star_rating_cache = Column(Float)

    previous_id = Column(BIGINT)
    next_id = Column(BIGINT)
    root_id = Column(BIGINT)
    version = Column(Integer, default = 0)

    ##############
    # Standard items

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", foreign_keys=[project_id])
  
    client_created_time = Column(DateTime, nullable = True)
    client_creation_ref_id = Column(String(), nullable = True)

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
            'project_id': self.project_id,
            'is_public': self.is_public,
            'member_created_id': self.member_created_id,
            'member_updated': self.member_updated,
            'time_created': self.time_created,
            'time_updated': self.time_updated,
            'archived': self.archived,
            'is_visible': self.is_visible,
            'code': self.code,
            'external_src_list': self.external_src_list,
            'use_instructions': self.use_instructions,
            'docs_link': self.docs_link,
            'client_creation_ref_id': self.client_creation_ref_id,
            'language': self.language
        }

    @staticmethod
    def get_by_id(session,
                  id: int):

        return session.query(UserScript).filter(
            UserScript.id == id).first()


    @staticmethod
    def get(session,
            id: int,
            project_id: int):

        query = session.query(UserScript)
        query = query.filter(UserScript.id == id)
        query = query.filter(or_(
            UserScript.project_id == project_id,
            UserScript.is_public == True
            ))

        return query.first()


    @staticmethod
    def list(
            session,
            project_id=None,
            org=None,
            limit=100,
            return_kind="objects",
            archived = False,
            date_to = None,     # datetime
            date_from = None,   # datetime
            date_to_string: str = None,
            date_from_string: str = None,
            name: str = None,
            name_match_type: str = "ilike",  # substring and helps if case Aa is off
            order_by_class_and_attribute = None,
            order_by_direction = desc,
            public_only = False
            ):
        """


        """

        query = session.query(UserScript)

        # Assume we must either have public script or project id
        if public_only is True:
            query = query.filter(UserScript.is_public == True)
        else:
            query = query.filter(UserScript.project_id == project_id)

        if name:
            if name_match_type == "ilike":
                name_search = f"%{name}%"
                query = query.filter(UserScript.name.ilike(name_search))
            else:
                query = query.filter(UserScript.name == name)

        if date_from or date_to:
            if date_from:
                query = query.filter(UserScript.created_time >= date_from)
            if date_to:
                query = query.filter(UserScript.created_time <= date_to)
        else:
            query = regular_methods.regular_query(
                query=query,
                date_from_string=date_from_string,
                date_to_string=date_to_string,
                base_class=UserScript,
                created_time_string='time_updated'
            )

        if archived is False:   
            query = query.filter(UserScript.archived == False)

        if order_by_class_and_attribute:
            query = query.order_by(
                nullslast(order_by_direction(order_by_class_and_attribute)))

        if return_kind == "count":
            return query.limit(limit).count()

        if return_kind == "objects":
            return query.limit(limit).all()


    @staticmethod
    def new(
            member: 'Member' = None,
            project: 'Project' = None,
            client_created_time = None,
            client_creation_ref_id = None,
            name = None,
            code = None,
            external_src_list = None,
            use_instructions = None,
            language = 'javascript'
            ) -> 'UserScript':


        return UserScript(
            member_created=member,
            project=project,
            client_created_time = client_created_time,
            client_creation_ref_id = client_creation_ref_id,
            name = name,
            code = code,
            external_src_list = external_src_list,
            use_instructions = use_instructions,
            language = language
        )
