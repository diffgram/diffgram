# OPENCORE - ADD
from shared.database.common import *


class Auth_api(Base):
	"""

	TODO should we merge "auth api" and user as "members"...

	"""

	__tablename__ = 'auth_api'

	id = Column(Integer, primary_key=True)

	member_id = Column(Integer, ForeignKey('member.id'))
	member = relationship('Member', foreign_keys = "Member.auth_api_id", uselist=False)

	created_time = Column(DateTime, default=datetime.datetime.utcnow)

	client_id = Column(String())
	client_secret = Column(String())

	project_string_id = Column(String())

	project_id = Column(Integer, ForeignKey('project.id'))
	project = relationship("Project")

	is_live = Column(Boolean, default=True)		# live or test
	is_valid = Column(Boolean, default=True)		# valid or revoked

	permission_level = Column(String())



	def get(session, client_id):
		return session.query(Auth_api).filter(
					Auth_api.client_id == client_id).first()


	def list_by_project(session, project_string_id):
		return session.query(Auth_api).filter(
					Auth_api.project_string_id == project_string_id,
					Auth_api.is_valid == True
					).all()


	def serialize_with_secret(self):
		return {
			'created_time': self.created_time,
			'client_id': self.client_id,
			'is_valid': self.is_valid,
			'client_secret': self.client_secret,
			}


	def serialize(self):
		return {
			'member_id': self.member_id,
			'created_time': self.created_time,
			'client_id': self.client_id,
			'is_valid': self.is_valid,
			'permission_level': self.permission_level,
			'member_kind' : 'api'
			}
