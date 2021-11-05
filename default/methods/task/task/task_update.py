# OPENCORE - ADD
from methods.regular.regular_api import *
from shared.database.task.task import Task
from shared.utils.task.task_new import create_review_sub_task
from shared.database.task.task_event import TaskEvent

@routes.route('/api/v1/task/update',
              methods = ['POST'])
@limiter.limit("1 per second, 50 per minute, 500 per day")
def task_update_api():
    """

    """
    spec_list = [
        {'task_id': {
            'kind': int,
            'permission': 'task'
        }
        },
        {'task_ids': {
            'kind': list,
            'permission': 'task',
            'required': False
        }
        },
        {'mode': {
            'kind': str,
            'valid_values_list': ['toggle_deferred']
        }
        },
        {'status': {
            'kind': str,
            'valid_values_list': ['archived']
        }
        }
    ]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        task_list = []
        if input['task_id']:
            task = Task.get_by_id(session = session,
                                  task_id = input['task_id'])
            task_list.append(task)
        else:
            task_list = Task.list(
                session = session,
                task_ids = input['task_ids']
            )
        for task in task_list:
            Permission_Task.by_task_id_core(task.id)
            task_update = Task_Update(
                session = session,
                task = task,
                mode = input['mode'],
                status = input['status'])

            task_update.main()

        if len(task_update.log["error"].keys()) >= 1:
            return jsonify(log = task_update.log), 400

        return jsonify(log = task_update.log), 200


@dataclass
class Task_Update():
    session: Any
    task: Task
    mode: str = None
    status: str = None

    """
    This is clearly over burdening for setting flag,
    but the point is more that we want to expand along this axis as
    other types of task update stuff get added.

    """

    def __post_init__(self):

        self.session.add(self.task)
        self.try_to_commit = regular_methods.try_to_commit

        # TODO clarify if this needs to use factory thing
        self.log = regular_log.default()

    def main(self):
        old_status = self.task.status
        if self.mode == 'toggle_deferred':
            self.defer()
        if self.status and self.status != 'complete':  # We don't allow to completed tasks here, use task_complete.
            self.change_status()
        regular_methods.try_to_commit(self)
        self.emit_task_event_based_on_status(old_status, self.task)
        self.task.job.refresh_stat_count_tasks(self.session)
        return

    def emit_task_event_based_on_status(self, old_status, task):
        if task.status == 'complete':
            if old_status != 'completed':
                TaskEvent.generate_task_creation_event(self .session, task)
        if task.status == 'in_progress':
            if old_status != 'in_progress':
                TaskEvent.generate_task_in_progress_event(self.session, task)
        if task.status == 'in_review':
            if old_status != 'in_review':
                TaskEvent.generate_task_review_start_event(self.session, task)
        if task.status == 'in_progress':
            if old_status == 'in_review':
                TaskEvent.gene(self.session, task)

    def change_status(self):
        if self.task.status != 'archived' and self.status == 'archived':
            self.task.job.stat_count_tasks -= 1
            self.session.add(self.task.job)

        self.task.status = self.status

    def defer(self):

        # Don't defer twice
        if self.task.status == 'deferred':
            self.log['error']['deferred'] = "Task has already been deferred."
            return

        # Future feature? in theory could defer again...
        # note this is task_type not Status
        if self.task.task_type == 'review':
            self.log['error']['deferred'] = "Review tasks cannot be deferred"
            return

        self.task.status = 'deferred'

        review_task = create_review_sub_task(
            session = self.session,
            job = self.task.job,
            root_task = self.task,
            guide_id = self.task.job.guide_review_id,
            create_new_file = False
        )

        self.log['success'] = True
