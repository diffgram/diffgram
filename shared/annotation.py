# OPEN CORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *

try:
    # The walrus service doesn't have task_complete
    from default.methods.task.task import task_complete
except:
    pass

import hashlib
import bisect

from google.cloud import storage

from shared.database.user import UserbaseProject
from shared.database.image import Image
from shared.database.annotation.instance import Instance
from shared.database.label import Label
from shared.helpers.permissions import LoggedIn, defaultRedirect, get_gcs_service_account
from shared.helpers.permissions import getUserID
from shared.utils.task import task_complete
from shared.model.model_manager import ModelManager
from shared.database.video.video import Video
from shared.database.video.sequence import Sequence
from shared.database.external.external import ExternalMap
from shared.shared_logger import get_shared_logger

logger = get_shared_logger()


# need to support updating instances from both services


@dataclass
class Annotation_Update():
    session: Any
    file: Any  # Video or Image file.
    instance_list_new: list = None  # New from external
    instance: object = None  # New from external
    instance_list_existing: list = None
    instance_list_existing_dict: dict = field(default_factory = lambda: {})
    instance_list_kept_serialized: list = field(default_factory = lambda: [])
    video_data: dict = None
    project: Project = None  # Note project is Required for get_allowed_label_file_ids()
    project_id: Project = None  # add project_id for avoiding dettached session on thread processing
    task: Task = None
    complete_task: bool = False
    gold_standard_file = None
    external_auth: bool = False
    do_update_sequences: bool = True
    previous_next_instance_map: dict = field(default_factory = lambda: {})
    creating_for_instance_template: bool = False

    # Keeps a Record of the new instances that were created after the update process finish
    new_added_instances: list = field(default_factory = lambda: [])

    # Keeps a Record of the deleted instances after the update process finish
    new_deleted_instances: list = field(default_factory = lambda: [])

    directory = None
    external_map: ExternalMap = None
    external_map_action: str = None
    new_instance_dict_hash: dict = field(default_factory = lambda: {}) # Keep a hash of all
    do_create_new_file = False
    new_file = None
    frame_number = None
    video_mode = False
    is_new_file = False  # defaults to False, ie for images?
    video_parent_file = None
    clean_instances: bool = False
    sequence = None
    allowed_model_run_id_list: list = None
    allowed_model_id_list: list = None

    count_instances_changed = 0

    do_init_existing_instances: bool = True  # Set to False to "add" only.
    member: Any = None

    # TODO clarify this,
    # Basically if an existing list is not supplied
    # / not inited then this will just "add" instances
    # and not remove them...
    # this is the behaviour but need to explain better /
    # how this gets "built" normally
    hash_old_cross_reference: dict = field(default_factory = lambda: {})
    allowed_label_file_id_list: list = field(default_factory = lambda: [])
    per_instance_spec_list: list = field(default_factory = lambda: [
        {'id': {  # becomes previous_id
            'default': None,
            'kind': int,
            'required': False
        }
        },
        {'root_id': {
            'default': None,
            'kind': int,
            'required': False
        }
        },
        {'model_id': {
            'default': None,
            'kind': int,
            'required': False
        }
        },
        {'model_run_id': {
            'default': None,
            'kind': int,
            'required': False
        }
        },
        {'version': {
            'default': None,
            'kind': int,
            'required': False
        }
        },
        {'x_min': {
            'default': None,
            'kind': int
        }
        },
        {'y_min': {
            'default': None,
            'kind': int
        }
        },
        {'x_max': {
            'default': None,
            'kind': int
        }
        },

        {'y_max': {
            'default': None,
            'kind': int
        }
        },
        {'label_file_id': {
            'default': None,
            'kind': int,
            'required': True
        }
        },
        {'soft_delete': {
            'default': False,  # Ensure only 2 states False, or True for delete
            'kind': bool,
            'valid_values_list': [True, False]
        }
        },
        {'type': {
            'default': None,
            'kind': str,
            'required': True,
            'valid_values_list': ['box', 'polygon', 'point', 'cuboid', 'tag', 'line', 'text_token', 'ellipse', 'curve',
                                  'keypoints']
        }
        },
        {'rating': {
            'default': None,
            'kind': int
        }
        },
        {'sequence_id': {
            'default': None,
            'kind': int
        }
        },
        {'number': {
            'default': None,
            'kind': int
        }
        },
        {'attribute_groups': {
            'default': None,
            'kind': dict
        }
        },
        {'machine_made': {
            'default': False,
            'kind': bool
        }
        },
        {'start_char': {
            'default': None,
            'kind': int
        }
        },
        {'end_char': {
            'default': None,
            'kind': int
        }
        },
        {'start_sentence': {
            'default': None,
            'kind': int
        }
        },
        {'end_sentence': {
            'default': None,
            'kind': int
        }
        },

        {'start_token': {
            'default': None,
            'kind': int
        }
        },
        {'end_token': {
            'default': None,
            'kind': int
        }
        },
        {'sentence': {
            'default': None,
            'kind': int
        }
        },
        {'creation_ref_id': {
            'default': None,
            'kind': str
        }
        },
        {'front_face': {
            'default': None,
            'kind': dict
        }
        },
        {'rear_face': {
            'default': None,
            'kind': dict
        }
        },
        {'angle': {
            'default': None,
            'kind': float
        }
        },
        {'center_x': {
            'default': None,
            'kind': int
        }
        },
        {'center_y': {
            'default': None,
            'kind': int
        }
        },
        {'width': {
            'default': None,
            'kind': int
        }
        },
        {'height': {
            'default': None,
            'kind': int
        }
        },
        {'p1': {
            'default': None,
            'kind': dict
        }
        },
        {'p2': {
            'default': None,
            'kind': dict
        }
        },
        {'cp': {
            'default': None,
            'kind': dict
        }
        },
        {'nodes': {
            'default': [],
            'kind': list,
            'allow_empty': True
        }
        },
        {'edges': {
            'default': [],
            'kind': list,
            'allow_empty': True
        }
        },
        {'client_created_time': {
            'kind': 'datetime',
            'required': False
        }
        },
        {'change_source': {
            'kind': str,
            'required': False
        }},
        {'pause_object': {
            'kind': bool,
            'required': False
        }}
    ])

    # If we want this.
    instance_type_count_template = {
        'box': 0,
        'polygon': 0,
        'line': 0,
        'point': 0,
        'tag': 0,
        'text_token': 0
    }

    # https://diffgram.readme.io/docs/general-annotation-update

    def __post_init__(self):

        self.log = regular_log.default()
        if self.creating_for_instance_template:
            return

        if self.project is None and self.project_id is not None:
            self.project = Project.get_by_id(self.session, self.project_id)
        self.get_allowed_label_file_ids()

        self.previous_next_instance_map = {}

        if self.member is None and not self.external_auth:
            self.member = get_member(session = self.session)

        # Order dependent here

        self.init_video_input()

        self.task_update()

        self.init_file()

        self.init_existing_instances()

        self.refresh_instance_count()

    def instance_template_main(self):
        """
            This is the main flow for creating/updating
            instances within the instance template context.

        """

        if not self.instance_list_new:
            logger.error('Error, please provide instance_list_new {}'.format(str(self.log)))
            return None

        # Remove requirement for label_file_id in this case
        for elm in self.per_instance_spec_list:
            if 'label_file_id' in elm:
                elm['label_file_id']['required'] = False

        self.update_instance_list(hash_instances = False,
                                  validate_label_file = False,
                                  overwrite_existing_instances = True)

        if len(self.log["error"].keys()) >= 1:
            logger.error('Error updating annotation {}'.format(str(self.log)))
            logger.error('Instance list is: {}'.format(self.instance_list_new))
            return self.return_orginal_file_type()

        return self.new_added_instances

    def __check_all_instances_available_in_new_instance_list(self):
        if not self.do_init_existing_instances:
            return True
        new_id_list = []
        for inst in self.instance_list_new:
            if inst.get('id'):
                new_id_list.append(inst.get('id'))

        ids_not_included = []
        for instance in self.instance_list_existing:
            # We don't check for soft_deleted instances
            if instance.soft_delete:
                continue
            if instance.id not in new_id_list:
                ids_not_included.append(instance.id)

        if len(ids_not_included) > 0:
            logger.error('Invalid payload on annotation update missing IDs {}'.format(ids_not_included))
            self.log['error']['new_instance_list_missing_ids'] = 'Invalid payload sent to server, missing the following instances IDs {}'.format(
                ids_not_included
            )
            self.log['error']['information'] = 'Error: outdated instance list sent. This can happen when 2 users are working on the same file at the same time.' \
                                               'Please try reloading page, clicking the refresh file data button or check your network connection. ' \
                                               'Please contact use if this persists.'
            self.log['error']['missing_ids'] = ids_not_included
            return False
        return True

    def append_new_instance_list_hash(self, instance):

        if instance.soft_delete is False:
            self.new_instance_dict_hash[instance.hash] = instance
            return True
        return False

    def order_new_instances_by_date(self):
        self.instance_list_new.sort(key=lambda item: item.get('client_created_time'), reverse=True)
        return self.instance_list_new

    def annotation_update_main(self):

        """
        Careful, we return very early here
            if there is not a new instance list

        """

        if not self.instance_list_new and not self.clean_instances:
            return self.return_orginal_file_type()
        logger.debug('Bulding existing hash list...')

        payload_includes_all_instances = self.__check_all_instances_available_in_new_instance_list()

        if not payload_includes_all_instances:
            logger.error('Error updating annotation {}'.format(str(self.log)))
            logger.error('Instance list is: {}'.format(self.instance_list_new))
            return self.return_orginal_file_type()

        self.build_existing_hash_list()

        ### Main work

        self.update_instance_list()

        ###

        # Early exit if errors, eg from instance limits
        # This may be a little aggressive, eg maybe shuold just "warn" on instances that are invalid.
        # Primary concern in current context is that we don't delete left over ones.
        if len(self.log["error"].keys()) >= 1:
            logger.error('Error updating annotation {}'.format(str(self.log)))
            logger.error('Instance list is: {}'.format(self.instance_list_new))
            return self.return_orginal_file_type()

        self.update_file_hash()

        self.left_over_instance_deletion()

        self.instance_list_cache_update()

        if len(self.log["error"].keys()) == 0:
            self.log['success'] = True
            # logger.info('Success updating annotation {}'.format(str(self.log)))
            if self.task and self.complete_task:
                result, new_file = task_complete.task_complete(
                    session = self.session,
                    task = self.task,
                    new_file = self.file,
                    project = self.project)

        else:
            logger.error('Error updating annotation {}'.format(str(self.log)))
        return self.return_orginal_file_type()

    def main(self):
        return self.annotation_update_main()

    def __perform_external_map_action(self):
        if not self.external_map:
            return
        if self.external_map_action == 'set_instance_id':
            if self.instance:
                self.external_map.instance = self.instance
                self.session.add(self.external_map)

    def instance_list_cache_update(self):
        """
        High level idea of caching
            While going through this process, we know which instances are new
            and have the data in memory. We want to cache that data on the file
            so other processes like the video buffer can access it.

        Details:
            Specifically we assume that update_cache_single_instance_in_list_context() is called
            and serializes a single new instance.

            We assume if the instance existed that the instance serialized is the
            existing one (ie so it has ids etc)
            and if it's new, that we are doing this after flush so we have ids.

            Acceptable states for cache:
            a) Exactly Correct
            b) Empty / None
            None is from integrity perspective because it will rebuild from System of Record (Database)
            BUT we do need to ensure if it exists its correct because
            it gets "fed back" into the system from the user. (For video.)
        """
        if not self.file:
            return
        # for x in self.instance_list_kept_serialized:
        #	print(x['id'], x['soft_delete'])
        self.file.set_cache_by_key(
            cache_key = 'instance_list',
            value = self.instance_list_kept_serialized
        )

    def return_orginal_file_type(self):
        """
        Not a fan of this setup... but at least this way
        We know we aren't returning a different file...
        I think this is part of an "ongoing" question
        At least for now, front end does file replace for video
        (ie in context of Complete flag / flags)
        so we should return the video file
        """

        if self.video_parent_file:
            return self.video_parent_file

        return self.file

    def init_file(self):
        # https://diffgram.readme.io/docs/init-annotation-update

        if self.video_mode is True and self.file.type == "frame":
            self.log['error']['video_mismatch'] = "In video mode but sending frame."
            return

        # For now there is no extra init needed if it's an image
        if self.file.type == "image":
            return

        if self.file.type == "video":

            self.video_parent_file = self.file

            # Switch -> self.file becomes the frame
            # Create frame file when first instance is created
            # Can be done prior to an instance - just current way

            # Default case, file already exists.
            self.file = File.get_frame_from_video(
                session = self.session,
                video_parent_file_id = self.video_parent_file.id,
                frame_number = self.frame_number)

            if self.file:
                return

            # File does not exist, so create it.

            self.file = File.new(
                session = self.session,
                file_type = "frame",
                video_parent_file = self.video_parent_file,
                frame_number = self.frame_number,
                project_id = self.project.id,
                task = self.task
            )
            self.is_new_file = True

    def init_existing_instances(self):

        if self.is_new_file is True:
            self.instance_list_existing = []
            return

        if self.do_init_existing_instances is False:
            return
        # for performance reasons, ie if updating single instance.

        # For better performance, we can exclude remove
        # But then have to figure out how to handle the undo case - otherwise all the deleted
        # ones will get recreated. Maybe the front end should only send != soft delete ones?
        # once it gets here, we don't know if it's a new soft delete or was an existing (without checking)
        self.instance_list_existing = Instance.list(session = self.session,
                                                    file_id = self.file.id,
                                                    limit = None,
                                                    exclude_removed = False)
        for instance in self.instance_list_existing:
            self.instance_list_existing_dict[instance.id] = instance

    def get_allowed_label_file_ids(self):
        """
        This strictly a security feature

        Could also follow this "allowed" or not pattern
        # for sequences

        A perfect example of where it's nice to be able to have code that checks
        if something is in the list, and knows the list will exist...?

        """
        project = self.project
        if self.task:
            logger.info('getting project from task {}'.format(self.task.id))
            project = self.task.project

        assert project is not None

        if not project.label_dict:
            project.refresh_label_dict(self.session)
        self.allowed_label_file_id_list = project.label_dict.get('label_file_id_list')

        assert self.allowed_label_file_id_list is not None

    def validate_label_file_id(self):
        """

        """
        if self.instance.label_file_id in self.allowed_label_file_id_list:
            return True
        self.log['error']['valid_label_file'] = "Permission issue with " + \
                                                str(self.instance.label_file_id) + " label_file_id."
        return False

    def init_video_input(self):

        # TODO, we aren't actually 'raising" this error very well here.
        # Also this will fire an error "wrongly"
        # which makes a check success at the end not quite work right.

        # Currently rely on front end to send a Null dict here then?

        if not self.video_data:
            return

        # TODO, we don't actually require video  file id here anymore
        # Since we now can pass as parent file ...

        # If video data is provided it must be complete
        spec_list = [
            {'video_mode': {
                'kind': bool,
                'required': True
            }
            },
            # TODO update to video_file_id
            {'video_file_id': {
                'kind': int,
                'required': True
            }
            },
            {'current_frame': {
                'kind': int,
                'required': True
            }
            }
        ]

        self.log, input = regular_input.input_check_many(
            spec_list = spec_list,
            log = self.log,
            untrusted_input = self.video_data)

        if len(self.log["error"].keys()) >= 1:
            return False

        self.video_mode = input['video_mode']
        self.video_parent_file_id = input['video_file_id']
        self.frame_number = input['current_frame']

    def update_file_hash(self):

        # Default behavior is to set status to complete upon saving
        # TODO consideration for other ways to do this, show this etc.
        # and consideration for the default to not save unless changes flag

        # TODO this does not detect a deleted box
        # If we create a new file then the deleted boxes get ignored automatically
        # Else we are flagging soft delete in working dir right?

        # If we properly update the new file to be file
        # then we don't need to worry about separate handling

        if self.count_instances_changed > 0 and self.file:
            self.file.hash_update()

    def __build_debug_log(self):
        local_log = {}
        local_log['project_id'] = self.project.id if self.project else None
        local_log['task_id'] = self.task.id if self.task else None
        local_log['frame_number'] = self.frame_number if self.frame_number else None
        local_log['file_id'] = self.file.id if self.file else None
        local_log['date'] = str(datetime.datetime.now())
        local_log['member'] = self.member.id if self.member else None
        return local_log

    def __choose_which_duplicate_instance_to_keep(
        self,
        existing_instance,
        instance,
        duplicate_instance_indexes,
        duplicate_instances_dict,
        index
    ):

        # Log for backend / send to front end?
        if self.log.get('duplicate_instance_ids'):
            self.log['duplicate_instance_ids'].append(existing_instance.get('id'))
            self.log['duplicate_instance_refs'].append(existing_instance.get('creation_ref_id'))
        else:
            self.log['duplicate_instance_ids'] = [existing_instance.get('id')]
            self.log['duplicate_instance_refs'] = [existing_instance.get('creation_ref_id')]

        self.log['debug'] = self.__build_debug_log()
        logger.warning('Error Duplicate IDs detected on instance_list. Id is: {}'.format(existing_instance.get('id')))

        instance_created_time = instance.get('client_created_time')
        if instance_created_time is None:
            # We don't compare if it does not have client creation time, we just keep the first one we saw.
            duplicate_instance_indexes.append(index)
            return
        # Logic to get the most recently created instance on the client.

        existing_created_time = existing_instance.get('client_created_time')
        if existing_created_time is not None:
            # Basically if the new instance has a more recent time, we add the previous one
            # to the array of duplicate indexes for removal.
            if existing_created_time < instance_created_time:
                duplicate_instance_indexes.append(duplicate_instances_dict[instance.get('id')]['index'])
                duplicate_instances_dict[instance.get('id')] = {'instance': instance, 'index': index}

        elif instance_created_time is not None:
            # If the newest instance on the list does has a created_time, then use that one.
            duplicate_instance_indexes.append(duplicate_instances_dict[instance.get('id')]['index'])
            duplicate_instances_dict[instance.get('id')] = {'instance': instance, 'index': index}
        else:
            # If both instances DON't have client_created_time then just keep the first one that appeared on the list
            pass

    def __identify_and_merge_duplicate_ids(self, instance_list):
        """
        Run time / general context note:
            If there are no duplicate IDs we essentially just record IDs in dict,
            and then return reference to original list

            If there are duplicates, we attempt to use time stamp to "choose" latests
            and we inform user with the `duplicate_instance_ids` key which duplicates where detected
        """
        # Duplicate IDs case
        # Test if new instance is more recently created
        # [ ] note sure on handline null property here / null time?
        duplicate_instance_indexes = []
        duplicate_instances_dict = {}

        for i, instance in enumerate(instance_list):

            if instance.get('id') is None:  # Ignore new instance (instances with no ID)
                continue

            # Check if newly found instance or if already have seen ID
            existing_instance_dict = duplicate_instances_dict.get(instance.get('id'))
            if existing_instance_dict is None:
                duplicate_instances_dict[instance.get('id')] = {'instance': instance, 'index': i}

            else:
                self.__choose_which_duplicate_instance_to_keep(
                    existing_instance = existing_instance_dict.get('instance'),
                    instance = instance,
                    duplicate_instance_indexes = duplicate_instance_indexes,
                    duplicate_instances_dict = duplicate_instances_dict,
                    index = i
                )

        # Remove duplicate indexes
        result = []
        if len(duplicate_instance_indexes) > 0:
            for i in range(0, len(instance_list)):
                if i not in duplicate_instance_indexes:
                    result.append(instance_list[i])
        else:
            result = instance_list
        return result

    def check_allowed_model_ids(self, instance_list):
        if not self.allowed_model_id_list:
            return True
        # Check for models
        for instance in instance_list:
            if instance.get('model_id') is None:
                continue
            if instance.get('model_id') not in self.allowed_model_id_list:
                self.log['error']['model_id'] = 'Invalid model_id {} allowed models are {}'.format(
                    instance.get('model_id'),
                    self.allowed_model_id_list
                )
                return False

        return True

    def check_allowed_model_run_ids(self, instance_list):
        if not self.allowed_model_run_id_list:
            return True
        # Check for models
        for instance in instance_list:
            if instance.get('model_run_id') is None:
                continue
            if instance.get('model_run_id') not in self.allowed_model_run_id_list:
                self.log['error']['model_run_id'] = 'Invalid model_run_id {} allowed runs are {}'.format(
                    instance.get('model_run_id'),
                    self.allowed_model_run_id_list
                )
                return False

        return True

    def update_instance_list(self,
                             hash_instances = True,
                             validate_label_file = True,
                             overwrite_existing_instances = False):
        """
        Assumes an untrusted / web level context
        """

        spec_list_cuboid_face = [
            {'bot_left': {
                'kind': dict
            }
            },
            {'bot_right': {
                'kind': dict
            }
            },
            {'top_left': {
                'kind': dict
            }
            },
            {'top_right': {
                'kind': dict
            }
            },
        ]

        cleaned_instance_list = self.instance_list_new
        try:
            cleaned_instance_list = self.__identify_and_merge_duplicate_ids(self.instance_list_new)
        except Exception as exception:
            logger.warning(str(exception) + "_trace_4f36a2aa")
            communicate_via_email.send(settings.DEFAULT_ENGINEERING_EMAIL,
                                       '[Exception] Duplicate ID On Annotation_Update', str(self.log))
        valid_models = self.check_allowed_model_ids(cleaned_instance_list)
        valid_runs = self.check_allowed_model_run_ids(cleaned_instance_list)
        if not valid_models or not valid_runs:
            return False
        for instance_proposed in cleaned_instance_list:
            # For other checks that are specific to
            # to certain instance types
            self.instance_proposed = instance_proposed

            self.log, input = regular_input.input_check_many(
                spec_list = self.per_instance_spec_list,
                log = self.log,
                untrusted_input = instance_proposed)

            if len(self.log["error"].keys()) >= 1:
                return False

            if input.get('front_face'):
                self.log, cuboid_face_data = regular_input.input_check_many(
                    spec_list = spec_list_cuboid_face,
                    log = self.log,
                    untrusted_input = input.get('front_face')
                )
                if len(self.log["error"].keys()) >= 1:
                    return False
            if input.get('rear_face'):
                self.log, cuboid_face_data = regular_input.input_check_many(
                    spec_list = spec_list_cuboid_face,
                    log = self.log,
                    untrusted_input = input.get('rear_face')
                )
                if len(self.log["error"].keys()) >= 1:
                    return False

            # Not sure about including this or using timestamp
            self.log['info'][str(time.time())] = "Valid Instance Dict"

            # Pattern of creating object, but not adding to
            # To session until checked fully
            # logger.debug('Updating instance with {}'.format(input))
            parent_file_id = None
            if self.file and self.file.type == "frame":
                if self.video_parent_file:
                    parent_file_id = self.video_parent_file.id

            self.update_instance(
                type = input['type'],
                x_min = input['x_min'],
                y_min = input['y_min'],
                x_max = input['x_max'],
                y_max = input['y_max'],
                id = input['id'],
                front_face = input['front_face'],
                rear_face = input['rear_face'],
                soft_delete = input['soft_delete'],
                label_file_id = input['label_file_id'],
                number = input['number'],
                sequence_id = input['sequence_id'],
                rating = input['rating'],
                attribute_groups = input['attribute_groups'],
                start_char = input['start_char'],
                end_char = input['end_char'],
                start_sentence = input['start_sentence'],
                end_sentence = input['end_sentence'],
                start_token = input['start_token'],
                end_token = input['end_token'],
                sentence = input['sentence'],
                creation_ref_id = input['creation_ref_id'],
                machine_made = input['machine_made'],
                model_id = input['model_id'],
                model_run_id = input['model_run_id'],
                previous_id = input['id'],  # Careful, purposely different
                version = input['version'],
                root_id = input['root_id'],
                center_x = input['center_x'],
                center_y = input['center_y'],
                angle = input['angle'],
                width = input['width'],
                height = input['height'],
                p1 = input['p1'],
                p2 = input['p2'],
                cp = input['cp'],
                nodes = input['nodes'],
                edges = input['edges'],
                client_created_time = input['client_created_time'],
                change_source = input['change_source'],
                parent_file_id = parent_file_id,
                hash_instances = hash_instances,
                validate_label_file = validate_label_file,
                overwrite_existing_instances = overwrite_existing_instances,
                pause_object = input['pause_object']
            )

    def get_min_coordinates_instance(self, instance):
        logger.debug('Getting min coordinates for {} - {}'.format(instance.id, instance.type))
        if instance.type in ['box', 'polygon', 'point']:
            return instance.x_min, instance.y_min
        elif instance.type == 'line':
            return min([p['x'] for p in instance.points['points']]), min([p['y'] for p in instance.points['points']])
        elif instance.type == 'cuboid':
            # Here we assume front face as xy max
            return min(
                instance.front_face['top_right']['x'],
                instance.front_face['bot_right']['x'],
                instance.front_face['top_left']['x'],
                instance.front_face['bot_right']['x'],
                instance.rear_face['top_right']['x'],
                instance.rear_face['bot_right']['x'],
                instance.rear_face['top_left']['x'],
                instance.rear_face['bot_right']['x'],
            ), min(
                instance.front_face['top_right']['y'],
                instance.front_face['bot_right']['y'],
                instance.front_face['top_left']['y'],
                instance.front_face['bot_right']['y'],

                instance.rear_face['top_right']['y'],
                instance.rear_face['bot_right']['y'],
                instance.rear_face['top_left']['y'],
                instance.rear_face['bot_right']['y'],
            )
        elif instance.type == 'ellipse':
            return instance.center_x - instance.width, instance.center_y - instance.height
        elif instance.type == 'curve':
            # Here assumption is that one point is gonna be max and the other min
            return min(instance.p2['x'], instance.p1['x']), min(instance.p2['y'], instance.p1['y'])
        elif instance.type == 'tag':
            # Here assumption is that tag is not really a "spacial" thing so no idea for min/max applies here.
            return 0, 0
        elif instance.type == 'keypoints':
            # Here assumption is that tag is not really a "spacial" thing so no idea for min/max applies here.
            return min([p['x'] for p in instance.nodes['nodes']]), min([p['y'] for p in instance.nodes['nodes']])
        else:
            logger.error('Invalid instance type for image crop: {}'.format(instance.type))
            return None

    def get_max_coordinates_instance(self, instance):
        logger.debug('Getting max coordinates for {} - {}'.format(instance.id, instance.type))
        if instance.type in ['box', 'polygon', 'point']:
            return instance.x_max, instance.y_max
        elif instance.type == 'line':
            return max([p['x'] for p in instance.points['points']]), max([p['y'] for p in instance.points['points']])
        elif instance.type == 'cuboid':
            # Here we assume front face as xy max
            return max(
                instance.front_face['top_right']['x'],
                instance.front_face['bot_right']['x'],
                instance.front_face['top_left']['x'],
                instance.front_face['bot_right']['x'],
                instance.rear_face['top_right']['x'],
                instance.rear_face['bot_right']['x'],
                instance.rear_face['top_left']['x'],
                instance.rear_face['bot_right']['x'],
            ), max(
                instance.front_face['top_right']['y'],
                instance.front_face['bot_right']['y'],
                instance.front_face['top_left']['y'],
                instance.front_face['bot_right']['y'],

                instance.rear_face['top_right']['y'],
                instance.rear_face['bot_right']['y'],
                instance.rear_face['top_left']['y'],
                instance.rear_face['bot_right']['y'],
            )
        elif instance.type == 'ellipse':
            return instance.center_x + instance.width, instance.center_y + instance.height
        elif instance.type == 'curve':
            # Here assumption is that one point is gonna be max and the other min
            return max(instance.p2['x'], instance.p1['x']), max(instance.p2['y'], instance.p1['y'])
        elif instance.type == 'tag':
            # Here assumption is that tag is not really a "spacial" thing so no idea for min/max applies here.
            return 0, 0
        elif instance.type == 'keypoints':
            # Here assumption is that tag is not really a "spacial" thing so no idea for min/max applies here.
            return max([p['x'] for p in instance.nodes['nodes']]), max([p['y'] for p in instance.nodes['nodes']])
        else:
            logger.error('Invalid instance type for image crop: {}'.format(instance.type))
            return None

    def update_instance(self,
                        type: str,
                        x_min: int,
                        y_min: int,
                        x_max: int,
                        y_max: int,
                        label_file_id: int,
                        id = None,
                        front_face: dict = None,
                        rear_face: dict = None,
                        soft_delete: bool = False,
                        number: int = None,
                        sequence_id: int = None,
                        rating = None,
                        attribute_groups = None,
                        interpolated = False,
                        machine_made = False,
                        start_char = None,
                        end_char = None,
                        start_sentence = None,
                        end_sentence = None,
                        start_token = None,
                        end_token = None,
                        sentence = None,
                        creation_ref_id = None,
                        model_id = None,
                        model_run_id = None,
                        previous_id = None,
                        version = None,
                        root_id = None,
                        center_x = None,
                        center_y = None,
                        angle = None,
                        width = None,
                        height = None,
                        change_source = None,
                        parent_file_id = None,
                        client_created_time = None,
                        cp = None,
                        p1 = None,
                        p2 = None,
                        nodes = [],
                        edges = [],
                        hash_instances = True,
                        overwrite_existing_instances = True,
                        validate_label_file = True,
                        pause_object = None):
        """
        Assumes a "system" level context

        if we moved the 4 box attributes into a single thing this would feel a lot smoother
        This doesn't include points yet since in other setting that gets added later...

        The reason we need a separate update_instance method like this,
        is because other internal functions may need to call it
        (ie Interpolate)
        I'm really trying to avoid passing so many arguments
        but I don't yet see a generic way around this
        And it seems silly to require the input to be in a say a "dict" form like from
        input...

        TODO clarify what needs to be init for this to work if called separately.

        sequence_id / number
        Careful! This doesn't that directly
        so need to add both together if adding directly
        (and not as part of say .main() where sequence update gets
        called for HUMAN updated ones.) that part still needs clarification

        """
        member_created_id = None
        if self.member:
            member_created_id = self.member.id

        if self.file:
            logger.debug('Creating Instance with file id: {}'.format(self.file.id))
            logger.debug('Creating Instance with project id: {}'.format(self.file.project.id))
            logger.debug('Creating Instance with type: {}'.format(type))
            logger.debug(
                'Creating Instance with TOKENS: {} {} {} {}'.format(start_sentence, end_sentence, end_char, start_char))
        if version is None:
            version = 0
        version += 1
        instance_attrs = {
            'file_id': self.file.id if self.file else None,
            'project_id': self.file.project_id if self.file else None,
            'frame_number': self.frame_number,
            'member_created_id': member_created_id,
            'global_frame_number': self.file.global_frame_number if self.file else None,
            'task': self.task,  # for stats
            'type': type,
            'x_min': x_min,
            'y_min': y_min,
            'x_max': x_max,
            'y_max': y_max,
            'front_face': front_face,
            'rear_face': rear_face,
            'soft_delete': soft_delete,
            'change_source': change_source,
            'label_file_id': label_file_id,
            'number': number,
            'sequence_id': sequence_id,
            'rating': rating,
            'attribute_groups': attribute_groups,
            'interpolated': interpolated,
            'client_created_time': client_created_time,
            'machine_made': machine_made,
            'start_char': start_char,
            'end_char': end_char,
            'parent_file_id': parent_file_id,
            'start_sentence': start_sentence,
            'end_sentence': end_sentence,
            'start_token': start_token,
            'end_token': end_token,
            'sentence': sentence,
            'creation_ref_id': creation_ref_id,
            'model_id': model_id,
            'model_run_id': model_run_id,
            'previous_id': previous_id,
            'version': version,
            'root_id': root_id,
            'center_x': center_x,
            'center_y': center_y,
            'angle': angle,
            'width': width,
            'height': height,
            'cp': cp,
            'p1': p1,
            'p2': p2,
            'nodes': {'nodes': nodes},
            'edges': {'edges': edges},
            'pause_object': pause_object
        }

        if overwrite_existing_instances and id is not None:
            self.instance = self.session.query(Instance).filter(Instance.id == id).first()
            for key, value in instance_attrs.items():
                setattr(self.instance, key, value)
        else:
            self.instance = Instance(**instance_attrs)

        self.instance_limits(validate_label_file = validate_label_file)

        if len(self.log["error"].keys()) >= 1:
            logger.error('Error on instance creation {}'.format(self.log))
            return False

        # After instance limits to make sure points are available.
        deducted_x_min, deducted_y_min = self.get_min_coordinates_instance(self.instance)
        deducted_x_max, deducted_y_max = self.get_max_coordinates_instance(self.instance)
        self.instance.x_min = int(deducted_x_min)
        self.instance.y_min = int(deducted_y_min)
        self.instance.x_max = int(deducted_x_max)
        self.instance.y_max = int(deducted_y_max)

        if len(self.log["error"].keys()) >= 1:
            logger.error('Error on instance creation {}'.format(self.log))
            return False

        """
        CAUTION
        Any condition above self.instance.hash_instance() may only be varied by the user.

        Because this runs on all instances - including historical (to build the hash comparison).
        So if we vary it with something like a data - we are essentially guaranteeing it will vary and be different.
        See https://github.com/diffgram/training_data/pull/140#issuecomment-745062821
        """
        # Here we assume that instance template will not have a hast (since we don't need versioning here)
        if hash_instances:
            self.instance.hash_instance()

        is_new_instance = self.determine_if_new_instance_and_update_current()

        try:  # wrap new concept in try block just in case
            self.instance = self.__validate_user_deletion(self.instance)
        except Exception as e:
            logger.error(str(e) + ' trace_82j2j__validate_user_deletion')
            communicate_via_email.send(settings.DEFAULT_ENGINEERING_EMAIL, '[Exception] __validate_user_deletion',
                                       str(self.log))

        self.__perform_external_map_action()

        self.update_cache_single_instance_in_list_context()
        logger.debug('is_new_instance {}'.format(is_new_instance))
        if is_new_instance is False:
            return

        # Stuff that's only relevant if a new instance was created:

        # This condition is super important! If we allow soft deleted instances to be counted,
        # we'll end up with a number 2x the amount of instances!
        action_type = 'new_instance'
        if self.instance.previous_id is None:
            self.instance.action_type = 'created'
            self.session.add(self.instance)
        else:
            if self.instance.action_type is None:
                self.instance.action_type = 'edited'
                self.session.add(self.instance)
        if not self.instance.soft_delete:
            self.update_instance_count(action_type = action_type)

        self.instance_count_updates()

        self.sequence_update(instance = self.instance)

    def update_cache_single_instance_in_list_context(self):
        """
        CAUTION this assumes that instance_list_kept_serialized will exist etc
         that we are operating on a list of instances, not just a single instance
         (ie in interpolation context.)

        Wary of having objects here since self.instance
        will keep changing, and not a need to "copy" this yet.
        Not sure if this is a good way to do it or not.

        Assumes it's running after determine_if_new_instance_and_update_current()
        since that updates self.instance if it exists
        """
        # Prevent from adding the same instances with ID None (cases where list has the same instance twice)
        # And both instances have the same hash and no ID.
        if self.instance.id is None:
            return
        serialized_data = self.instance.serialize_with_label()
        self.instance_list_kept_serialized.append(serialized_data)

    def instance_count_updates(self):
        if self.file is None:
            return

        if not self.file.instance_type_count:
            self.file.instance_type_count = self.instance_type_count_template
        if not self.file.count_instances_changed:
            self.file.count_instances_changed = 0

        if not self.file.instance_type_count.get(self.instance.type):
            self.file.instance_type_count[self.instance.type] = 1
        else:
            self.file.instance_type_count[self.instance.type] += 1
        self.file.count_instances_changed += 1

    def refresh_instance_count(self):
        """
        For now we assume that if we have initialized the existing instance list
        that we wish to refresh this value.
        """
        if self.do_init_existing_instances is False:
            return

        self.file.count_instances = 0
        for instance in self.instance_list_existing:
            if instance.soft_delete is False:
                self.file.count_instances += 1

    def update_instance_count(self, action_type = None):
        """
            Performs an update of a  new instance count for the current file.
            The self.file.count_instances is a cached value that represents
            the number of instances in the file that have not been deleted (soft_delete=True)..
        @:param action_type: 'new_instance', 'deleted_instance'
        :return:
        """
        if self.file is None:
            return

        if self.file.count_instances is None:  # just in case, should not be needed
            self.file.count_instances = 0

        if action_type == 'new_instance':
            self.file.count_instances += 1

        elif action_type == 'delete_instance':
            self.file.count_instances -= 1
            # Add this case to prevent having negative counts.
            if self.file.count_instances < 0:
                self.file.count_instances = 0

    def may_create_new_file_old_source_control(self):

        """
        This is part of original source control idea
        It still may be useful for new ideas
        """

        if file.committed is True:
            self.do_create_new_file = True

        if self.do_create_new_file is True:
            # TODO not a great naming convention here
            # Maybe file should just be file
            # and then handle other related concerns seperetly
            self.file = File.copy_file_from_existing(
                self.session, directory, self.file)

    def instance_limits(self, validate_label_file = True):
        """
        I'm not a huge fan of having so many self.instance things
        but don't see a great alterative...
        """
        if validate_label_file:
            if self.validate_label_file_id() is False:
                return False

        # Any other "prep" work for files?
        if self.instance.type == "box":
            assert self.instance.x_min is not None

        if self.instance.type in ["polygon", "point", "line"]:

            spec_list = [{'points': {
                'default': None,
                'kind': list,
                'required': True,
                'empty': False
            }
            }]

            self.log, input = regular_input.input_check_many(
                spec_list = spec_list,
                log = self.log,
                untrusted_input = self.instance_proposed)

            if len(self.log["error"].keys()) >= 1:
                return False

            self.instance.points = {'points': input['points']}  # Due to dict storing funnyness

            # this assert is kinda silly now that we are running this right here...
            assert self.instance.points is not None

            result = self.check_polygon_points_and_build_bounds()
            if result is False: return

        if self.instance.type in ["box", "polygon"]:

            # TODO clarify when exactly "rounding" is needed here
            # Maybe have been for polygon thing or something??
            self.instance.x_min = round(self.instance.x_min)
            self.instance.y_min = round(self.instance.y_min)
            self.instance.y_max = round(self.instance.y_max)
            self.instance.x_max = round(self.instance.x_max)

            self.instance.x_min = max(0, self.instance.x_min)
            self.instance.y_min = max(0, self.instance.y_min)

            # How do we want to handle the "max" value
            # We can use file.image.width / file.image.height
            # But don't really want to have to make an extra hop for every save.
            # May want this as some kind of optional thing like
            # "strict checking enabled" or something

            self.instance.width = self.instance.x_max - self.instance.x_min
            self.instance.height = self.instance.y_max - self.instance.y_min
            if self.instance.width < 1:
                self.log['error']['width'] = "Width: {} less than 1 pixels or negative. xmin: {} xmax: {}".format(
                    str(self.instance.width),
                    str(self.instance.x_min),
                    str(self.instance.x_max),

                )
                return False

            if self.instance.height < 1:
                self.log['error']['height'] = "height: {} less than 1 pixels or negative. xmin: {} xmax: {}".format(
                    str(self.instance.height),
                    str(self.instance.y_min),
                    str(self.instance.y_max),

                )
                return False

            if self.instance.x_min > self.instance.x_max:
                self.log['error']['x_min'] = "x_min " + \
                                             str(self.instance.x_min) + " > x_max" + str(self.instance.x_max)
                return False

            if self.instance.y_min > self.instance.y_max:
                self.log['error']['y_min'] = "y_min " + \
                                             str(self.instance.y_min) + " > y_max" + str(self.instance.y_max)
                return False

    def determine_if_new_instance_and_update_current(self):
        """
        Key point here is that the first pass through the list,
        we don't know which ones to delete
        We only know which ones we can add.

        Three cases

        * The hash matches. This means that the instance already exists.
        * The hash doesn't exist. This means it's a new instance.
        * AFTER we go through all the instances, if the hash still exists, then
        it's an "old" instance..

        From this perspective, any "new" instance that didn't previously
        have a matching hash gets created
        And any "old" instances get deleted (after done pass on instance list)

        If the hash of the instance already exists,
        then there is no need to add the instance as it already exists.

        The concept of an instance being deleted on the front end is
        only relevant in the form of it being an attribute.

        The show removed works IF the instance is an exact match
        for everything but show removed,
        but if it's just a different isntance, then the "old" instance
        gets deleted? I still feel a bit confused on that

    Try block because occasionally it's possible that the hash won't
            be in the list. this appears to happen if there are duplicate
            instances, ie instances with the same hash

        """
        is_new_instance = True
        if self.instance.soft_delete is False and self.new_instance_dict_hash.get(self.instance.hash) is not None:
            # This case can happen when 2 instances with the exact same data are sent on instance_list_new.
            # We only want to keep one of them.
            logger.warning('Got duplicated hash {}'.format(self.instance.hash))
            is_new_instance = False
            # The instance_dict hash will always have the newest instance (sorted by created_time)
            existing_instance = self.new_instance_dict_hash[self.instance.hash]
            self.instance = existing_instance
            return is_new_instance
        else:
            # Add the instance hash if the instance is soft_delete False
            self.append_new_instance_list_hash(self.instance)

        self.existing_instance_index = self.hash_old_cross_reference.get(self.instance.hash)
        # print('existing index', self.existing_instance_index)
        if self.existing_instance_index is not None:

            is_new_instance = False
            # the current self.instance is the newly created one,
            # which is created so we can get hash that's the same.
            # but we don't persist it if it already exists
            # here we update current instance to existing instance,
            # that way it should be exactly consistent from caching perspective, ie for id
            existing_instance = self.instance_list_existing[self.existing_instance_index]
            self.instance = existing_instance
            try:
                self.hash_list.remove(self.instance.hash)
            # logger.info("Removed str(self.instance.hash))
            except:
                self.log['info']['hash_list'] = "No instance to remove."

            # In this case instance is NOT a new instance, because hash already exists.
            return is_new_instance


        # TODO maybe look at pulling this into it's own function

        # Only add instance to session if it's new.
        # Keep a separate record of the newly added instances.

        self.session.add(self.instance)
        self.session.flush()
        if self.file:
            self.session.add(self.file)

        if self.instance.previous_id is None and not self.creating_for_instance_template:
            self.instance.root_id = self.instance.id
            self.previous_next_instance_map[self.instance.previous_id] = self.instance.id

        self.new_added_instances.append(self.instance)
        return is_new_instance

    def __validate_user_deletion(self, instance):
        """
            Determines and sets the deletion_type to user if the previouse instance was not deleted
            and new version is.
            This is assumed to be a helper function of the main algorithm and is not intended for use
            outside this class. Main assumption is that we know the system deletion has not happened yet
            at this point so we know that the soft_delete current value was provided by the client and
            not set by the system (which happens at a next step.)
        :param instance:
        :return:
        """
        if not self.do_init_existing_instances:
            return instance
        # Here we want to determine if the instance was deleted by the user or not by checking the previous ID
        if instance.previous_id is not None:
            previous_instance = self.instance_list_existing_dict.get(self.instance.previous_id)
            if not previous_instance:
                return instance

            if previous_instance.soft_delete is False and instance.soft_delete is True:
                previous_instance.deletion_type = 'user'
                self.instance.action_type = 'deleted'
                self.session.add(previous_instance)
                self.session.add(self.instance)
            if previous_instance.soft_delete is True and instance.soft_delete is False:
                self.instance.action_type = 'undeleted'
                self.session.add(previous_instance)
                self.session.add(self.instance)
        return instance

    def task_update(self):
        """
        careful, if we do end up changing the file here this needs to run
        before file_init () or handle the parent video vs image better...

        Caution, this assumes that file is the 'parent' file,
        ie video or image.
        if this is run after when it's an image then it will create issues
        ie just returning an image.

        The context is that IF we want to do this here (instead of a time of provisioning) so we can copy
        instances for review file

        Context of realizing it was resetting it to an image / copying
        image and that was a lot of the confusion.

        """

        if not self.task:
            return

        if self.task.task_type == 'review':

            # if self.task.file_id == self.task.root(self.session).file_id:			# and not yet new file

            # this was moved to task_new.py
            #	pass

            if self.task.job_type == "Exam":
                # Not sure if this is a good way to do it or not,
                # assumption is that the everything else is "frozen" so this
                # is just a way to track things like "missing" attribute?

                # Context of a process (human, auto etc) marking an instance
                # from the gold standard. ie "missing" flag (could be others)
                # Many exams to original gold standard which we can't modify
                # And don't want to create a ton of new instances / files
                # (alternative is to make a copy of the gold standard file for everything
                # but that seems like over kill and could confuse things since it's not really changing...

                self.task.gold_standard_file = self.gold_standard_file

                task_exam_stats(task = self.task,
                                instance_list = self.instance_list_new)

    def sequence_update(self,
                        instance = None,
                        update_existing_only = False):
        logger.debug('Checking update sequence: video_mode:{} interpolated:{} machine_made:{}'.format(self.video_mode,
                                                                                                      self.instance.interpolated if self.instance else None,
                                                                                                      self.instance.machine_made if self.instance else None))
        if self.video_mode is False:
            return

        if self.instance.interpolated is True:
            return

        if self.instance.machine_made is True:
            return

        if self.do_update_sequences is False:
            return

        logger.debug('Updating sequence Mode:{} Instance:{} VideoParent:{}'.format(self.video_mode,
                                                                                   self.instance.id,
                                                                                   self.video_parent_file))

        """
        in new context can be *multiple* sequences
        (eg current and prior) that get updated in one save 
        suggest following the pattern of add_instances and using a list
        and then serializing and returning that list.
        Because it's now updating in the deleted contexts
        """

        # For "Human" updates only
        if update_existing_only is False:

            self.sequence = Sequence.update(
                session = self.session,
                project = self.project,
                video_mode = self.video_mode,
                instance = instance,
                video_file = self.video_parent_file
            )

        else:
            # Eg for deleting when sequence is changed on existing instance
            sequence = Sequence.update_single_existing_sequence(
                session = self.session,
                instance = instance,
                video_file = self.video_parent_file
            )

    def check_polygon_points_and_build_bounds(self):
        """
        TODO state goal of this / clarify motivation / need

        # POLYGON
        # This is for box building for mask rcnn, maybe seperate function?
        # [ ] Is this the same as coco bounding box? would want to test that I guess
        """
        self.instance.x_min = 99999
        self.instance.x_max = 0
        self.instance.y_min = 99999
        self.instance.y_max = 0

        x = "x"  # context of potential future support for other formats
        y = "y"

        filtered_points = []
        for index, point in enumerate(self.instance.points['points']):

            if not isinstance(point, dict) or point[x] is None or point[y] is None:
                continue

            filtered_points.append(
                {"x": point[x],
                 "y": point[y]})

            if point[x] <= self.instance.x_min: self.instance.x_min = point[x]
            if point[x] >= self.instance.x_max: self.instance.x_max = point[x]
            if point[y] <= self.instance.y_min: self.instance.y_min = point[y]
            if point[y] >= self.instance.y_max: self.instance.y_max = point[y]

        # We could make this more generic but would ahve to include
        # The type, the operator, the count, and the message

        if self.instance.type == "polygon":
            if len(filtered_points) <= 1:
                self.log['error']['filtered_points'] = "1 or less points."
                return False

        elif self.instance.type == "point":
            if len(filtered_points) != 1:
                self.log['error']['filtered_points'] = "Must be one point"
                return False

        elif self.instance.type == "line":
            if len(filtered_points) != 2:
                self.log['error']['filtered_points'] = "Must be two points"
                return False

        self.instance.points['points'] = filtered_points
        return True

    def build_existing_hash_list(self):
        """
        hash_old_cross_reference
        given an existing hash value returns index value in existing array
        ie  hash of   hash_old_cross_reference[abc] == 2
        if the hash value of object 2 is abc

        """
        if self.instance_list_existing is None:
            return

        self.hash_list = []
        for index, item in enumerate(self.instance_list_existing):
            self.hash_list.append(item.hash)
            self.hash_old_cross_reference[item.hash] = index

    # Would be curious to have this as like a "log level" or something

    def left_over_instance_deletion(self):
        """
        clean up old items that didn't match
        Use cross reference list for constant time operation here

        """
        if self.instance_list_existing is None:
            return
        for remaining_hash in self.hash_list:
            index = self.hash_old_cross_reference[remaining_hash]
            instance = self.instance_list_existing[index]

            prior_hash = instance.hash

            instance.soft_delete = True
            if instance.deletion_type is None:
                instance.deletion_type = 'system_deletion'
            instance.next_id = self.previous_next_instance_map.get(instance.id)
            # We need to rehash the instance in order to have the soft_delete and next_id be part of the hash.
            instance.hash_instance()

            # logger.info(instance.hash == prior_hash)

            if instance.hash != prior_hash:
                self.declare_newly_deleted_instance(instance = instance)

    def declare_newly_deleted_instance(
        self,
        instance):

        logger.info("Newly Deleted")

        self.new_deleted_instances.append(instance.id)

        self.update_instance_count(action_type = 'delete_instance')

        # Prevent from updating the original deletion time.
        if not instance.deleted_time:
            instance.deleted_time = datetime.datetime.utcnow()

        self.sequence_update(
            instance = instance,
            update_existing_only = True)

        self.count_instances_changed += 1

        self.session.add(instance)


