# OPENCORE - ADD
from shared.database.common import *


class Comment(Base):
	"""
	

	"""
	__tablename__ = 'comment'

	id = Column(Integer, primary_key = True)
	created_time = Column(DateTime, default = datetime.datetime.utcnow)

	user_id = Column(Integer, ForeignKey('userbase.id'))
	user = relationship("User")

	type = Column(String)  # ie task, issue, contract? other... or could comment on a report...

	discussion_id = Column(Integer, ForeignKey('discussion.id'))
	discussion = relationship("Discussion", foreign_key = [discussion_id])
	
	task_id = Column(Integer, ForeignKey('task.id'))
	task = relationship("Task")

	# Markdown format?
	content = Column(String())
	
	# Add reaction?

	def get_by_id(session, id):    
		return session.query(Comment).filter(Comment.id == id).first()

	def serialize(self):
		return {
			'id' : self.id,
			'user' : self.user.serialize_for_activity(),
			'discussion_id' : self.discussion_id,
			'content' : self.content
		}