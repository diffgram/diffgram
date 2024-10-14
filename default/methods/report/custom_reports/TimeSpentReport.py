from shared.database.report.report_template import ReportTemplate  # Importing ReportTemplate class
from shared.database.task.task_time_tracking import TaskTimeTracking  # Importing TaskTimeTracking class
from sqlalchemy.orm.session import Session  # Importing Session class
from sqlalchemy import func  # Importing func for aggregate functions

class TimeSpentReport:
    # Class representing TimeSpentReport
    report_template: ReportTemplate  # Instance variable to hold ReportTemplate object
    session: Session  # Instance variable to hold Session object

    def __init__(self, report_template: ReportTemplate, session: Session):
        # Constructor to initialize TimeSpentReport object
        self.report_template = report_template  # Assigning ReportTemplate object
        self.session = session  # Assigning Session object

    def run(self):
        # Method to execute the TimeSpentReport query
        query = self.session.query(TaskTimeTracking) \
            .with_entities(TaskTimeTracking.task_id, func.avg(TaskTimeTracking.time_spent),  # Selecting required columns
                           func.count(TaskTimeTracking.user_id)) \
            .filter(TaskTimeTracking.project_id == self.report_template.project_id,  # Filtering by project_id
                    TaskTimeTracking.status.is_(None))  # Filtering by status (None)

        if self.report_template.job_id:
            # If job_id is present in ReportTemplate object, filter by job_id
            query = query.filter(
                TaskTimeTracking.job_id == self.report_template.job_id
            )

        if self.report_template.member_list:
            # If member_list is present in ReportTemplate object, filter by user_id in member_list
            query = query.filter(
                TaskTimeTracking.user_id.in_(self.report_template.member_list)
            )

        if self.report_template.task_id:
            # If task_id is present in ReportTemplate object, filter by task_id
            query = query.filter(
                TaskTimeTracking.task_id == self.report_template.task_id
            )

        query = query.group_by('task_id')  # Grouping by task_id
        data = query.all()  # Executing the query

        result = {
            'count': len(data),  # Number of records
            'labels': [],  # Labels for the chart
            'values': [],  # Values for the chart
            'values_metadata': [],  # Metadata for the values
            'header_name': 'Time Spent (Minutes)',  # Header name for the chart
        }

        for elm in data:
            # Preparing the result data
            result['labels'].append(elm[0])
            result['values'].append(round(elm[1] / 60.0, 2))  # Converting time_spent from seconds to minutes
            result['values_metadata'].append({'num_users': elm[2]})  # Number of users

        return result  # Returning the result