######################################################################################################
######################################################################################################
######################################################################################################


def task_annotation_update(
    session,
    task_id: int,
    input,
    untrusted_input,
    task = None):
    # In context of already having the {task} object,
    # ie for newly created stuff... (to prevent race conditions)
    if not task:
        task = Task.get_by_id(session = session,
                              task_id = task_id)
        if not task:
            return False

    # TODO Why are we adding this to session here? not clear
    session.add(task)

    project = task.project

    instance_list_new = untrusted_input.get('instance_list', None)
    gold_standard_file = untrusted_input.get('gold_standard_file', None)

    annotation_update = Annotation_Update(
        session = session,
        task = task,
        file = task.file,
        project = project,
        instance_list_new = instance_list_new,
        video_data = input['video_data'],
        do_init_existing_instances = True
    )

    new_file = annotation_update.main()

    if input['and_complete'] is True:
        result, new_file = task_complete.task_complete(
            session = session,
            task = task,
            new_file = new_file,
            project = project)

    return new_file.serialize_with_type(session), annotation_update


def task_exam_stats(task,
                    instance_list):
    # careful instance_list is a dict here not python object yet
    # (so need to call .get() instead of .attribute
    # Not sure if this is right place to put it

    task.review_star_rating_average = 0.0

    # gold standard file is a cached dict
    # careful to use those methods instead ".attribute"
    if task.gold_standard_file['instance_list']:

        task.gold_standard_missing = 0

        for instance in task.gold_standard_file['instance_list']:

            missing = instance.get('missing', None)
            if missing == True:
                task.gold_standard_missing += 1

    sum_ratings = 0
    count_ratings = 0
    # What about soft deletes?

    if len(instance_list) > 0:

        for instance in instance_list:

            rating = instance.get('rating', None)
            if rating:
                sum_ratings += rating
                count_ratings += 1

        task.review_star_rating_average = sum_ratings / count_ratings


