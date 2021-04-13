# OPENCORE - ADD
from shared.database.common import *


# Mainly for a label file / in that context

class Attribute_Template_Group_to_File(Base):

	__tablename__ = 'attribute_template_group_to_file'

	"""

	Context of groups to label files for the TEMPLATING not the storage
	
	
	"""

	attribute_template_group_id = Column(Integer, ForeignKey('attribute_template_group.id'), primary_key=True)
	attribute_template_group = relationship("Attribute_Template_Group")
	
	file_id = Column(Integer, ForeignKey('file.id'), primary_key=True)
	file = relationship("File")



	def get(session, group_id, file_id):

		result = session.query(Attribute_Template_Group_to_File).filter(
			Attribute_Template_Group_to_File.attribute_template_group_id == group_id,
			Attribute_Template_Group_to_File.file_id == file_id).first()

		return result


	def get_all_from_group(session, group_id):

		query = session.query(Attribute_Template_Group_to_File).filter(
			Attribute_Template_Group_to_File.attribute_template_group_id == group_id)

		return query.all()


	def set(session, group_id, file_id):

		result = Attribute_Template_Group_to_File(
			attribute_template_group_id = group_id,
			file_id = file_id)

		return result