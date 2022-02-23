from shared.database.report.report_template import ReportTemplate
from shared.database.task.task_event import TaskEvent
from sqlalchemy.orm.session import Session
from sqlalchemy import func
from shared.database.user import User


class TaskReportRejectRatioReport:
    report_template: ReportTemplate
    session: Session

    def __init__(self, report_template: ReportTemplate, session: Session):
        self.report_template = report_template
        self.session = session

    def run(self):
        query_completed = self.session.query(TaskEvent) \
            .with_entities(TaskEvent.user_assignee_id, func.count(TaskEvent.id)) \
            .filter(TaskEvent.project_id == self.report_template.project_id,
                    TaskEvent.event_type == 'task_completed')

        query_rejected = self.session.query(TaskEvent) \
            .with_entities(TaskEvent.user_assignee_id, func.count(TaskEvent.id)) \
            .filter(TaskEvent.project_id == self.report_template.project_id,
                    TaskEvent.event_type == 'task_request_changes')

        if self.report_template.job_id:
            query_completed = query_completed.filter(
                TaskEvent.job_id == self.report_template.job_id
            )
            query_rejected = query_rejected.filter(
                TaskEvent.job_id == self.report_template.job_id
            )
        if self.report_template.member_list:
            query_completed = query_completed.filter(
                TaskEvent.user_assignee_id.in_(self.report_template.member_list)
            )
            query_rejected = query_rejected.filter(
                TaskEvent.job_id == self.report_template.job_id
            )
        if self.report_template.task_id:
            query_completed = query_completed.filter(
                TaskEvent.task_id == self.report_template.task_id
            )
            query_rejected = query_rejected.filter(
                TaskEvent.job_id == self.report_template.job_id
            )

        query_completed = query_completed.group_by('user_assignee_id').order_by('user_assignee_id')
        query_rejected = query_rejected.group_by('user_assignee_id').order_by('user_assignee_id')
        data_completed = query_completed.all()
        data_rejected = query_rejected.all()
        result = {
            'count': len(data_completed),
            'labels': [],
            'values_completed': [],
            'values_rejected': [],
            'values_metadata': [],
            'header_name': 'Tasks Completed / Changes Requested',
        }
        for i in range(0, len(data_completed)):
            print(i)
            print('aaa', data_completed[i], data_completed)
            print('aaa', data_rejected[i], data_rejected)
            result['labels'].append(data_completed[i][0])
            result['values_completed'].append(data_completed[i][1])
            result['values_rejected'].append(data_rejected[i][1])

        users = self.session.query(User).filter(
            User.id.in_(result['labels'])
        ).all()
        user_dict = {}
        for u in users:
            user_dict[u.id] = u
        for elm in data_completed:
            result['values_metadata'].append({'email': user_dict[elm[0]].email,
                                              'first_name': user_dict[elm[0]].first_name,
                                              'last_name': user_dict[elm[0]].last_name
                                              })
        return result
