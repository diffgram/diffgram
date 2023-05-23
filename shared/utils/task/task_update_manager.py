from shared.database.task.task import Task, TASK_STATUSES
from shared.database.task.task_event import TaskEvent
from shared.regular import regular_methods, regular_log
from dataclasses import dataclass
from shared.database.source_control.working_dir import WorkingDirFileLink


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
        if self.mode == 'incomplete':
            self.status = 'in_progress'
            self.change_status()
        if self.status:
            self.change_status()
        regular_methods.try_to_commit(self)
        self.emit_task_event_based_on_status(old_status, self.task)
        self.update_related_file_status(old_status, self.task)
        self.task.job.refresh_stat_count_tasks(self.session)
        return

    def update_related_file_status(self, old_status, updated_task: Task):
        if updated_task.status == 'complete':
            # Find All Other Tasks from the related file
            other_pending_tasks = Task.get_related_pending_tasks(session = self.session,
                                                                 task = updated_task)
            if len(other_pending_tasks) == 0:
                updated_task.file.ann_is_complete = True

            else:
                updated_task.file.ann_is_complete = False
        else:
            updated_task.file.ann_is_complete = False
        self.session.add(updated_task.file)

    def emit_task_event_based_on_status(self, old_status, task):
        if task.status == 'complete':
            if old_status != 'completed':
                assignees = task.get_assignees(session = self.session)
                if old_status == 'in_review':
                    TaskEvent.generate_task_review_complete_event(self.session, task, self.member)
                for user in assignees:
                    TaskEvent.generate_task_completion_event(self.session, task, self.member, task_assignee = user)
                if not assignees:
                    TaskEvent.generate_task_completion_event(self.session, task, self.member,
                                                             task_assignee = self.member.user)

        if task.status == 'in_progress':
            if old_status != 'in_progress':
                TaskEvent.generate_task_in_progress_event(self.session, task, self.member)
        if task.status == 'review_requested':
            if old_status != 'review_requested':
                TaskEvent.generate_task_review_start_event(self.session, task, self.member)
        if task.status == 'requires_changes':
            if old_status != 'requires_changes':
                assignees = task.get_assignees(session = self.session)
                for user in assignees:
                    TaskEvent.generate_task_request_change_event(self.session, task, self.member, task_assignee = user)
                if not assignees:
                    TaskEvent.generate_task_request_change_event(self.session, task, self.member)

    def update_files_count(self):
        result, log = WorkingDirFileLink.file_link_update(
            session = self.session,
            add_or_remove = 'remove',
            directory = self.task.job.directory,
            job = self.task.job,
            incoming_directory = self.task.job.directory,
            file_id = self.task.file_id,
            log = self.log
        )
        if regular_log.log_has_error(log):
            self.log['error']['file_link_update'] = "error file_link_update"
            return
        self.task.job.update_file_count_statistic(session = self.session)

    def change_status(self):
        if self.task.status != 'archived' and self.status == 'archived':
            self.task.job.stat_count_tasks -= 1
            self.session.add(self.task.job)

        self.task.status = self.status
        if self.status == 'archived':
            self.update_files_count()
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

        self.log['success'] = True
