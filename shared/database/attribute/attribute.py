from shared.database.common import *


class Attribute(Base):
	"""

	WIP WIP WIP Attribute

	"""

	__tablename__ = 'attribute'
	id = Column(BIGINT, primary_key = True)

	archived = Column(Boolean, default = False)		# Hide from list

	template_id = Column(Integer, ForeignKey('attribute_template.id'))
	template = relationship("Attribute_Template", foreign_keys=[template_id])

	instance_id = Column(Integer, ForeignKey('instance.id'))
	instance = relationship(	"Instance", foreign_keys=[instance_id])

	# Question do we want to cache the group here too?

	# Optional
	value = Column(String())

	member_created_id = Column(Integer, ForeignKey('member.id'))
	member_created = relationship("Member", foreign_keys=[member_created_id])

	member_updated_id = Column(Integer, ForeignKey('member.id'))
	member_updated = relationship("Member", foreign_keys=[member_updated_id])

	time_created = Column(DateTime, default=datetime.datetime.utcnow)
	time_updated = Column(DateTime, onupdate=datetime.datetime.utcnow)

	# TODO add other properties from Action class



	# WIP WIP WIP
	@staticmethod
	def new(
			session,
			project,
			kind,
			org,
			member,
			template):
		"""
		"""

		if group is None:
			return False

		attribute = Attribute(
			project = project,
			org = org,
			member_created = member,
			template = template
			)

		return attribute