try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *

import threading

from shared.database.input import Input
from shared.permissions.super_admin_only import Super_Admin



# from methods.input.process_media import check_if_add_items_to_queue
# circular import...


@routes.route('/api/walrus/v1/project/<string:project_string_id>' +
              '/input/update',
              methods = ['POST'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
@limiter.limit("300 per day")
def api_input_update(project_string_id):
    """

    """
    spec_list = [
        {'id_list': list},
        {"mode": {
            'kind': str,
            'valid_values_list': ["ARCHIVE", "RETRY"]
        }
        }
    ]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        user = User.get(session = session)
        project = Project.get(session, project_string_id)

        # TODO somehow validate that input list is a list of ints?

        input_list = session.query(Input).filter(
            Input.id.in_(input['id_list']),
            Input.project_id == project.id).all()
        if not input_list:
            log['error']['id_list'] = "None found."
            return jsonify(log = log), 400

        if input['mode'] == "RETRY":
            update_input = Update_Input(
                session = session,
                input_list = input_list)

            update_input.retry_file_list()

            if len(update_input.log["error"].keys()) >= 1:
                return jsonify(log = update_input.log), 400

        # For testing it's handy to run this right away here
        # check_if_add_items_to_queue(add_deferred_items_time = 0)

        if input['mode'] == "ARCHIVE":
            update_input = Update_Input(
                session = session,
                input_list = input_list)

            update_input.archive_input()

            log['success'] = True

        return jsonify(log = log), 200


def report_input_forever():
    def task_manager():
        minutes = 180
        check_interval_seconds = 60 * minutes

        while True:
            print("[input report monitor] heartbeat")
            with sessionMaker.session_scope() as session:
                update_input = Update_Input(
                    session = session
                )

                update_input.report_input_list_recent(
                    include_within_x_minutes = minutes)

            time.sleep(check_interval_seconds)

    t = threading.Timer(0, task_manager)
    t.daemon = True
    t.start()


# Need a time sleep here for testing, else program quits
# As it doesn't wait on thread (unlike in context of server)
# time.sleep(100)


@routes.route('/api/walrus/v1/diffgram/reporting/input/start',
              methods = ['GET'])
@Super_Admin.is_super()
def start_input_reporting_api():
    """
    Manual method to start reporting
    while we figure out gunicorn sql connection
    """

    report_input_forever()

    return jsonify(True), 200


@dataclass
class Update_Input():
    session: Any
    input_list: list = None

    """

    Mainly focused around Retrying 

    Expecting this could get a lot more complex in the future

    TODO 
    Consider what retrys are allowed, 
        ie requiring URL or some way to re access it

    What other informatino should be stored?
        ie should the timestamp change, or some other record of it being 
        retried? some benefits to not changing some of info

    What checks are we doing for stuff,
        ie I am hardpressed to see when we would need
        to retry a success case?

    Can we use this for some form of input or config testing?
        sometimes the input stuff can be complex, 

    It creates it's own log, just for this process right?


    """

    def __post_init__(self):
        self.log = regular_log.default()

    def retry_file_list(self):

        for input in self.input_list:
            self.input = input
            self.retry_file()

    def retry_file(self):
        """

        1) Marks existing file as "removed"
        2) Sets processing deferred on input to True
        3) Resets status

        TODO limits,
            * ie do we allow retry of "split" videos,
                and if so does that need to follow different
                process
            * ...

        """

        if self.input.mode != "update":
            # Important. Context of updates not creating a new file, so not wanting to
            # remove original file.
            self.remove_associated_file(self.input)

        self.input.processing_deferred = True

        self.input.status = "retrying"
        self.input.status_text = ""
        self.input.update_log = {}

        if not self.input.retry_count:
            self.input.retry_count = 0
        self.input.retry_count += 1

        if not self.input.retry_log:
            self.input.retry_log = {}

        self.input.retry_log[datetime.datetime.utcnow().isoformat()] = self.log

        self.session.add(self.input)
        if settings.PROCESS_MEDIA_ENQUEUE_LOCALLY_IMMEDIATELY:
            from walrus.methods.input.process_media import PrioritizedItem, add_item_to_queue
            item = PrioritizedItem(
                priority = 10000,  # individual frames have a priority here.
                input_id = self.input.id,
                media_type = self.input.media_type)
            add_item_to_queue(item)

    def archive_input(self):
        """
        Caution: Also removes associated file
            Under assumption that if we are archiving an input we don't want the file.
        """

        for input in self.input_list:
            input.archived = True
            self.remove_associated_file(input)
            self.remove_copied_file(input)
            self.session.add(input)

    def remove_copied_file(self, input):
        if input.mode == 'copy_file' and input.newly_copied_file:
            input.newly_copied_file.state = "removed"
            self.log['info']['removed_copied_file_id'] = input.newly_copied_file.id

    def remove_associated_tasks(self, file):
        tasks = self.session.query(Task).filter(
            Task.file_id == file.id
        ).all()
        for task in tasks:
            task.status = 'archived'
            self.session.add(task)

    def remove_associated_file(self, input):
        """
        Take input as argument in context of trying to make these
        classes more modular, ie not "assuming" that input is in self.
        """

        if input.file and input.mode != 'copy_file':
            input.file.state = "removed"
            self.remove_associated_tasks(input.file)
            self.log['info']['prior_file_id'] = input.file.id

    def report_input_list_recent(
        self,
        include_within_x_minutes: int):
        """
        Showing all status's for now, just a way to "monitor" it so to speak?

        We could just use last updated time
            then wouldn't even need to have a "has been reported on" flag...

        We could just run this every few hours including files updated within last hour?

        In the future thinking about ways this could be personalized for individual users?
            For now more of a monitoring thing for us.

        Input time updated is inverted as we just want ones that Have been updated
        within this time

        """
        include_files_touched_within = datetime.datetime.utcnow() - \
                                       datetime.timedelta(minutes = include_within_x_minutes)

        limit = 100

        exempt_statuses = ['success', 'init']

        # Main context here is the time updated being less then
        # include_files_touched_within value

        input_list = self.session.query(Input).filter(
            Input.archived == False,
            Input.status.notin_(exempt_statuses),
            include_files_touched_within < Input.time_updated
        ).order_by(Input.time_updated.desc()).limit(limit).all()

        message = []
        message.append("\n Showing up to " + str(limit) + " of most recent (potential issues) within past: " +
                       str(include_within_x_minutes) + " minutes. \n" + " Excluded: " + \
                       str(exempt_statuses))

        date_format = 'D:%d, %H:%M'

        header_list = ["Status\t", "%",
                       "created_time", "time_updated",
                       "Filename (20 char)",
                       "ID", "Project", "project_string_id", ]

        for header in header_list:
            message.append(header + "\t")

        for input in input_list:
            message.append("\n")

            filename = None
            if input.original_filename:
                filename = input.original_filename[: 20]

            message.append(str(input.status) + "\t\t")
            message.append(str(input.percent_complete) + "\t")
            message.append(datetime.datetime.strftime(input.created_time, date_format) + "\t")
            message.append(datetime.datetime.strftime(input.time_updated, date_format) + "\t")
            message.append(str(filename) + "\t")
            message.append(str(input.id) + "\t")
            message.append(str(input.project.name) + "\t")
            message.append(str(input.project.project_string_id) + "\t")

        if input_list:
            try:
                communicate_via_email.send(
                    email = "support@diffgram.com",
                    subject = "Input report: " + str(len(input_list)) + " items.",
                    message = "".join(message)
                )
            except Exception as e:
                print("input update, communicate_via_email", e)


    def build_input_list_eligible_for_retry(self):

        normal_max_updated_since_time = datetime.datetime.utcnow() - \
                                        datetime.timedelta(minutes = 180)

        historical_limit: int = time.time() - (60 * 60 * 24)
        exempt_statuses = ['success', 'failed', 'init', 'retrying']
        
        # Dont retry update files since it can cause duplicate files or instances.
        exempt_modes = ['update', 'update_existing', 'copy_file', 'flow']

        self.input_list = self.session.query(Input).with_for_update(
            skip_locked = True).filter(
            Input.archived == False,
            Input.processing_deferred == False,
            Input.retry_count < 3,
            Input.status.notin_(exempt_statuses),
            Input.mode.notin_(exempt_modes),
            normal_max_updated_since_time > Input.time_updated,
            Input.time_last_attempted > historical_limit
        ).limit(10).all()

        if self.input_list:

            try:
                description = str(len(self.input_list)) + " retried [Auto Retry]. \n" + \
                            "First project in list: " + \
                            str(self.input_list[0].project.name) + " \n" + \
                            str(self.input_list[0].project.project_string_id) + \
                            "\n input ids: " + ", ".join([str(i.id) for i in self.input_list]) + \
                            "\n prior percent complete: " + ", ".join(
                    [str(i.percent_complete) for i in self.input_list]) + \
                            "\n created_time: " + ", ".join([str(i.created_time) for i in self.input_list]) + \
                            "\n time_updated: " + ", ".join([str(i.time_updated) for i in self.input_list])

                Event.new(
                    session=self.session,
                    kind="input_retry",
                    description=description
                )
            except:
                print("Failed to create input_rety event")



    def automatic_retry(self):

        self.build_input_list_eligible_for_retry()
        self.retry_file_list()