# From STUDIO
def annotation_update_web(
    session,
    project_string_id,
    file_id):
    data = request.get_json(force = True)  # Force = true if not set as application/json'

    if file_id is None: return "error file_id is None", 400

    instance_list_new = data.get('instance_list', None)
    and_complete = data.get('and_complete', None)

    project = Project.get(session, project_string_id)
    user = User.get(session)

    file = File.get_by_id_and_project(
        session = session,
        project_id = project.id,
        file_id = file_id)

    # If file permission error make sure it's sending image_file
    # and not video file.
    # We can't use jsonify here yet
    if file is None: return "error file_id permission", 400

    video_data = data.get('video_data', None)

    annotation_update = Annotation_Update(
        session = session,
        file = file,
        project = project,
        instance_list_new = instance_list_new,
        video_data = video_data
    )
    """
    TODO
    Do we want more clarity in terms of how it's
    "Converting" the file back into a video?
    it's kind of confusing because this could return a video
    and flags could convert it back...

    """

    new_file = annotation_update.main()

    if and_complete is True:
        new_file = new_file.toggle_flag_shared(session)

    Event.new(
        session = session,
        kind = "annotation_update",
        member_id = user.member_id,
        project_id = project.id,
        file_id = new_file.id,
        description = "Changed " + str(new_file.count_instances_changed)
    )

    return new_file.serialize_with_type(session), annotation_update
