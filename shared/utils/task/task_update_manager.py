from shared.database.task.task import Task, TASK_STATUSES
from shared.utils.task.task_new import create_review_sub_task
from shared.database.task.task_event import TaskEvent
from shared.regular import regular_methods, regular_log
from dataclasses import dataclass

@dataclass
class Task_Update():
    session: any
    task: Task
    mode: str = None
    status: str = None
    member: 'Member' = None

    """
        Controls the changing of the task status and generation of the appropriate events depending
        on the status.

        Notes:
            - For completing a task use task_complete() function in task.py. that function uses this class eventually.

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
        if self.status:
            self.change_status()
        regular_methods.try_to_commit(self)
        self.emit_task_event_based_on_status(old_status, self.task)
        self.task.job.refresh_stat_count_tasks(self.session)
        return

    def emit_task_event_based_on_status(self, old_status, task):
        if task.status == 'complete':
            if old_status != 'completed':
                TaskEvent.generate_task_completion_event(self.session, task, self.member)
        if task.status == 'in_progress':
            if old_status != 'in_progress':
                TaskEvent.generate_task_in_progress_event(self.session, task, self.member)
        if task.status == 'in_review':
            if old_status != 'in_review':
                TaskEvent.generate_task_review_start_event(self.session, task, self.member)
        if task.status == 'requires_changes':
            if old_status != 'requires_changes':
                TaskEvent.generate_task_request_change_event(self.session, task, self.member)

    def change_status(self):
        if self.task.status != 'archived' and self.status == 'archived':
            self.task.job.stat_count_tasks -= 1
            self.session.add(self.task.job)

        self.task.status = self.status
        self.session.add(self.task)

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

        self.task.status = TASK_STATUSES['deferred']

        review_task = create_review_sub_task(
            session = self.session,
            job = self.task.job,
            root_task = self.task,
            guide_id = self.task.job.guide_review_id,
            create_new_file = False
        )

        self.log['success'] = True
