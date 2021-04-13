# OPENCORE - ADD
from shared.database.common import *


class Report(Base):
	__tablename__ = 'report'

	"""

	Instance of a ReportTemplate
	Generated / saved for historical review

	See ReportTemplate for more general thing
		
	"""

	id = Column(Integer, primary_key=True)

	report_template_id = Column(Integer, ForeignKey('report_template.id'))
	report_template = relationship("ReportTemplate", foreign_keys=[report_template_id])

	# These are dates actually ran
	datetime_from = Column(DateTime)
	datetime_to = Column(DateTime)

	# Previous period?



	# WIP WIP WIP
	def serialize(self):

		return {
			'id' : self.id,

			# note datetime not date
			'datetime_from': self.datetime_from,
			'datetime_to' : self.datetime_to
			}