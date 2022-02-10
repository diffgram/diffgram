# OPENCORE - ADD
from methods.regular.regular_api import *

from shared.database.user import Signup_code
from shared.database.user import UserbaseProject
from shared.database.auth.api import Auth_api
from shared.database.auth.member import Member

from shared.database.deletion import Deletion
from shared.feature_flags.feature_checker import FeatureChecker
from shared.regular.regular_log import log_has_error

@routes.route('/api/project/<string:project_string_id>/share',
              methods = ['POST'])
@Project_permissions.user_has_project(["admin"])
def share_member_project_api(project_string_id):
    """

    Also covers revoking / removing user / member

    Adds a user to a project
    Checks
    1. User adding has permission to add user to project (ie is admin)
    2. If user being added is existing
    3. Chooses appropriate method to execute request

    If user is existing calls permissions_update_user_exists()
    else calls permissions_invite_user()

    Returns {"success" : True} if successful , {"success" : False} otherwise

    user is user to be added... is there a better name for that?
    """

    spec_list = [
        {'member_list': None},
        {'mode': str},
        {'user_dict': None},
        {'notify': {
            'default': True,
            'kind': bool
        }
        }
    ]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        member = get_member(session)
        share_project = Share_Project(
            session = session,
            member = member,
            member_list = input['member_list'],
            user_dict = input['user_dict'],
            mode = input['mode'],
            project = Project.get(session, project_string_id),
            notify = input['notify']
        )

        share_project.user_who_made_request = User.get(session)

        share_project.main()

        if len(share_project.log["error"].keys()) >= 1:
            return jsonify(log = share_project.log), 400

        share_project.log["success"] = True

    # Set cache dirty
    with sessionMaker.session_scope() as session:
        project = Project.get_by_string_id(session, project_string_id = project_string_id)
        project.set_cache_key_dirty('member_list')
        session.add(project)

        return jsonify(share_project.log), 200


@routes.route('/api/project/<string:project_string_id>/share/list',
              methods = ['GET'])
@Project_permissions.user_has_project(["admin", "Editor", "Viewer"])
def share_view_list_api(project_string_id):
    """
    Returns list of user permissions for project
    """

    with sessionMaker.session_scope() as session:
        project = Project.get(session, project_string_id)

        members_list = project.regenerate_member_list()

        auth_api_list = Auth_api.list_by_project(session, project_string_id)

        # CAREFUL does permission here match with route permission?
        # ie allow view, than can't show client secret from auth_api
        for auth_api in auth_api_list:
            members_list.append(auth_api.serialize())

        return jsonify(success = True,
                       members_list = members_list), 200


