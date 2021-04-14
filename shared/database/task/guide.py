# OPENCORE - ADD
from shared.database.common import *



class Guide(Base):
	"""
	
	A guide can be assigned a type

	A task can have 1? guide?

	A contract can have multiple guides

	Good guides can be shared

	Concept that a user may create and is likely to re use guides

	And likely to update over time

	"""
	__tablename__ = 'guide'
	id = Column(Integer, primary_key = True)

	is_visible = Column(Boolean, default = True)  # Seperate "is draft" thing here or...

	archived = Column(Boolean, default = False)		# Hide from list

	# Type 
	# (ie what tasks is this for? does that matter?)
	# The task may care what guide it has but the guide doesn't right
	# Or maybe it should have it...

	# Maybe tags instead?

	name = Column(String())
	description_markdown = Column(String())

	# samples (cached and/or link diretly to file?)
	# other types of attachements? ?? files?

	# Deferred as this could grow to be quite large.
	history_cache =  deferred(Column(MutableDict.as_mutable(JSONEncodedDict), 
							default = {}))

	# attached to projects for permissions???
	# I guess if sharing guides between projects maybe future thing?
	project_id = Column(Integer, ForeignKey('project.id'))
	project = relationship('Project')

	member_created_id = Column(Integer, ForeignKey('member.id')) 
	member_created = relationship("Member", foreign_keys=[member_created_id])

	member_updated_id = Column(Integer, ForeignKey('member.id'))
	member_updated = relationship("Member", foreign_keys=[member_updated_id])

	time_created = Column(DateTime, default=datetime.datetime.utcnow)
	time_updated = Column(DateTime, onupdate=datetime.datetime.utcnow)


	def serialize(self):

		return {
			'name' : self.name,
			'markdown' : self.description_markdown,
			'time_updated' : self.time_updated
			}

	def serialize_for_trainer(self):

		return {
			'name' : self.name,
			'markdown' : self.description_markdown,
			'time_updated' : self.time_updated
			}

	def serialize_for_list_view(self):

		return {
			'id': self.id,
			'name': self.name,
			'description_markdown': self.description_markdown, 
			# For now include markdown because we want to be able to edit
			# and it doesn't realy seem heavy enough to justify a seperate call yet
			'time_updated' : self.time_updated
			
		}
	
	def get_by_id(session, guide_id):
		if guide_id is None:
			return None

		return session.query(Guide).filter(
					Guide.id == guide_id).first()