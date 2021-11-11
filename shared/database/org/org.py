from shared.database.common import *
from shared.database.org.org_to_user import Org_To_User


class Org(Base):
	"""
	Orginization


	An Org can have multiple
	 projects
	 users
	 billing account?

	"""
	__tablename__ = 'org'
	id = Column(Integer, primary_key = True)

	security_disable = Column(Boolean)

	verified_by_diffgram = Column(Boolean)

	name = Column(String)

	api_address_valid = Column(Boolean)
	api_trainer_org = Column(Boolean)

	address_primary_id = Column(Integer, ForeignKey('address.id'))
	address_primary = relationship('Address', 
										foreign_keys=[address_primary_id])

	# TODO "address" history

	primary_user_id = Column(Integer, ForeignKey('userbase.id'))
	primary_user = relationship('User', 
								foreign_keys=[primary_user_id])



	# An API method for example could create an org
	member_created_id = Column(Integer, ForeignKey('member.id')) 
	member_created = relationship("Member", foreign_keys=[member_created_id])

	member_updated_id = Column(Integer, ForeignKey('member.id'))
	member_updated = relationship("Member", foreign_keys=[member_updated_id])

	time_created = Column(DateTime, default=datetime.datetime.utcnow)
	time_updated = Column(DateTime, onupdate=datetime.datetime.utcnow)
	
	remote_address_created = Column(String())




	def serialize(self):

		org = {
			'id' : self.id,
			'name' : self.name
		}
		return org


	def get_by_id(session, 
				  org_id):

		if org_id is None:
			return False

		return session.query(Org).filter(
					Org.id == org_id).first()


	def user_to_org_list(
			session,
			org_id):


		query = session.query(Org_To_User)

		query = query.filter(
					Org_To_User.org_id == org_id)


		return query.all()