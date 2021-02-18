from diffgram.core.directory import Directory


class Job():

    def __init__(self,
                 client,
                 job_dict=None):

        self.client = client

        if self.client.project_string_id is None:
            raise Exception("\n No project string id in client.")

        # TODO review way to set all properties
        # from existing job update

        self.id = None
        self.name = None
        self.status = None
        self.stat_count_tasks = None
        self.stat_count_complete = None
        self.percent_completed = None
        self.tasks_remaining = None
        self.instance_type = None
        self.share = None
        self.type = None
        self.permission = None
        self.field = None
        self.category = None
        self.review_by_human_freqeuncy = None
        self.label_mode = None
        self.passes_per_file = None
        self.attached_directories = []
        self.member_list_ids = []
        self.attached_directories_dict = None

        self.refresh_from_dict(
            job_dict=job_dict)

    def refresh_from_dict(
            self,
            job_dict=None):

        if not job_dict:
            return

        for key, value in job_dict.items():
            setattr(self, key, value)

    def __repr__(self):
        return str(self.serialize())

    def __add_directory_to_job(self, directory, mode='sync'):
        """

        :param directories: Array of directories Objects
        :param mode: sync, copy_once or inactive.
        :return:
        """
        self.attached_directories.append(
            {
                'directory_id': directory['id'],
                'selected': mode,

            }
        )
        return self.attached_directories

    def attach_directories(self, directories, mode='sync', override_existing=False):
        """
            Attaches directories to a job.
        :param directories: Array of directories Objects
        :param mode: sync, copy_once or inactive.
        :param override_existing: if True. detaches all existing directories.
        :return: The updated job object with the new directories.
        """
        if len(directories) == 0:
            raise ValueError('Provide at least 1 directory')
        if self.status != 'draft':
            raise ValueError('Can only attach directories while on draft mode, not when job has been already launched.')
        if override_existing:
            self.attached_directories = []

        for dir in directories:
            self.attached_directories.append(
                {
                    'directory_id': dir['id'],
                    'selected': mode

                }
            )
        self.attached_directories_dict = {'attached_directories_list': self.attached_directories}
        endpoint = "/api/v1/project/{}/job/update".format(self.client.project_string_id)
        data = self.serialize()
        data['job_id'] = self.id
        response = self.client.session.post(
            self.client.host + endpoint,
            json=data)

        self.client.handle_errors(response)

        data = response.json()

        if data["log"]["success"] == True:
            # TODO review better way to update fields
            self.id = data["job"]["id"]

        return self

    def serialize(self):

        if hasattr(self.launch_datetime, 'isoformat'):
            self.launch_datetime = self.launch_datetime.isoformat()

        label_file_list = None
        if hasattr(self, "label_file_list") and self.label_file_list:
            label_file_list = [file.serialize() for file in self.label_file_list]

        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'instance_type': self.instance_type,
            'share': self.share,
            'type': self.type,
            'permission': self.permission,
            'field': self.field,
            'category': self.category,
            'review_by_human_freqeuncy': self.review_by_human_freqeuncy,
            'label_mode': self.label_mode,
            'passes_per_file': self.passes_per_file,
            'file_count': self.file_count,
            'attached_directories_dict': self.attached_directories_dict,
            'launch_datetime': self.launch_datetime,
            'label_file_list': label_file_list,
            'member_list_ids': self.member_list_ids
        }

    def new(self,
            name=None,
            instance_type=None,
            share="project",
            job_type="Normal",
            permission=None,
            field=None,
            category=None,
            review_by_human_freqeuncy=None,
            label_mode=None,
            passes_per_file=None,
            file_list=None,
            guide=None,
            launch_datetime=None,
            file_count=None,
            label_file_list=None,
            sync_directories=[],
            single_copy_directories=[],
            members_list_ids = [],
            ):
        """

        Arguments
            self,
            config, a dict of job data
            launch, bool, Launch job after creation

        Expects

        Returns

        """

        # QUESTION create job object eariler instead of after response?
        if len(members_list_ids) == 0:
            raise ValueError('Please provide at least one member_id in members_list_ids.')
        job = Job(client=self.client)

        job.name = name
        job.instance_type = instance_type
        job.share = share
        job.type = job_type  # careful rename to type from job_type
        job.permission = permission
        job.field = field
        job.category = category
        job.review_by_human_freqeuncy = review_by_human_freqeuncy
        job.label_mode = label_mode
        job.passes_per_file = passes_per_file
        job.launch_datetime = launch_datetime
        job.label_file_list = label_file_list
        job.attached_directories = []
        job.member_list_ids = members_list_ids

        if len(sync_directories) == 0 and len(single_copy_directories) == 0:
            raise ValueError(
                'Please provide at least one attached directory to the job in either sync_directories param or single_copy_directories')

        for dir in sync_directories:
            self.__add_directory_to_job(directory=dir, mode='sync')

        for dir in single_copy_directories:
            self.__add_directory_to_job(directory=dir, mode='sync')

        job.attached_directories_dict = {'attached_directories_list': self.attached_directories}

        if not file_count:
            if file_list:
                file_count = len(file_list)

        job.file_count = file_count

        endpoint = "/api/v1/project/{}/job/new".format(self.client.project_string_id)

        response = self.client.session.post(
            self.client.host + endpoint,
            json=job.serialize())

        self.client.handle_errors(response)

        data = response.json()

        if data["log"]["success"] == True:
            # TODO review better way to update fields
            job.id = data["job"]["id"]

        if file_list:
            # Careful we want to call job here not self
            # Since job will have a different id
            # self is constructor
            job.file_update(file_list=file_list)

        if guide:
            job.guide_update(guide=guide)

        return job

    def file_update(
            self,
            file_list,
            add_or_remove="add"
    ):
        """

        Arguments
            self,
            file_list, list of files,
            add_or_remove, either "add" or "remove"

        Expects

        Returns

        Assumptions

            The API will use the project default if None is supplied
            but if we are not in the default we must supply valid
            directory_id

            Otherwise when it checks permissions it will error
            ie {"file_link":"File link not in incoming directory"}

        """

        endpoint = "/api/v1/project/" + self.client.project_string_id + \
                   "/job/file/attach"

        file_list = [file.serialize() for file in file_list]

        update_dict = {
            'directory_id': self.client.directory_id,
            'file_list_selected': file_list,
            'job_id': self.id,
            'add_or_remove': add_or_remove}

        response = self.client.session.post(self.client.host + endpoint,
                                            json=update_dict)

        self.client.handle_errors(response)

        data = response.json()

        if data["log"]["success"] == True:
            print("File update success")

    def launch(
            self
    ):
        """

        Arguments
            self,

        Expects
            None

        Returns
            True if success

        """

        endpoint = "/api/v1/job/launch"

        request = {'job_id': self.id}

        response = self.client.session.post(
            self.client.host + endpoint,
            json=request)

        self.client.handle_errors(response)

        data = response.json()

        if data["log"]["success"] == True:
            print("Launched")
            return True

        return False

    def guide_update(
            self,
            guide,
            kind="default",
            action="update"
    ):
        """

        Arguments
            self,
            guide, class Guide object
            kind options ["default", "review"]
            update_or_remove options ["update", "remove"]

        Expects

        Returns
            None, prints update

        """

        endpoint = "/api/v1/guide/attach/job"

        update_dict = {'guide_id': guide.id,
                       'job_id': self.id,
                       'kind': kind,
                       'update_or_remove': action}

        response = self.client.session.post(self.client.host + endpoint,
                                            json=update_dict)

        self.client.handle_errors(response)

        data = response.json()

        if data["log"]["success"] == True:
            print("Guide update success")
            return True

        return False

    def get_by_id(
            self,
            id: int):
        """
        """

        job = Job(client=self.client)
        job.id = id

        job.refresh_info()

        return job

    def generate_export(
            self,
            kind='Annotations',
            return_type="data",
            wait_for_export_generation=True
    ):
        """

        Arguments
            self,
            kind, string, in ["Annotations", "TF Records"]
            return_type, string, in ["url", "data"]

        # Note that the "data" return type is for kind "Annotations"
        # The data is expected to be returned in JSON format

        Expects

        Returns

        """

        endpoint = "/api/walrus/project/" + self.client.project_string_id + \
                   "/export/to_file"

        # TODO not a fan of "return_type" variable name
        # Also, can we map this into a more "automatic"
        # Default? ie tf records being a url etc..

        spec_dict = {
            'job_id': self.id,
            'kind': kind,
            'source': "job",
            'file_comparison_mode': "latest",
            'directory_id': None,
            'masks': False,
            'return_type': return_type,
            'wait_for_export_generation': wait_for_export_generation
        }

        response = self.client.session.post(self.client.host + endpoint,
                                            json=spec_dict)

        self.client.handle_errors(response)

        data = response.json()

        if wait_for_export_generation is False:
            export = self.client.export.new(data.get('export'))
            return export

        return data

    def refresh_info(
            self,
            mode_data=None
    ):
        """
        Assumptions

        Arguments

        Returns

        """

        endpoint = "/api/v1/job/" + str(self.id) + \
                   "/builder/info"

        spec_dict = {
            'mode_data': mode_data
        }

        response = self.client.session.post(
            self.client.host + endpoint,
            json=spec_dict)

        self.client.handle_errors(response)

        data = response.json()

        # print(data)

        self.refresh_from_dict(
            job_dict=data['job'])
