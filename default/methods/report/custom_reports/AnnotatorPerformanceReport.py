from shared.database.report.report_template import ReportTemplate
from shared.database.task.task_time_tracking import TaskTimeTracking
from sqlalchemy.orm.session import Session
from sqlalchemy import func
from shared.database.user import User

class AnnotatorPerformanceReport:
    report_template: ReportTemplate
    session: Session

    def __init__(self, report_template: ReportTemplate, session: Session):
        self.report_template = report_template
        self.session = session

    def run(self):
        query = self.session.query(TaskTimeTracking) \
            .with_entities(TaskTimeTracking.user_id,
                           func.avg(TaskTimeTracking.time_spent)) \
            .filter(TaskTimeTracking.project_id == self.report_template.project_id,
                    TaskTimeTracking.status.is_(None))
        if self.report_template.job_id:
            query = query.filter(
                TaskTimeTracking.job_id == self.report_template.job_id
            )
        if self.report_template.member_list:
            query = query.filter(
                TaskTimeTracking.user_id.in_(self.report_template.member_list)
            )
        if self.report_template.task_id:
            query = query.filter(
                TaskTimeTracking.task_id == self.report_template.task_id
            )

        query = query.group_by('user_id')
        data = query.all()
        result = {
            'count': len(data),
            'labels': [],
            'values': [],
            'values_metadata': [],
            'header_name': 'Annotator Task Time (Minutes)',
        }
        for elm in data:
            result['labels'].append(elm[0])
            result['values'].append(round(elm[1] / 60.0, 2))  # To Minutes
        users = self.session.query(User).filter(
            User.id.in_(result['labels'])
        ).all()
        user_dict = {}
        for u in users:
            user_dict[u.id] = u
        for elm in data:
            result['values_metadata'].append({'email': user_dict[elm[0]].email,
                                              'first_name': user_dict[elm[0]].first_name,
                                              'last_name': user_dict[elm[0]].last_name
                                              })

        return result
