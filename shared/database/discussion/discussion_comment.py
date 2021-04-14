# OPENCORE - ADD
from shared.database.common import *


class DiscussionComment(Base):
    """
    

    """
    __tablename__ = 'discussion_comment'

    id = Column(Integer, primary_key = True)

    user_id = Column(Integer, ForeignKey('userbase.id'))
    user = relationship("User")

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", foreign_keys = [project_id])

    discussion_id = Column(Integer, ForeignKey('discussion.id'))
    discussion = relationship("Discussion", foreign_keys = [discussion_id])

    # Markdown format?
    content = Column(String())

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys = [member_updated_id])

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    # Add reaction?
    @staticmethod
    def update(
            session: object,
            comment_id: int = None,
            member: object = None,
            content: str = None,
    ):
        comment = DiscussionComment.get_by_id(session, id = comment_id)
        comment.content = content
        comment.member_updated = member
        comment.time_updated = datetime.datetime.utcnow()
        session.add(comment)
        return comment

    @staticmethod
    def list(
            session: object,
            project_id: int = None,
            discussion_id: int = None,
            ordering: str = 'asc',
    ):
        """
            List the comments based on the given dicussion and project_id.
        :param session:
        :param project_id:
        :param discussion_id:
        :param ordering: Can be any of ['asc', 'desc']. Sets the ordering of the result by the created time.
        :return:
        """
        query = session.query(DiscussionComment).filter(
            DiscussionComment.discussion_id == discussion_id,
            DiscussionComment.project_id == project_id
        )

        if ordering == 'asc':
            query = query.order_by(DiscussionComment.time_created.asc())
        else:
            query = query.order_by(DiscussionComment.time_created.desc())
        return query.all()

    @staticmethod
    def new(
            session: object,
            content: str = None,
            member_created_id: int = None,
            project_id: int = None,
            member_updated_id: int = None,
            discussion_id: int = None,
            user_id: int = None,
            add_to_session: bool = True,
            flush_session: bool = True
    ):
        comment = DiscussionComment(
            content = content,
            project_id = project_id,
            user_id = user_id,
            discussion_id = discussion_id,
            member_created_id = member_created_id,
            member_updated_id = member_updated_id,
        )
        if add_to_session:
            session.add(comment)
        if flush_session:
            session.flush()

        return comment

    @staticmethod
    def get_by_id(session: object, id: int):
        return session.query(DiscussionComment).filter(DiscussionComment.id == id).first()

    def serialize(self):
        return {
            'id': self.id,
            'user': self.user.serialize_for_activity() if self.user else None,
            'discussion_id': self.discussion_id,
            'member_created_id': self.member_created_id,
            'member_updated_id': self.member_updated_id,
            'time_created': self.time_created,
            'time_updated': self.time_updated,
            'content': self.content
        }
