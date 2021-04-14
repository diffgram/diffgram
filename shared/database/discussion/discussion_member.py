# OPENCORE - ADD
from shared.database.common import *


class DiscussionMember(Base):
    __tablename__ = 'discussion_member'
    id = Column(Integer, primary_key = True)

    user_id = Column(Integer, ForeignKey('userbase.id'))
    user = relationship("User", foreign_keys = [user_id])

    #TODO add member_id

    discussion_id = Column(Integer, ForeignKey('discussion.id'))
    discussion = relationship("Discussion", foreign_keys = [discussion_id])
