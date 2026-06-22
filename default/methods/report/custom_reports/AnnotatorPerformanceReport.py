from shared.database.report.report_template import ReportTemplate
from shared.database.task.task_time_tracking import TaskTimeTracking
from sqlalchemy.orm.session import Session
from sqlalchemy import func
from shared.database.user import User

class AnnotatorPerformanceReport:
    # Initialize the report with a report template and a session
    def __init__(self, report_template: ReportTemplate, session: Session):
        self.report_template = report_template
        self.session = session

    def run(self):
        # Query for the user IDs and average time spent on tasks
        query = self.session.query(TaskTimeTracking) \
            .with_entities(TaskTimeTracking.user_id,
                           func.avg(TaskTimeTracking.time_spent))

        # Filter the query based on the report template
        query = query.filter(TaskTimeTracking.project_id == self.report_template.project_id,
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

        # Group the query by user ID
        query = query.group_by('user_id')

        # Execute the query and store the results
        data = query.all()

        # Initialize the result dictionary
        result = {
            'count': len(data),
            'labels': [],
            'values': [],
            'header_name': 'Annotator Task Time (Minutes)',
        }

        # Iterate over the data and populate the result dictionary
        for elm in data:
            result['labels'].append(elm[0])
            result['values'].append(round(elm[1] / 60.0, 2))  # Convert to minutes

        # Return the result dictionary
        return result
