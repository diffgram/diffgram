# OPENCORE - ADD
from shared.database.common import *


class ReportDashboard(Base):
	__tablename__ = 'report_dashboard'

	"""
	Assumes 1 of :
		diffgram_wide_default, project, org...




	"""

	id = Column(Integer, primary_key=True)

	diffgram_wide_default = Column(Boolean, default = False)

	project_id = Column(Integer, ForeignKey('project.id'))
	project = relationship("Project", foreign_keys=[project_id])

	name = Column(String())
	archived = Column(Boolean, default = False)

	member_created_id = Column(Integer, ForeignKey('member.id')) 
	member_created = relationship("Member", foreign_keys=[member_created_id])

	member_updated_id = Column(Integer, ForeignKey('member.id'))
	member_updated = relationship("Member", foreign_keys=[member_updated_id])

	time_created = Column(DateTime, default=datetime.datetime.utcnow)
	time_updated = Column(DateTime, onupdate=datetime.datetime.utcnow)


	@staticmethod
	def new(project_id: int):
		"""

		April 15, 2020
			Main assumption for now is that a project will
			have one dashboard. This is a thing for future expansions
			and to support the "multiple views" thing so 
			one report can have different views.

		The assumption is that each project has it's own dashboard
		so that edits can flow nicely, not quite clear how dashboard maintains
		a "default reports" list, or if that's handled through a separate process.

		"""


		dashboard = ReportDashboard(
			project_id = project_id)

		return dashboard




	# for list, see ReportTemplate.list() and pass dashboard id