class Share_Project():

    def __init__(
        self,
        session,
        member,
        member_list,  # for existing members only?
        mode,  # NEW , REMOVE
        project,
        user_dict,  # "NEW" user dict
        notify = False
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
        self.member = member
        self.mode = mode
        self.log = regular_log.default()
        self.mode = mode
        self.project_string_id = project.project_string_id  # Convenience since it's used a lot
        self.project = project
        self.member_list_untrusted = member_list
        self.member_list = []
        self.user_dict = user_dict
        self.notify = notify

    def main(self):

        if self.mode == "NEW":
            self.new()

        print('NEWW', self.log)
        if log_has_error(self.log):
            return

        # Could add "update" here in future...
        if self.mode in ["REMOVE"]:
            self.verify_member_list_untrusted()

        for member in self.member_list:

            self.member_to_modify = member

            if self.mode == "REMOVE":
                self.remove()

        if log_has_error(self.log):
            return

        if len(self.log["error"].keys()) == 0:
            # cache invalidation if successful
            self.project.set_cache_key_dirty('member_list')
            self.session.add(self.project)

    def verify_member_list_untrusted(self):

        for member_untrusted in self.member_list_untrusted:

            member = Member.get_by_id(
                session = self.session,
                member_id = member_untrusted.get('member_id'))

            if member.user == self.user_who_made_request:
                self.log['error']['user_who_made_request'] = "Can't remove yourself."
                return

            self.member_list.append(member)

    def check_free_tier_member_limits(self):

        existing_members = self.project.regenerate_member_list()

        feature_checker = FeatureChecker(
            session = self.session,
            user = self.member.user,
            project = self.project
        )

        max_users = feature_checker.get_limit_from_plan('MAX_USERS_PER_PROJECT')

        if len(existing_members) >= max_users:
            message = 'Free Tier Limit Reached - Max Users Allowed: {}. But Project with ID: {} has {}'.format(
                max_users,
                self.project.project_string_id,
                len(existing_members))
            self.log['error']['free_tier_limit'] = message
            return False

    def new(self):

        # NEW is untested after refactor

        spec_list = [
            {'email': str},
            {'permission_type': str},
            {'note': None}
        ]

        self.log, input = regular_input.input_check_many(
            spec_list = spec_list,
            log = self.log,
            untrusted_input = self.user_dict)

        self.check_free_tier_member_limits()

        if log_has_error(self.log):
            print('LOG HAS ERROR')
            return

        # TODO review if we should use the validate() function for email
        # currently in user/account/account_new
        # and if that validate function is also striping whitespace as expected.
        # wonder if that applies to login / other areas too...

        input['email'] = input['email'].strip()  # remove whitespace which
        # is especially relevent here because we are checking if the user
        # exists

        self.user_to_modify = User.get_by_email(self.session, input['email'])

        if self.user_who_made_request.is_super_admin is not True:
            if self.user_to_modify == self.user_who_made_request:
                self.log['error']['user_who_made_request'] = "You are already on the project."
                return
        print('user_to_modify', self.user_to_modify)
        # Assumes if user exists to add permissions directly
        if self.user_to_modify:

            permission_result, permission_error = Project_permissions.add(
                input['permission_type'],
                self.user_to_modify,
                self.project_string_id)

            if self.project not in self.user_to_modify.projects:
                self.user_to_modify.projects.append(self.project)

            if permission_result is False:
                self.log['error']['permission_error'] = permission_error
                return

            self.email_existing_user(
                permission_type = input['permission_type'],
                note = input['note'])

            UserbaseProject.set_working_dir(session = self.session,
                                            user_id = self.user_to_modify.id,
                                            project_id = self.project.id,
                                            working_dir_id = self.project.directory_default_id)

        # Assumes user does not exist
        else:

            # TODO refactor to use shared auth code signup method
            signup_code = Signup_code()
            signup_code.email_sent_to = input['email']
            signup_code.type = "add_to_project"

            signup_code.new_code(self.session)

            signup_code.project_string_id = self.project_string_id
            signup_code.permission_level = input['permission_type']
            self.session.add(signup_code)

            signup_link = settings.URL_BASE + "user/new?" + \
                          "code=" + signup_code.code + \
                          "&email=" + signup_code.email_sent_to

            self.invite_user(
                signup_link = signup_link,
                permission_type = input['permission_type'],
                note = input['note'],
                email = input['email'])

        Event.new(
            kind = "shared_project",
            session = self.session,
            member_id = self.user_who_made_request.member_id,
            project_id = self.project.id,
            email = self.user_who_made_request.email
        )

    def remove(self):

        if self.member_to_modify.kind == "human":
            self.remove_user()

        if self.member_to_modify.kind == "api":
            self.remove_auth_api()

    def remove_auth_api(self):

        auth_api = self.member_to_modify.auth_api

        if auth_api is None:
            self.log['error']['auth_api'] = "No valid auth api attached to this member"
            return

        if auth_api.project != self.project:
            self.log['error']['auth_api'] = "Permission error, check auth is related to project."
            return

        if auth_api.is_valid == False:
            self.log['error']['auth_api'] = "Is already not valid."
            return

        # TODO share deletion thing? maybe record member instead of auth_api id?
        deletion = Deletion(project = self.project,
                            member_created = self.user_who_made_request.member,
                            mode = 'remove_auth_api')
        self.session.add(deletion)
        deletion.cache = {}
        deletion.cache['auth_api_id'] = auth_api.id

        auth_api.is_valid = False
        self.session.add(auth_api)

    def remove_user(self):
        """

        """

        # TODO what parts of this are shared with auth and what parts are user only

        # TODO current operating on member or some other name
        # Instead of going back and forth...

        # Do we want to do this, or check if the user has the project in their user.projects...
        # Context of security model that we don't know till this point if a user / member thing
        # being passes this way is actually valid.
        # Realized that if the project key doesn't exist that that will fail, could use a .get()

        self.user_to_modify = self.member_to_modify.user

        if self.project not in self.user_to_modify.projects:
            self.log['error']['permission_error'] = "Check right user / project combination"
            return

        # Assumes first permission
        user_current_permission = self.user_to_modify.permissions_projects[self.project_string_id][0]

        deletion = Deletion(project = self.project,
                            member_created = self.user_who_made_request.member,
                            mode = 'remove_users_project_permission')
        self.session.add(deletion)

        deletion.cache = {}
        deletion.cache['user_modified'] = self.user_to_modify.id

        deletion.cache['permissions'] = user_current_permission

        # TODO error handling here...
        Project_permissions.remove(
            permission = user_current_permission,
            user = self.user_to_modify,
            sub_type = self.project_string_id)

        self.session.add(self.user_to_modify)
        self.user_to_modify.projects.remove(self.project)

    def email_existing_user(
        self,
        permission_type,
        note
    ):

        if self.notify is False:
            return

        subject = "Added to project " + self.project_string_id

        message = " You have been added to: " + self.project_string_id
        message += " as a " + str(permission_type)

        message += ". Access the project here. " + settings.URL_BASE + \
                   "project/" + self.project_string_id

        message += " Added by " + str(self.user_who_made_request.email)
        message += " With personal note of:" + str(note)

        communicate_via_email.send(self.user_to_modify.email, subject, message)

    def invite_user(
        self,
        signup_link,
        permission_type,
        note,
        email):
        """
        In:
        self.user_to_modify, dictionary

        Does:
        Sends email to user to be invited

        """

        # We still notify here since the user doesn't exist...

        subject = "Added to project " + self.project_string_id

        message = " You have been added to: " + self.project_string_id
        message += " as an: " + str(permission_type)

        message += " Create an account to get started here: " + signup_link

        message += " Added by " + str(self.user_who_made_request.email)
        message += " " + str(note)

        # Careful, can't use self.user_to_modify here since user doesn't exist yet....
        communicate_via_email.send(email, subject, message)
