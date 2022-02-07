from shared.database.report.report_template import ReportTemplate
from shared.database.task.task_time_tracking import TaskTimeTracking
from sqlalchemy.orm.session import Session
from sqlalchemy import func


class TimeSpentReport:
    report_template: ReportTemplate
    session: Session

    def __init__(self, report_template: ReportTemplate, session: Session):
        self.report_template = report_template
        self.session = session

    def run(self):
        query = self.session.query(TaskTimeTracking) \
            .with_entities(TaskTimeTracking.task_id, func.avg(TaskTimeTracking.time_spent),
                           func.count(TaskTimeTracking.user_id)) \
            .filter(TaskTimeTracking.project_id == self.report_template.project_id
                    )
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

        query = query.group_by('task_id')
        data = query.all()
        result = {
            'count': len(data),
            'labels': [],
            'values': [],
            'values_metadata': [],
            'header_name': 'Time Spent (Minutes)',
        }
        for elm in data:
            result['labels'].append(elm[0])
            result['values'].append(round(elm[1] / 60.0, 2))  # To Minutes
            result['values_metadata'].append({'num_users': elm[2]})

        return result
