# OPENCORE - ADD
from shared.database.common import *
from shared.communicate.email import communicate_via_email
from shared.database.notifications.notification_relation import NotificationRelation
from shared.database.task.task import Task
from shared.database.source_control.file import File
from shared.database.input import Input
from shared.database.task.job.job import Job
import hmac
import hashlib
import json
import requests
import codecs
from shared.shared_logger import get_shared_logger

logger = get_shared_logger()


class Notification(Base):
    """
        Base data table for notification.
    """

    __tablename__ = 'notification'
    id = Column(Integer, primary_key=True)

    status = Column(String(), default="sent")

    channel_type = Column(String(), default='email')

    type = Column(String(), default='default')

    title = Column(String(), default='')

    description = Column(String(), default='')

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys=[member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys=[member_updated_id])

    # Default
    notification_relation_id = Column(Integer, ForeignKey('notification_relation.id'))
    notification_relation = relationship("NotificationRelation", foreign_keys=[notification_relation_id])

    time_created = Column(DateTime, default=datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate=datetime.datetime.utcnow)

    def serialize_for_list_view(self, session):

        return {
            'id': self.id,
            'status': self.status,
            'title': self.title,
            'description': self.description,
            'time_created': self.time_created,
            'time_completed': self.time_completed,
            'member_created_id': self.member_created_id,
        }

    def __generate_payload_for_task(self, session, start_time=None):
        tasks = []
        task = Task.get_by_id(session=session, task_id=self.notification_relation.task_id)
        if task:
            tasks.append(task)
        time_column = Task.time_created
        if self.type == 'task_completed':
            time_column = Task.time_completed
        if start_time:
            tasks = session.query(Task).filter(Task.project_id == self.notification_relation.task.project_id,
                                               time_column <= datetime.datetime.utcnow(),
                                               time_column >= start_time).all()
        payload = [task.serialize_builder_view_by_id(session=session) for task in tasks]
        return payload

    def __generate_payload_for_file(self, session, start_time=None):
        files = [File.get_by_id(session=session, file_id=self.notification_relation.input.file_id)]
        if start_time:
            files = session.query(File).filter(File.project_id == self.notification_relation.input.project_id,
                                               File.created_time <= datetime.datetime.utcnow(),
                                               File.created_time >= start_time).all()

        payload = [file.serialize_with_annotations(session=session) for file in files]
        return payload

    def __generate_payload_for_task_template(self, session, start_time=None):
        task_template = Job.get_by_id(session=session, job_id=self.notification_relation.job_id)
        payload = task_template.serialize_builder_info_default(session=session)
        return payload

    def send_to_webhook(self, session, url, secret, start_time=None):
        if self.type == ['task_completed', 'task_created']:
            payload = self.__generate_payload_for_task(session, start_time)
        elif self.type == 'input_file_uploaded':
            payload = self.__generate_payload_for_file(session, start_time)
        elif self.type == 'task_template_completed':
            payload = self.__generate_payload_for_task(session, start_time)
        else:
            logger.error('Invalid notification type for webhook.')
            return False

        computed_signature = hmac.new(codecs.encode(secret),
                                      msg=codecs.encode(json.dumps(payload)),
                                      digestmod=hashlib.sha1).hexdigest()
        headers = {
            'X-Hub-Signature': computed_signature
        }

        requests.post(url=url,
                      json=payload,
                      headers=headers)

    def __build_subject_and_message_for_task(self, session, start_time, event_type='completion'):
        print('BUILDING EMAIL', start_time, event_type)
        subject = 'New Task Completed: {}'.format(self.notification_relation.task_id)
        if event_type == 'creation':
            subject = 'New Task Created: {}'.format(self.notification_relation.task_id)

        if start_time:
            subject = 'New Tasks Completed.'
            if event_type == 'creation':
                subject = 'New Tasks Created'

            message = 'New Task completed on Project: {} \n\nTask List:\n'.format(
                self.notification_relation.task.project.name,
            )
            if event_type == 'creation':
                message = 'New Task created on Project: {} \n\nTask List:\n'.format(
                    self.notification_relation.task.project.name,
                )

            tasks_in_time_window = session.query(Task).filter(
                Task.project_id == self.notification_relation.task.project.id,
                Task.time_completed >= start_time,
                Task.time_completed <= datetime.datetime.utcnow()
            ).all()
            if event_type == 'creation':
                tasks_in_time_window = session.query(Task).filter(
                    Task.project_id == self.notification_relation.task.project.id,
                    Task.time_created >= start_time,
                    Task.time_created <= datetime.datetime.utcnow()
                ).all()

            links_list = ''
            for task in tasks_in_time_window:
                url_task = '[{}] {}task/{}'.format(task.job.name, settings.URL_BASE, task.id)
                links_list += '{} \n'.format(url_task)
            message += links_list
        else:
            message = 'New Task completed on Project: {} \n Task completed by: {} {} \n'.format(
                self.notification_relation.task.project.name,
                self.member_created.user.first_name if self.member_created else '--',
                self.member_created.user.last_name if self.member_created else '--',
            )
            if event_type == 'creation':
                message = 'New Task created on Project: {} \n'.format(
                    self.notification_relation.task.project.name,
                )
            url_task = '[{}] {}task/{}'.format(self.notification_relation.task.job.name,
                                               settings.URL_BASE,
                                               self.notification_relation.task_id)
            message += url_task
        return subject, message

    def __build_subject_and_message_for_task_template(self):
        url_task_template = '{}job/{}'.format(settings.URL_BASE, self.notification_relation.job_id)
        subject = 'New Task Template Completed: {}'.format(self.notification_relation.job_id)
        message = 'New Task Template completed on Project: {} \n To View the Task Template click the following link: {}'.format(
            self.notification_relation.job.project.name,
            url_task_template
        )
        return subject, message

    def __build_subject_and_message_for_file_upload(self, session=None, start_time=None):
        subject = 'New File Uploaded: {}'.format(self.notification_relation.input.file_id)

        if start_time:
            subject = 'New Files Uploaded.'

            message = 'New files uploaded on Project: {} \n\nFile List:\n'.format(
                self.notification_relation.input.file.project.name,
            )
            files = session.query(File).join(Input, Input.id == File.input_id).filter(
                File.project_id == self.notification_relation.input.file.project.id,
                Input.created_time >= start_time,
                Input.created_time <= datetime.datetime.utcnow()
            ).all()
            print('fileees', files, start_time, datetime.datetime.utcnow())
            links_list = ''
            for file in files:
                url_task = '==> {}file/{}'.format(settings.URL_BASE, file.id)
                links_list += '{} \n'.format(url_task)
            message += links_list
        else:
            message = 'New File uploaded on Project: {} \n File uploaded by: {} {} \n'.format(
                self.notification_relation.input.file.project.name,
                self.member_created.user.first_name if self.member_created else '--',
                self.member_created.user.last_name if self.member_created else '--',
            )

            url_task = '{}file/{}'.format(settings.URL_BASE,
                                          self.notification_relation.input.file_id)
            message += url_task

        return subject, message

    def send_email(self, session=None, start_time=None, email=None, email_list=[]):
        # URL to flow
        message = 'Default Message'
        subject = 'Default Subject'
        if self.type == 'task_completed':
            subject, message = self.__build_subject_and_message_for_task(session=session,
                                                                         start_time=start_time,
                                                                         event_type='completion')
        elif self.type == 'task_created':
            subject, message = self.__build_subject_and_message_for_task(session=session,
                                                                         start_time=start_time,
                                                                         event_type='creation')
        elif self.type == 'input_file_uploaded':
            subject, message = self.__build_subject_and_message_for_file_upload(session=session,
                                                                                start_time=start_time)

        elif self.type == 'task_template_completed':
            subject, message = self.__build_subject_and_message_for_task_template()

        if len(email_list) > 0:
            communicate_via_email.send(
                email_list=email_list,
                subject=subject,
                message=message)
        else:
            communicate_via_email.send(
                email=email,
                subject=subject,
                message=message)

    @staticmethod
    def new(session=None,
            add_to_session=False,
            flush_session=False,
            type=None,
            status='unread',
            channel_type='unread',
            description=None,
            title=None,
            member_created=None,
            member_updated=None,
            project_id=None,
            input_id=None,
            task_id=None,
            job_id=None,
            member_id=None,
            working_dir_id=None,
            file_id=None,
            ):

        notification = Notification(
            status=status,
            member_created=member_created,
            title=title,
            description=description,
            channel_type=channel_type,
            type=type,
            member_updated=member_updated,
            time_created=datetime.datetime.now(),
            time_updated=datetime.datetime.now(),
        )
        if add_to_session:
            session.add(notification)
        if flush_session:
            session.flush()
        # Create notification Object
        notification_relation = NotificationRelation.new(session=session,
                                                         add_to_session=add_to_session,
                                                         flush_session=flush_session,
                                                         project_id=project_id,
                                                         input_id=input_id,
                                                         task_id=task_id,
                                                         job_id=job_id,
                                                         member_id=member_id,
                                                         working_dir_id=working_dir_id,
                                                         file_id=file_id)
        notification.notification_relation = notification_relation
        return notification

    @staticmethod
    def get_by_id(session, job_launch_id=None):
        return session.query(Notification).filter(
            Notification.id == job_launch_id
        ).first()
