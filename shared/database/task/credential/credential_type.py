from shared.database.common import *


class Credential_Type(Base):
	"""
	


	"""
	__tablename__ = 'credential_type'
	id = Column(Integer, primary_key = True)

	name = Column(String())
	description_markdown = Column(String())

	project_id = Column(Integer, ForeignKey('project.id'))
	project = relationship('Project')

	# New Oct 15, 2019
	archived = Column(Boolean, default = False)		# Hide from list

	history_cache =  deferred(Column(MutableDict.as_mutable(JSONEncodedDict), 
							default = {}))

	# TODO future visibilty options for credentials, ie viewable outside
	# of project scope etc. Maybe even an "is public bool" or something
	public = Column(Boolean)

	# icon / image
	image_id = Column(Integer, ForeignKey('image.id'))		# new feb 12 2019
	image = relationship("Image")

	member_created_id = Column(Integer, ForeignKey('member.id')) 
	member_created = relationship("Member", foreign_keys=[member_created_id])

	member_updated_id = Column(Integer, ForeignKey('member.id'))
	member_updated = relationship("Member", foreign_keys=[member_updated_id])

	time_created = Column(DateTime, default=datetime.datetime.utcnow)
	time_updated = Column(DateTime, onupdate=datetime.datetime.utcnow)


	def new(
			member_created  = None,
			name  = None,
			project  = None,
			description_markdown = None
		):

		# TODO need some way to signify "Diffgram wide"
		# eg for generic ID stuff

		credential_type = Credential_Type(
					member_created = member_created,
					name = name,
					project = project,
					description_markdown = description_markdown)

		return credential_type


	def get_or_new(
			name,
			session,
			add_and_flush = True):
		"""
		example context of generic Diffgram wide things like
		Gov ID
		"""

		credential_type = Credential_Type.get_by_name(
			name = name,
			session = session
			)

		if credential_type is None:
			credential_type = Credential_Type.new(
				name = name)

			if add_and_flush is True:
				session.add(credential_type)
				session.flush()

		return credential_type


	def get_by_name(
			name,
			session
		):

		return session.query(Credential_Type).filter(
			Credential_Type.name == name).first()


	def serialize_for_list_view(self):

		image = None
		if self.image:
			image = self.image.serialize()

		return {
			'id': self.id,
			'name': self.name,
			'description_markdown': self.description_markdown,
			'image': image
			
		}

	def get_by_id(session, credential_type_id):
		if credential_type_id is None:
			return False

		return session.query(Credential_Type).filter(
					Credential_Type.id == credential_type_id).first()
