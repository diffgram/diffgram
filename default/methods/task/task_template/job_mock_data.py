# OPENCORE - ADD
# Mock spec for sending instance data to save function.


"""
 mock pseduo code starter

 For each task in job
 TODO Get task id
 TODO Call test_task_annotation_update()
	With and_complete set to True

"""

from methods.annotation.annotation_mock import mock_task_annotation_update



def mock_run_all_tasks_in_job(
		job,
		session):


	# could also use task_list.task_list_core() if want more control

	for task in job.task_list(session = session):

		mock_task_annotation_update(
			session = session,
			task = task,
			and_complete = True)

		# How are we actually handling errors / exceptions here...


	return True
