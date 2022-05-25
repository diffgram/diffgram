# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *

from shared.database.connection.connection import Connection
from cryptography.fernet import Fernet

connection_spec_list = [

    {'name': {
        'default': 'My Connection',
        'kind': str,
        'required': False
    }
    },
    {'project_string_id': {
        'kind': str,
        'required': False
    }
    },
    {'permission_scope': {
        'default': 'project',
        'kind': str,
        'required': False,
        'valid_values_list': ['project', 'org', 'Project', 'Org']
    }
    },
    {"archived": {
        'default': False,
        'kind': bool,
        'required': False
    }
    },
    {"private_id": {
        'default': None,
        'kind': str,
        'required': False
    }
    },
    {"private_host": {
        'default': None,
        'kind': str,
        'required': False
    }
    },
    {"private_secret": {
        'default': None,
        'kind': str,
        'required': False
    }
    },
    {"disabled_ssl_verify": {
        'default': None,
        'kind': bool,
        'required': False
    }
    },
    # WIP... We assume for new we want to update it, otherwise
    # assume we don't. May be cases where we do wish to do so
    # because of encryption though we don't know on the front
    {"do_update_private_secret": {
        'default': False,
        'kind': bool,
        'required': False
    }
    },

    {"account_email": {
        'default': None,
        'kind': str,
        'required': False
    }
    },

    {"project_id_external": {
        'default': None,
        'kind': str,
        'required': False
    }
    },

    {"integration_name": {
        'default': None,
        'kind': str,
        'required': True
    }
    }

    # See update_connection () for where metadata get loaded
]


