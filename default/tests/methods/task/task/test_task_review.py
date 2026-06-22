from unittest.mock import patch

import json
import flask
from typing import Dict, Any, Union
from shared.database.hashing_functions import make_secure_val
from shared.database.discussion.discussion_comment import DiscussionComment
from shared.database.task.task_event import TaskEvent
from shared.utils.task.task_update_manager import Task_Update
from shared.database.task.task import TASK_STATUSES, Task
from methods.task.task import task_next_issue, task_complete
from methods.regular.regular_api import get_project_by_project_string_id
from methods.task.task import task_review
from shared.database.project.project import Project
from shared.database.directory.directory import Directory
from shared.database.member.member import Member
from shared.database.user.user import User
from shared.database.file.file import File
from shared.database.job.job import Job
from shared.database.session import SessionLocal


class TestTaskReview:
    """Test cases for task_review module."""

    def setUp(self) -> None:
        """Set up the test environment."""
        self.session: SessionLocal = SessionLocal()
        self.project_data = self.create_project_with_context()
        self.project: Project = self.project_data['project']
        self.auth_api = self.create_project_auth()
        self.member: Member = self.auth_api.member
        self.member.user = self.register_user(
            username='test_user',
            email='test@test.com',
            password='diffgram123',
            project_string_id=self.project.project_string_id,
            member_id=self.member.id
        )
        job = self.create_job(name=f"my-test-job-{1}", project=self.project)
        file = self.create_file(project_id=self.project.id)
        self.task: Task = self.create_task(
            name='test task', file=file, job=job, status='available'
        )
        self.task.add_reviewer(self.session, self.auth_api.member.user)
        self.task.add_reviewer(self.session, self.member.user)
        self.session.commit()

    def create_project_with_context(self, users: Dict[str, Any]) -> Dict[str, Union[Project, Member]]:
        """Create a project with context."""
        return data_mocking.create_project_with_context(users, self.session)

    def create_project_auth(self, project: Project = None, session: SessionLocal = None) -> common_actions:
        """Create project authentication."""
        return common_actions.create_project_auth(project=project, session=session)

    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        project_string_id: str,
        member_id: int
    ) -> User:
        """Register a user."""
        return data_mocking.register_user(
            {
                'username': username,
                'email': email,
                'password': password,
                'project_string_id': project_string_id,
                'member_id': member_id
            },
            self.session
        )

    def create_job(self, name: str, project: Project) -> Job:
        """Create a job."""
        return data_mocking.create_job({'name': name, 'project': project}, self.session)

    def create_file(self, project_id: int) -> File:
        """Create a file."""
        return data_mocking.create_file({'project_id': project_id}, self.session)

    def create_task(
        self,
        name: str,
        file: File,
        job: Job,
        status: str
    ) -> Task:
        """Create a task."""
        return data_mocking.create_task({'name': name, 'file': file, 'job': job, 'status': status}, self.session)

    @staticmethod
    def test_task_review_api(
        client,
        client_id: str,
        client_secret: str,
        project_string_id: str,
        task_id: int,
        make_secure_val_mock: patch
    ) -> None:
        """Test task review API."""
        request_data = {
            'action': 'approve'
        }
        auth_api = common_actions.create_project_auth(
            project=get_project_by_project_string_id(project_string_id, client, self.session),
            session=self.session
        )
        auth_api.member.user = data_mocking.register_user(
            {
                'username': 'test_user',
                'email': 'test@test.com',
                'password': 'diffgram123',
                'project_string_id': project_string_id,
                'member_id': auth_api.member.id
            },
            self.session
        )
        self.task.add_reviewer(self.session, auth_api.member.user)
        self.session.commit()

        with client.session_transaction() as session:
            session['user_id'] = make_secure_val_mock(auth_api.member.user.id)
            credentials = b64encode(f"{client_id}:{client_secret}".encode()).decode('utf-8')

        response = client.post(
            f"/api/v1/task/{task_id}/review",
            data=json.dumps(request_data),
            headers={
                'directory_id': str(self.project.directory_default_id),
                'Authorization': f"Basic {credentials}"
            }
        )
        data = response.json
        make_secure_val_mock.assert_called_once()
        assert response.status_code == 200
        assert data['task']['status'] == 'complete'

        # 400 Case
        request_data = {
            'action': 'wrong_value'
        }
        response = client.post(
            f"/api/v1/task/{task_id}/review",
            data=json.dumps(request_data),
            headers={
                'directory_id': str(self.project.directory_default_id),
                'Authorization': f"Basic {credentials}"
            }
        )
        data = response.json
        assert response.status_code == 400

    @staticmethod
    def test_task_review_core(
        session: SessionLocal,
        task: Task,
        member: Member,
        action: str,
        comment_text: str
    ) -> None:
        """Test task review core."""
        with patch('shared.utils.task.task_update_manager.Task_Update.main') as mock:
            with patch('shared.database.discussion.discussion_comment.DiscussionComment.new', return_value='discussion_comment_result') as new_mock:
                with patch('shared.database.task.task_event.TaskEvent.generate_task_comment_event') as task_event_mock:
                    if action == 'approve':
                        task_review.task_review_core(
                            session=session,
                            task_id=task.id,
                            action=action,
                            member=member,
                            comment_text=comment_text
                        )
                        mock.assert_called_once()
                        new_mock.assert_called_once()
                        task_event_mock.assert_called_once()
                    elif action == 'request_change':
                        result = task_review.task_review_core(
                            session=session,
                            task_id=task.id,
                            action=action,
                            member=member,
                            comment_text=comment_text
                        )
                        mock.assert_called_once()
                        assert result['id'] == task.id
                        assert result['status'] == TASK_STATUSES['requires_changes']
                    else:
                        raise ValueError(f"Invalid action: {action}")
