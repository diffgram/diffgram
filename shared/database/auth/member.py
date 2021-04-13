# OPENCORE - ADD
from shared.database.common import *


class Member(Base):
	"""

	# may be user or api 

	"""

	__tablename__ = 'member'

	id = Column(Integer, primary_key=True)

	kind = Column(String()) 
	# [ "human", "api", ... ]

	user_id = Column(Integer, ForeignKey('userbase.id'))
	user = relationship('User', foreign_keys=[user_id], 
					    uselist=False, back_populates="member")

	auth_api_id = Column(Integer, ForeignKey('auth_api.id'))
	auth_api = relationship('Auth_api', foreign_keys=[auth_api_id], 
						  uselist=False, back_populates="member")

	# TODO future
	# May be some more permissions we can move into here / share
	
	def get_by_id(	session, 
					member_id):

		return session.query(Member).filter(
					Member.id == member_id).first()
	