class Connection_Operations():
    """
    """

    def __init__(
        self,
        session,
        connection_id: int = None,
        metadata: dict = None,
        member = None,
        project_string_id = None
    ):

        self.session = session
        self.connection_id = connection_id

        # This will get converted into
        # metadata after validating spec.
        self.metadata_untrusted = metadata
        self.member = member

        # These are assumed to be set from other functions
        # ie through a validation process...???
        self.org = None
        self.project = None
        self.fernet = None

        self.log = regular_log.default()

        if self.metadata_untrusted:
            self.metadata = self.validate_connection_spec(
                metadata_untrusted = self.metadata_untrusted)
            if len(self.log["error"].keys()) >= 1:
                return

        self.project_string_id = project_string_id

    def init_cryptography(self):
        """
        Context we have seen this fail is if fernet key is invalid.
        """

        try:
            self.fernet = Fernet(settings.FERNET_KEY)

            if self.fernet is None:
                raise Exception('Fernet not defined.')

        except Exception as exception:
            print('[init_cryptography] ', exception)
            return False

    def get_existing_connection(self, connection_id):
        """
        No permissions checking
        Literal get database object
        """
        self.connection = Connection.get_by_id(
            session = self.session,
            id = connection_id)

        return self.connection

    def validate_existing_connection_id_permissions(self):
        """
        For external validation

        We use what we know about the connection (ie the project it's related to)
        and what we know about the user making the request to validate the permissions.

        Because if we use what the user supplies the user could
        supply any project they have permissions to (even if it's unrelated to to the connection)

        The assumption is we operate on the project from the connection
        May still need some more thought here.

        There's some tension / confusion here between how we should validate
        permissions for an existing one...

        concrete for existing
        """
        if self.connection is None:
            raise Forbidden("Not Found")

        self.validate_connection_permissions_scope(
            permission_scope = self.connection.permission_scope,
            project_string_id = self.connection.project.project_string_id,
        )

    def validate_connection_permissions_scope(self,
                                              permission_scope: str,
                                              project_string_id: str = None
                                              ):
        """
        abstract

        For internal use generally.
        """

        permission_scope = permission_scope.lower()

        self.permission_scope = permission_scope

        if permission_scope == "project":
            # Validate project
            # July 1, 2020,
            # only Admin because even seeing the list view of storage
            # objects may be considered sensitive

            project_role_list = ["admin"]

            Project_permissions.check_permissions(
                session = self.session,
                project_string_id = project_string_id,
                Roles = project_role_list)

            self.project = Project.get(self.session, project_string_id)
            return

        # Should not be possible to reach here if permission_scope string is validated.
        raise Forbidden("permission_scope is invalid")

    def save(self):

        self.connection = self.get_from_id_or_new_connection(
            connection_id = self.connection_id,
            project = self.project
        )
        if len(self.log["error"].keys()) >= 1:
            return

        self.update_connection(metadata = self.metadata)

        if len(self.log["error"].keys()) >= 1:
            return

        self.session.add(self.connection)

        if not self.connection.id:
            self.session.flush()  # Get ID, relevant if new object

    def get_from_id_or_new_connection(
        self,
        connection_id: int,
        project = None
    ) -> Connection:
        """
        Pattern where creating a "new"
        one really just does the ID and the rest if part of update process?

        """

        if connection_id:
            connection = Connection.get_by_id(
                session = self.session,
                id = connection_id)

            if connection is None:
                self.log['error']['connection'] = "Invalid connection ID"
                return

            return connection

        else:
            return Connection.new(
                member = self.member,
                project = project)

    def encrypt_secret(self, secret) -> str:
        """
        https://pypi.org/project/cryptography/
        it works in bytes
        but we assume secret will be a string

        """
        if not self.fernet:
            self.init_cryptography()

        return self.fernet.encrypt(secret.encode())

    def decrypt_secret(self, secret) -> str:
        """
        For use when a connection is being used to
        process some other part of the system

        Library returns bytes, we want string
            Note difference that we are decoding return value
            Except when encrypting...

        Exception handling
            One example is: secret key is not a match for encrypted data
            Context that we would rather catch these with dedicated cases
            as they come up. Since it's likely to be an ongoing thing that
            it's possible for keys to get rotated / mixed up.
            Still needs more work.
        """
        if not self.fernet:
            self.init_cryptography()
        if not self.fernet:
            return False

        try:
            open_secret = self.fernet.decrypt(secret)
            string_open_secret = open_secret.decode()
            new_line_fixed_string_open_secret = string_open_secret.replace('\\n', '\n')

            return new_line_fixed_string_open_secret

        except Exception as exception:
            print('[decrypt_secret]', exception)
            return False

    def get_secret(self) -> str:
        """
        Concrete getter for default secret
        """

        if not self.connection:
            return False

        return self.decrypt_secret(self.connection.private_secret_encrypted)

    def validate_connection_spec(
        self,
        metadata_untrusted: dict):
        """
        This is strictly validating the
        raw data is there it's not checking permissions

        """

        self.log, metadata = regular_input.input_check_many(
            spec_list = connection_spec_list,
            log = self.log,
            untrusted_input = metadata_untrusted)

        if len(self.log["error"].keys()) >= 1:
            return

        return metadata

    def update_secret_connection(
        self,
        metadata: dict):
        """
        careful, we don't store this on front end by default
        so only update if user expressly updates
        """

        private_secret = metadata.get('private_secret')
        if not private_secret:
            return

        self.connection.private_secret_encrypted = self.encrypt_secret(private_secret)

    def update_connection(
        self,
        metadata: dict):
        """
        Assumes data has been validated...

        Assumes all 'connections' are unique concrete instances

        """

        ## CAREFUL need to add into API spec too
        self.connection.name = metadata.get('name')
        self.connection.permission_scope = metadata.get('permission_scope')
        if self.connection.permission_scope:
            self.connection.permission_scope.lower()
        self.connection.archived = metadata.get('archived')
        self.connection.integration_name = metadata.get('integration_name')
        self.connection.private_host = metadata.get('private_host')
        self.connection.disabled_ssl_verify = bool(metadata.get('disabled_ssl_verify', False))
        self.connection.private_id = metadata.get('private_id')
        self.connection.account_email = metadata.get('account_email')
        self.connection.project_id_external = metadata.get('project_id_external')

        self.connection.member_updated = self.member

        self.update_secret_connection(metadata = metadata)

    def connection_list(
        self):
        """
        Assumes validated scope / permission

        Seems to make sense to use self here since
        we are only running this if validated right?
        """

        connections_list = Connection.list(
            session = self.session,
            permission_scope = self.permission_scope,
            project = self.project,
            return_kind = "objects"
        )
        return connections_list
