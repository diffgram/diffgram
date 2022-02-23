# OPENCORE - ADD
from methods.regular.regular_api import *
from methods.regular.regular_api import *

from shared.database.user import Signup_code
from shared.database.user import UserbaseProject
from shared.database.auth.api import Auth_api
from shared.database.auth.member import Member

from shared.database.deletion import Deletion


@routes.route('/api/project/<string:project_string_id>/share-link', methods=['POST'], defaults={'task_id': None})       # CAUTION note this is swapped, we fill default of route NOT using
@routes.route('/api/task/<int:task_id>/share-link', methods=['POST'],  defaults={'project_string_id': None})
@PermissionTaskOrProject.by_task_or_project_wrapper(
    apis_user_list = ["builder_or_trainer"],
    roles = ["admin", "Editor", "Viewer"])
def share_link(project_string_id, task_id):
    """


    """

    spec_list = [
        {'member_list': None},
        {'message': {
            'default': '',
            'required': False,
            'allow_empty': True,
            'kind': str
        }},
        {'link': str},
    ]
    log, input, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:

        # Case of providing just task_id (For trainer mode)
        if not project_string_id:
            task = Task.get_by_id(session, task_id=task_id)
            project_string_id = task.project.project_string_id

        current_user = User.get(session = session)
        link_sharer = LinkSharer(
            session=session,
            user_sending=current_user,
            log=log,
            link_to_send=input['link'],
            member_list=input['member_list'],
            message=input['message'],
            project=Project.get(session, project_string_id),
        )

        link_sharer.share_to_member_list()

        if len(link_sharer.log["error"].keys()) >= 1:
            return jsonify(log=link_sharer.log), 400

        link_sharer.log["success"] = True

    # Set cache dirty
    with sessionMaker.session_scope() as session:
        project = Project.get_by_string_id(session, project_string_id=project_string_id)
        project.set_cache_key_dirty('member_list')
        session.add(project)

        return jsonify(link_sharer.log), 200


class LinkSharer:

    def __init__(
            self,
            session,
            log,
            member_list,  # for existing members only?
            user_sending,  # for existing members only?
            project,
            message,
            link_to_send,
            notify=False
    ):

        """

        user_dict of form:
            {'email': str},
            {'permission_type': str},
            {'note': None}

        Assumption is that member_list, or user_dict can be None based on the mode
        And then the new() or remove() etc method will check if the dict it needs exists
        """

        self.session = session
        self.log = log
        self.user_sending = user_sending
        self.message = message
        self.link_to_send = link_to_send
        self.project_string_id = project.project_string_id  # Convenience since it's used a lot
        self.project = project
        self.member_list_untrusted = member_list
        self.member_list = []
        self.notify = notify

    def share_to_member_list(self):
        self.verify_member_list_untrusted()
        for member in self.member_list:
            self.email_link(member)
        return

    def verify_member_list_untrusted(self):
        if 'all' in self.member_list_untrusted:
            user_ids = [u.id for u in self.project.users]
            members = self.session.query(Member).filter(Member.id.in_(user_ids))
            self.member_list = members
            return
        for member_untrusted in self.member_list_untrusted:

            member = Member.get_by_id(
                session=self.session,
                member_id=member_untrusted
            )
            if not member:
                self.log['error']['member'] = "Member does not exist."
                return

            self.member_list.append(member)

    def email_link(
            self,
            member
    ):
        if not member.user or not member.user.email:
            return
        
        subject = f"[{self.project_string_id}]{self.user_sending.first_name} Has Shared an Instance With You "

        message = f"{self.user_sending.first_name} shared the following instance: \n\r {self.link_to_send} \n\r"

        message += "Notes: \n\r"

        message += f"{self.message}"
        communicate_via_email.send(member.user.email, subject, message)
