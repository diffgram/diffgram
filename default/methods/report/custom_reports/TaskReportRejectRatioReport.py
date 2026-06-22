from shared.database.report.report_template import ReportTemplate
from shared.database.task.task_event import TaskEvent
from sqlalchemy.orm.session import Session
from sqlalchemy import func, and_
from shared.database.user import User
from typing import List, Dict, Tuple

class TaskReportRejectRatioReport:
    """
    A class for generating a task report with reject ratio.
    """
    report_template: ReportTemplate
    session: Session

    def __init__(self, report_template: ReportTemplate, session: Session):
        self.validate_report_template(report_template)
        self.report_template = report_template
        self.session = session

    def validate_report_template(self, report_template: ReportTemplate):
        """
        Validate the report_template attributes.
        """
        required_attributes = ['project_id']
        for attr in required_attributes:
            if getattr(report_template, attr) is None:
                raise ValueError(f"Report template missing required attribute: {attr}")

    def run(self) -> Dict[str, List[Union[str, int, Dict[str, str]]]]:
        """
        Generate the task report with reject ratio.
        """
        query = self.session.query(TaskEvent.user_assignee_id, func.count(TaskEvent.id)) \
            .filter(and_(TaskEvent.project_id == self.report_template.project_id,
                         TaskEvent.event_type.in_(['task_completed', 'task_request_changes'])))

        if self.report_template.job_id:
            query = query.filter(TaskEvent.job_id == self.report_template.job_id)

        if self.report_template.member_list:
            query = query.filter(TaskEvent.user_assignee_id.in_(self.report_template.member_list))

        if self.report_template.task_id:
            query = query.filter(TaskEvent.task_id == self.report_template.task_id)

        query = query.group_by('user_assignee_id').order_by('user_assignee_id')
        data = query.all()

        completed_tasks, rejected_tasks = self.separate_tasks(data)
        result = self.generate_result(completed_tasks, rejected_tasks)

        return result

    def separate_tasks(self, data: List[Tuple[int, int]]) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
        """
        Separate completed and rejected tasks.
        """
        completed_tasks = [task for task in data if task[1] > 0 and task[0] != -1]
        rejected_tasks = [task for task in data if task[1] > 0 and task[0] == -1]

        return completed_tasks, rejected_tasks

    def generate_result(self, completed_tasks: List[Tuple[int, int]], rejected_tasks: List[Tuple[int, int]]) -> Dict[str, List[Union[str, int, Dict[str, str]]]]:
        """
        Generate the final result.
        """
        result = {
            'count': len(completed_tasks),
            'labels': [],
            'values_completed': [],
            'values_rejected': [],
            'values_metadata': [],
            'header_name': 'Tasks Completed / Changes Requested',
        }

        for i in range(0, len(completed_tasks)):
            result['labels'].append(completed_tasks[i][0])
            result['values_completed'].append(completed_tasks[i][1])

        if len(completed_tasks) == len(rejected_tasks):
            for i in range(0, len(rejected_tasks)):
                result['values_rejected'].append(rejected_tasks[i][1])
        else:
            raise Exception("Data inconsistency: completed_tasks and rejected_tasks have different lengths.")

        users = self.session.query(User).filter(
            User.id.in_(result['labels'])
        ).all()

        user_dict = {u.id: {'email': u.email, 'first_name': u.first_name, 'last_name': u.last_name} for u in users}

        for elm in completed_tasks:
            result['values_metadata'].append(user_dict[elm[0]])

        return result
