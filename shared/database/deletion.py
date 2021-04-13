# OPENCORE - ADD
from shared.database.common import *



class Deletion(Base):
	"""
	
	Track deletion process for long running operations

	Initially used for projects

	Can see it being user for other stuff in future

	Could also be useful for "hard deleting" stuff
	and having a record of that...


	"""
	__tablename__ = 'deletion'
	id = Column(Integer, primary_key = True)

	notes = Column(String)

	mode = Column(String)		# ie "remove_project_permission"

	cache =  Column(MutableDict.as_mutable(JSONEncodedDict), 
						 default = {})

	project_id = Column(Integer, ForeignKey('project.id'))
	project = relationship('Project', foreign_keys=[project_id])

	member_created_id = Column(Integer, ForeignKey('member.id')) 
	member_created = relationship("Member", foreign_keys=[member_created_id])

	member_updated_id = Column(Integer, ForeignKey('member.id'))
	member_updated = relationship("Member", foreign_keys=[member_updated_id])

	time_created = Column(DateTime, default=datetime.datetime.utcnow)
	time_updated = Column(DateTime, onupdate=datetime.datetime.utcnow)
