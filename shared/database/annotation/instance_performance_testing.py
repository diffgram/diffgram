# OPENCORE - ADD
from default.methods.regular.regular_api import *
from shared import database_setup_supporting	
from shared.helpers.performance import explain_postgres
from shared.database.video.sequence import Sequence

# new session to "keep it clean"

def primary_key():
	with sessionMaker.session_scope() as session:
		with profiled():
			instance = session.query(Instance).filter(
				Instance.id == 1004176).first()


def foreign_key():
	with sessionMaker.session_scope() as session:
		with profiled():
			instance = session.query(Instance).filter(
				Instance.video_parent_file_id == 1004176).first()


def multi_condition():
	with sessionMaker.session_scope() as session:
		with profiled():
			instance = session.query(Instance).filter(
					Instance.video_parent_file_id == 1004176,
					Instance.frame_number == 1223).first()


def explain_single_sequence_id(file_id):
	with sessionMaker.session_scope() as session:
		query = session.query(Sequence).filter(
				Sequence.video_file_id == file_id)
		explain_results = session.execute(explain_postgres(query)).first()
		print(explain_results)


def explain_single_file_id(file_id):
	with sessionMaker.session_scope() as session:
		query = session.query(Instance).filter(
				Instance.file_id == file_id)
		explain_results = session.execute(explain_postgres(query)).first()
		print(explain_results)




def explain_many():
	with sessionMaker.session_scope() as session:
		primary_key = session.query(Instance).filter(Instance.id == 1004176)
		foreign_key = session.query(Instance).filter(
						Instance.video_parent_file_id == 1004176)
		multi_condition = session.query(Instance).filter(
						Instance.video_parent_file_id == 1004176,
						Instance.frame_number == 1223)
		run_with_explain(session, primary_key)
		run_with_explain(session, foreign_key)
		run_with_explain(session, multi_condition)


def run_with_explain(session, query):
	explain_results = session.execute(explain_postgres(query)).first()
	print(explain_results)


#primary_key()
#foreign_key()
#multi_condition()

single_instance = 1164186
explain_single_sequence_id(single_instance)

single_instance = 1164186
explain_single_file_id(single_instance)

many_instances_on_frame = 1164509
explain_single_file_id(many_instances_on_frame)

#explain_many()
