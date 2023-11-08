import datetime, time
from shared.communicate.email import communicate_via_email
from dataclasses import dataclass, field
from shared.database.user import User
from shared.database.project import Project
from shared.database.task.task import Task
from typing import Any
from shared.regular import regular_log
from shared.regular import regular_input
from shared.regular.regular_member import get_member
from shared.database.event.event import Event
from shared.database.source_control.file import File
from shared.settings import settings
from shared.database.source_control.file_stats import FileStats
from flask import request
try:
    # The walrus service doesn't have task_complete
    from shared.methods.task.task import task_complete
except:
    pass

import hashlib
import bisect

from google.cloud import storage

from shared.database.user import UserbaseProject
from shared.database.image import Image
from shared.database.annotation.instance import Instance
from shared.database.labels.label import Label
from shared.helpers.permissions import LoggedIn, defaultRedirect, get_gcs_service_account
from shared.helpers.permissions import getUserID
from shared.utils.task import task_complete
from shared.model.model_manager import ModelManager
from shared.database.video.video import Video
from shared.database.video.sequence import Sequence
from shared.database.external.external import ExternalMap
from shared.shared_logger import get_shared_logger
import traceback
from typing import Optional
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
    video_data: Optional[dict] = None
    project: Project = None  # Note project is Required for get_allowed_label_file_ids()
    project_id: int = None  # add project_id for avoiding dettached session on thread processing
    task: Optional[Task] = None
    complete_task: bool = False
    gold_standard_file = None
    external_auth: bool = False
    do_update_sequences: bool = True
    previous_next_instance_map: dict = field(default_factory = lambda: {})
    serialized_ids_map: dict = field(default_factory = lambda: {})
    creating_for_instance_template: bool = False

    # Keeps a Record of the new instances that were created after the update process finish
    new_added_instances: list = field(default_factory = lambda: [])

    # Keeps a Record of the deleted instances after the update process finish
    new_deleted_instances: list = field(default_factory = lambda: [])
    # This array will keep track of any new instance relations that did not have instance IDs
    new_instance_relations_list_no_ids: dict = field(default_factory = lambda: [])

    duplicate_hash_new_instance_list: list = field(default_factory = lambda: [])
    system_upgrade_hash_changes: list = field(default_factory = lambda: [])

    directory = None
    external_map: Optional[ExternalMap] = None
    external_map_action: Optional[str] = None
    new_instance_dict_hash: dict = field(default_factory = lambda: {})  # Keep a hash of all
    do_create_new_file = False
    set_parent_instance_list = False
    new_file = None
    frame_number = None
    video_mode = False
    is_new_file = False  # defaults to False, ie for images?
    video_parent_file = None
    clean_instances: bool = False
    force_lock: bool = True
    sequence = None
    new_created_sequence_list: list = field(default_factory = lambda: [])
    allowed_model_run_id_list: list = None
    allowed_model_id_list: list = None
    added_sequence_ids: list = field(default_factory = lambda: [])

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
            'valid_values_list': ['box',
                                  'polygon',
                                  'point',
                                  'geo_point',
                                  'geo_circle',
                                  'geo_polyline',
                                  'geo_polygon',
                                  'geo_box',
                                  'cuboid',
                                  'tag',
                                  'line',
                                  'text_token',
                                  'ellipse',
                                  'curve',
                                  'keypoints',
                                  'cuboid_3d',
                                  'global',
                                  'relation',
                                  'audio'
                                  ]
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
        {
            'start_time': {
                'default': None,
                'kind': float
            }
        },
        {
            'end_time': {
                'default': None,
                'kind': float
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
        {'rotation_euler_angles': {
            'default': None,
            'kind': dict
        }
        },
        {'position_3d': {
            'default': None,
            'kind': dict
        }
        },
        {'center_3d': {
            'default': None,
            'kind': dict
        }
        },
        {'dimensions_3d': {
            'default': None,
            'kind': dict
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
        }},
        {'from_instance_id': {
            'kind': int,
            'required': False
        }},
        {'to_instance_id': {
            'kind': int,
            'required': False
        }},
        {'from_creation_ref': {
            'kind': str,
            'required': False
        }},
        {'to_creation_ref': {
            'kind': str,
            'required': False
        }},
        {'text_tokenizer': {
            'kind': str,
            'required': False
        }},
        {'lonlat': {
            'kind': list,
            'required': False
        }},
        {'coords': {
            'kind': list,
            'required': False
        }},
        {'radius': {
            'kind': float,
            'required': False
        }},
        {'bounds': {
            'kind': list,
            'required': False
        }},
        {'bounds_lonlat': {
            'kind': list,
            'required': False
        }},
        {'score': {
            'kind': float,
            'required': False
        }},

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

    # Tested
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

    # Tested
    def instance_template_main(self):
        """
            This is the main flow for creating/updating
            instances within the instance template context.

        """

        if not self.instance_list_new:
            logger.error(f"Error, please provide instance_list_new {str(self.log)}")
            return None

        # Remove requirement for label_file_id in this case
        for elm in self.per_instance_spec_list:
            if 'label_file_id' in elm:
                elm['label_file_id']['required'] = False

        self.update_instance_list(hash_instances = False,
                                  validate_label_file = False,
                                  overwrite_existing_instances = True)

        if len(self.log["error"].keys()) >= 1:
            logger.error(f"Error updating annotation {str(self.log)}")
            logger.error(f"Instance list is: {self.instance_list_new}")
            return self.return_orginal_file_type()

        return self.new_added_instances

    # Tested
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
            frame_numbers_instance_list_new = [x.get('frame_number') for x in self.instance_list_new]
            logger.error(f"Invalid payload on annotation update. Frontend missing IDs {ids_not_included}")
            if self.video_mode == True:
                logger.error(f"Frame Number {self.frame_number}")
                logger.error(f"frame_numbers_instance_list_new: {frame_numbers_instance_list_new}")
            logger.error(f"File ID {self.file.id}")
            self.log['warning'] = {}
            self.log['warning'][
                'new_instance_list_missing_ids'] = 'Invalid payload sent to server, missing the following instances IDs {}'.format(
                ids_not_included
            )
            self.log['warning'][
                'information'] = 'Error: outdated instance list sent. This can happen when 2 users are working on the same file at the same time.' \
                                 'Please try reloading page, clicking the refresh file data button or check your network connection. ' \
                                 'Please contact use if this persists.'
            self.log['warning']['missing_ids'] = ids_not_included
            self.log['warning']['instance_list_new'] = self.instance_list_new
            self.log['warning']['frame_number'] = self.frame_number
            self.log['warning']['instance_list_existing_ids'] = [x.id for x in self.instance_list_existing]
            # TODO: Temporarly removing this hard block since it's causing lots of user experience issue during annotation process
            # We record this a an event and revisit it in the future
            Event.new(
                session = self.session,
                project_id = self.project_id,
                file_id = self.file.id if self.file else None,
                task_id = self.task.id if self.task else None,
                kind = "missing_ids_in_new_instance_list_error",
                member_id = self.member.id if self.member else None,
                error_log = self.log,
                success = False)
            # Do not return an error state for now, we are recording the event.
            # return False
        return True

    # Tested
    def append_new_instance_list_hash(self, instance):
        if instance.soft_delete is False:
            self.new_instance_dict_hash[instance.hash] = instance
            return True
        return False

    # Tested
    def order_new_instances_by_date(self):
        self.instance_list_new.sort(
            key = lambda item: (item.get('client_created_time') is not None, item.get('client_created_time')),
            reverse = True)
        return self.instance_list_new

    # Tested
    def annotation_update_main(self):

        """
        Careful, we return very early here
            if there is not a new instance list

        """

        if not self.instance_list_new and not self.clean_instances:
            return self.return_orginal_file_type()
        logger.debug('Bulding existing hash list...')

        self.instance_list_new = self.order_new_instances_by_date()
        payload_includes_all_instances = self.__check_all_instances_available_in_new_instance_list()

        if not payload_includes_all_instances:
            logger.error(f"Error updating annotation {str(self.log)}")
            logger.error(f"Instance list is: {self.instance_list_new}")
            return self.return_orginal_file_type()

        self.build_existing_hash_list()

        ### Main work

        self.update_instance_list()
        self.add_missing_ids_to_new_relations()
        ###

        # Early exit if errors, eg from instance limits
        # This may be a little aggressive, eg maybe shuold just "warn" on instances that are invalid.
        # Primary concern in current context is that we don't delete left over ones.
        if len(self.log["error"].keys()) >= 1:
            logger.error(f"Error updating annotation {str(self.log)}")
            logger.error(f"Instance list is: {self.instance_list_new}")
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
                    project = self.project,
                    member = self.member)

        else:
            logger.error(f"Error updating annotation {str(self.log)}")
        return self.return_orginal_file_type()

    def main(self):
        return self.annotation_update_main()

    # Tested
    def __perform_external_map_action(self):
        if not self.external_map:
            return
        if self.external_map_action == 'set_instance_id':
            if self.instance:
                self.external_map.instance = self.instance
                self.session.add(self.external_map)

    # Tested
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
        self.file.set_cache_by_key(
            cache_key = 'instance_list',
            value = self.instance_list_kept_serialized
        )

        FileStats.update_file_stats_data(
            session = self.session,
            instance_list = self.instance_list_kept_serialized,
            file_id = self.file.id,
            project = self.project
        )

    # Tested
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
            if self.force_lock:
                try:
                    self.file = File.get_by_id(session = self.session,
                                               file_id = self.file.id,
                                               with_for_update = True,
                                               nowait = True)
                except Exception as e:
                    self.log['error'][
                        'file_lock'] = "File is locked or being saved by another user, please try saving again."
                    self.log['error']['trace'] = traceback.format_exc()
            return

        if self.file.type == "video":

            self.video_parent_file = self.file

            # Switch -> self.file becomes the frame
            # Create frame file when first instance is created
            # Can be done prior to an instance - just current way

            # If this is set to true, we'll attach the instance list to the video parent file
            if self.set_parent_instance_list:
                self.file = self.video_parent_file
            else:
                # Default case, file already exists.
                self.file = File.get_frame_from_video(
                    session = self.session,
                    video_parent_file_id = self.video_parent_file.id,
                    frame_number = self.frame_number,
                    with_for_update = True,
                    nowait = True
                )

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
    
    # Tested
    def detect_and_remove_collisions(self, instance_list):
        result = []
        hashes_dict = {}
        instance_list.sort(key = lambda item: (item.created_time is not None, item.created_time), reverse = True)

        for inst in instance_list:

            if inst.soft_delete is True:
                result.append(inst)
                continue

            if hashes_dict.get(inst.hash) is None:
                result.append(inst)
                hashes_dict[inst.hash] = True
            else:
                # Collision detected, we keep the newest instance by created time (which was order sorted).
                # So this one is just to be deleted and not added to results.
                logger.warning(f"Collision detected on {inst.hash} instance id: {inst.id}")
                logger.warning(f"hashes_dict: {hashes_dict}")
                inst.soft_delete = True
                inst.action_type = "from_collision"
                self.session.add(inst)

        return result
    
    # Tested
    def rehash_existing_instances(self, instance_list):
        result = []
        for instance in instance_list:
            prev_hash = instance.hash
            instance.hash_instance()
            new_hash = instance.hash
            if prev_hash != new_hash:
                logger.info(
                    'Warning: Hashing algorithm upgrade Instance ID: {} has changed \n from: {} \n to: {}'.format(
                        instance.id,
                        prev_hash,
                        new_hash
                    ))
                self.system_upgrade_hash_changes.append([prev_hash, new_hash])
                self.session.add(instance)
            result.append(instance)

        return result

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
                                                    sort_by = 'created_time',
                                                    exclude_removed = False,
                                                    with_for_update = True)
        self.instance_list_existing = self.detect_and_remove_collisions(self.instance_list_existing)
        self.instance_list_existing = self.rehash_existing_instances(self.instance_list_existing)

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
            logger.info(f"getting project from task {self.task.id}")
            project = self.task.project

        assert project is not None

        if not project.label_dict:
            project.refresh_label_dict(self.session)
        self.allowed_label_file_id_list = project.label_dict.get('label_file_id_list')

        assert self.allowed_label_file_id_list is not None

    def validate_label_file_id(self):
        """

        """
        if self.instance.label_file_id is None:
            return True

        if self.instance.label_file_id in self.allowed_label_file_id_list:
            return True

        if self.instance.type == "global":
            self.instance.label_file_id = None  # Ensure is None for Security
            return True

        self.log['error']['valid_label_file'] = "Label File ID" + \
                                                str(self.instance.label_file_id) + f"does not belong to project {self.project.project_string_id}. Ensure you are using the correct label_file_id (and not the label ID). They are different!"
        return False

    def init_video_input(self):

        # TODO, we aren't actually 'raising" this error very well here.

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
            },
            {'set_parent_instance_list': {
                'kind': bool,
                'required': False
            }
            }
        ]

        self.log, input = regular_input.input_check_many(
            spec_list = spec_list,
            log = self.log,
            untrusted_input = self.video_data)

        if len(self.log["error"].keys()) >= 1:
            return False

        self.set_parent_instance_list = input['set_parent_instance_list']
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
        logger.warning(f"Error Duplicate IDs detected on instance_list. Id is: {existing_instance.get('id')}")

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
            logger.warning(f"{str(exception)}_trace_4f36a2aa")
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
            if self.instance_proposed['type'] == 'relation':
                for elm in self.per_instance_spec_list:
                    if 'label_file_id' in elm:
                        elm['label_file_id']['required'] = False

            if self.instance_proposed.get('type') == 'global':
                self.instance_proposed['label_file_id'] = -1  # to bypass input type check

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
                start_time = input['start_time'],
                end_time = input['end_time'],
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
                rotation_euler_angles = input['rotation_euler_angles'],
                position_3d = input['position_3d'],
                center_3d = input['center_3d'],
                dimensions_3d = input['dimensions_3d'],
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
                pause_object = input['pause_object'],
                text_tokenizer = input['text_tokenizer'],
                from_instance_id = input['from_instance_id'],
                to_instance_id = input['to_instance_id'],
                from_creation_ref = input['from_creation_ref'],
                to_creation_ref = input['to_creation_ref'],
                lonlat = input['lonlat'],
                coords = input['coords'],
                radius = input['radius'],
                bounds = input['bounds'],
                bounds_lonlat = input['bounds_lonlat'],
                score = input['score'],
            )

    def get_min_coordinates_instance(self, instance):
        logger.debug(f"Getting min coordinates for {instance.id} - {instance.type}")

        if instance.type in ['text_token', 'relation', 'global']:
            return 0, 0

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
            if not instance.nodes['nodes'][0]['x'] or not instance.nodes['nodes'][0]['y']:
                return 0, 0
            return min([p['x'] for p in instance.nodes['nodes']]), min([p['y'] for p in instance.nodes['nodes']])
        elif instance.type == 'cuboid_3d':
            return instance.center_3d['x'] - (instance.dimensions_3d['width'] / 2), \
                   instance.center_3d['y'] - (instance.dimensions_3d['height'] / 2), \
                   instance.center_3d['z'] - (instance.dimensions_3d['depth'] / 2)
        else:
            logger.error(f"Invalid instance type for image crop: {instance.type}")
            return None

    def get_max_coordinates_instance(self, instance):
        logger.debug(f"Getting max coordinates for {instance.id} - {instance.type}")

        if instance.type in ['text_token', 'relation', 'global']:
            return 0, 0

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
            if not instance.nodes['nodes'][0]['x'] or not instance.nodes['nodes'][0]['y']:
                return 0, 0
            return max([p['x'] for p in instance.nodes['nodes']]), max([p['y'] for p in instance.nodes['nodes']])
        elif instance.type == 'cuboid_3d':
            return instance.center_3d['x'] + (instance.dimensions_3d['width'] / 2), \
                   instance.center_3d['y'] + (instance.dimensions_3d['height'] / 2), \
                   instance.center_3d['z'] + (instance.dimensions_3d['depth'] / 2)
        else:
            logger.error(f"Invalid instance type for image crop: {instance.type}")
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
                        start_time = None,
                        end_time = None,
                        sentence = None,
                        creation_ref_id = None,
                        model_id = None,
                        model_run_id = None,
                        previous_id = None,
                        version = None,
                        root_id = None,
                        center_x = None,
                        center_y = None,
                        rotation_euler_angles = None,
                        position_3d = None,
                        center_3d = None,
                        dimensions_3d = None,
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
                        pause_object = None,
                        text_tokenizer = 'wink',
                        from_instance_id = None,
                        to_instance_id = None,
                        from_creation_ref = None,
                        to_creation_ref = None,
                        lonlat = None,
                        coords = None,
                        radius = None,
                        bounds = None,
                        bounds_lonlat = None,
                        score = None
                        ):
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
            logger.debug(f"Creating Instance with file id: {self.file.id}")
            logger.debug(f"Creating Instance with project id: {self.file.project.id}")
            logger.debug(f"Creating Instance with type: {type}")
            logger.debug(
                f"Creating Instance with TOKENS: {start_sentence} {end_sentence} {end_char} {start_char}")
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
            'start_time': start_time,
            'end_time': end_time,
            'sentence': sentence,
            'creation_ref_id': creation_ref_id,
            'model_id': model_id,
            'model_run_id': model_run_id,
            'previous_id': previous_id,
            'version': version,
            'root_id': root_id,
            'center_x': center_x,
            'center_y': center_y,
            'center_3d': center_3d if center_3d is not None else {},
            'rotation_euler_angles': rotation_euler_angles if rotation_euler_angles is not None else {},
            'position_3d': position_3d if position_3d is not None else {},
            'dimensions_3d': dimensions_3d if dimensions_3d is not None else {},
            'angle': float(angle) if angle is not None else 0.0,
            'width': width,
            'height': height,
            'cp': cp,
            'p1': p1,
            'p2': p2,
            'nodes': {'nodes': nodes},
            'edges': {'edges': edges},
            'pause_object': pause_object,
            'from_instance_id': from_instance_id,
            'to_instance_id': to_instance_id,
            'text_tokenizer': text_tokenizer,
            'lonlat': lonlat,
            'coords': coords,
            'radius': radius,
            'bounds': bounds,
            'bounds_lonlat': bounds_lonlat,
            'score' : score
        }
        if overwrite_existing_instances and id is not None:
            self.instance = self.session.query(Instance).filter(Instance.id == id).first()
            for key, value in instance_attrs.items():
                setattr(self.instance, key, value)
        else:
            self.instance = Instance(**instance_attrs)

        self.instance_limits(validate_label_file = validate_label_file)

        self.check_relations_id_existence(from_id = from_instance_id,
                                          to_id = to_instance_id,
                                          from_ref = from_creation_ref,
                                          to_ref = to_creation_ref)

        if len(self.log["error"].keys()) >= 1:
            logger.error(f"Error on instance creation {self.log}")
            return False

        self.deduct_spatial_coordinates()

        if len(self.log["error"].keys()) >= 1:
            logger.error(f"Error on instance creation {self.log}")
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

        is_new_instance = self.determine_if_new_instance_and_update_current(old_id = id)

        try:  # wrap new concept in try block just in case
            self.instance = self.__validate_user_deletion(self.instance, is_new_instance)
        except Exception as e:
            logger.error(f"{str(e)} trace_82j2j__validate_user_deletion")
            communicate_via_email.send(settings.DEFAULT_ENGINEERING_EMAIL, '[Exception] __validate_user_deletion',
                                       str(self.log))

        self.__perform_external_map_action()

        self.update_cache_single_instance_in_list_context()
        logger.debug(f"is_new_instance {is_new_instance}")
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

        sequence = self.sequence_update(instance = self.instance)

        if sequence:
            if not self.instance.soft_delete:
                sequence.add_keyframe_to_cache(self.session, self.instance)
                self.session.add(sequence)

                self.added_sequence_ids.append(sequence.id)  # prevent future deletion from history annotations

    def deduct_spatial_coordinates(self):

        if self.instance.type in ["global",
                                  'geo_point',
                                  'geo_circle',
                                  'geo_polyline',
                                  'geo_polygon',
                                  'geo_box',
                                  "relation",
                                  "token",
                                  "audio"
                                  ]:
            return

        min_coords = self.get_min_coordinates_instance(self.instance)
        max_coords = self.get_max_coordinates_instance(self.instance)

        if self.instance.type in ['cuboid_3d']:
            self.instance.min_point_3d = {
                'min': {
                    'x': min_coords[0],
                    'y': min_coords[1],
                    'z': min_coords[2]
                }
            }
            self.instance.max_point_3d = {
                'max': {
                    'x': max_coords[0],
                    'y': max_coords[1],
                    'z': max_coords[2]
                }
            }
        else:
            self.instance.x_min = int(min_coords[0])
            self.instance.y_min = int(min_coords[1])
            self.instance.x_max = int(max_coords[0])
            self.instance.y_max = int(max_coords[1])

    def find_serialized_instance_index(self, id):
        for i in range(0, len(self.instance_list_kept_serialized)):
            instance = self.instance_list_kept_serialized[i]
            if instance.get('id') == id:
                return i

    # Tested
    def update_sequence_id_in_cache_list(self, instance):
        """
            Updates the sequences ID in the cache list.
        :param instance:
        :return:
        """
        if instance.id is None:
            return
        if instance.sequence_id is None:
            return
        for i in range(0, len(self.instance_list_kept_serialized)):
            existing_serialized_instance = self.instance_list_kept_serialized[i]
            if existing_serialized_instance.get('id') == instance.id:
                existing_serialized_instance['sequence_id'] = instance.sequence_id

    # Tested
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

        if not self.serialized_ids_map.get(self.instance.id):
            serialized_data = self.instance.serialize_with_label()
            self.instance_list_kept_serialized.append(serialized_data)
            self.serialized_ids_map[self.instance.id] = True

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

    # Tested
    def add_missing_ids_to_new_relations(self):

        for relation_elm in self.new_instance_relations_list_no_ids:
            instance = relation_elm['instance']
            from_ref = relation_elm['from_ref']
            to_ref = relation_elm['to_ref']
            if instance.from_instance_id is None:
                new_instance = next((item for item in self.new_added_instances if item.creation_ref_id == from_ref),
                                    None)
                if new_instance:
                    instance.from_instance_id = new_instance.id

            if instance.to_instance_id is None:
                new_instance = next((item for item in self.new_added_instances if item.creation_ref_id == to_ref),
                                    None)
                if new_instance:
                    instance.to_instance_id = new_instance.id

            instance.hash_instance()
            self.session.add(instance)

    # Tested
    def check_relations_id_existence(self, from_id, to_id, from_ref, to_ref):
        """
            Checks if current instance is a relations and if ID's are available for saving.
            If not avaialable, fallback to creation_refs and add IDs after creation_refs are saved.
            If non are available we throw error.

        :return:
        """
        if self.instance.type != 'relation':
            return

        if from_id is None and not from_ref:
            self.log['error']['from_id'] = 'Provide from_instance_id or from_creation_ref'
            return

        if to_id is None and not to_ref:
            self.log['error']['to_id'] = 'Provide to_instance_id or to_creation_ref'
            return
        if from_id is None or to_id is None:
            self.new_instance_relations_list_no_ids.append({'instance': self.instance,
                                                            'from_ref': from_ref,
                                                            'to_ref': to_ref})

    def instance_limits(self, validate_label_file = True):
        """
        I'm not a huge fan of having so many self.instance things
        but don't see a great alterative...
        """
        # Initialize default Values
        self.instance.points = {'points': []}

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

    def detect_special_duplicate_data_cases_from_existing_ids(self, old_id):

        if self.instance.soft_delete is True or not self.new_instance_dict_hash.get(self.instance.hash):
            self.append_new_instance_list_hash(self.instance)  # tracking for special cases
            return True
        else:
            # This case can happen when 2 instances with the exact same data are sent on instance_list_new.
            # We only want to keep one of them.
            logger.warning(f"Got duplicated hash {self.instance.hash}")
            # The instance_dict hash will always have the newest instance (sorted by created_time)
            self.duplicate_hash_new_instance_list.append(self.instance)
            existing_instance = self.new_instance_dict_hash[self.instance.hash]
            if existing_instance.id is not None and self.instance.id is not None:
                message = 'Two instances with the same label on same position, please remove one. IDs: {}, {}'.format(
                    self.instance.id,
                    existing_instance.id
                )
                logger.error(message)
                self.log['error']['duplicate_instances'] = message
                return False

            self.instance = existing_instance
            try:
                self.hash_list.remove(self.instance.hash)
            # logger.info("Removed str(self.instance.hash))
            except:
                self.log['info']['hash_list'] = "No instance to remove."

            return False

    def determine_if_new_instance_and_update_current(self, old_id = None):
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

        special_case_result = self.detect_special_duplicate_data_cases_from_existing_ids(old_id)
        if special_case_result is False: return False
        self.existing_instance_index = self.hash_old_cross_reference.get(self.instance.hash)

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
            self.instance.hash_instance()
            self.previous_next_instance_map[self.instance.previous_id] = self.instance.id

        self.new_added_instances.append(self.instance)
        return is_new_instance

    def __validate_user_deletion(self, instance, is_new_instance):
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

            if previous_instance.soft_delete is True and instance.soft_delete is False and is_new_instance:
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
        # For "Human" updates only
        if update_existing_only is False:

            updated_sequence, is_new_sequence = Sequence.update(
                session = self.session,
                project = self.project,
                video_mode = self.video_mode,
                instance = instance,
                video_file = self.video_parent_file
            )
            if updated_sequence is not None and not updated_sequence.archived:
                self.sequence = updated_sequence
            if is_new_sequence:
                self.new_created_sequence_list.append(self.sequence)
            self.update_sequence_id_in_cache_list(instance = instance)
            return updated_sequence
        else:
            # Eg for deleting when sequence is changed on existing instance
            sequence = Sequence.update_single_existing_sequence(
                session = self.session,
                instance = instance,
                video_file = self.video_parent_file
            )
            self.update_sequence_id_in_cache_list(instance = instance)

            return sequence

    # Tested
    def check_polygon_points_and_build_bounds(self):
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
                 "y": point[y],
                 "figure_id": point.get('figure_id')
                 }
            )

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

        logger.info(f"Newly Deleted {instance.id}")

        self.new_deleted_instances.append(instance.id)

        self.update_instance_count(action_type = 'delete_instance')

        # Prevent from updating the original deletion time.
        if not instance.deleted_time:
            instance.deleted_time = datetime.datetime.utcnow()

        sequence = self.sequence_update(
            instance = instance,
            update_existing_only = True)

        if sequence:
            if sequence.id not in self.added_sequence_ids:
                sequence.remove_keyframe_to_cache(self.session, instance)
                self.session.add(sequence)

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
    task = None,
    member = None,
    log = regular_log.default()):
    # In context of already having the {task} object,
    # ie for newly created stuff... (to prevent race conditions)
    if not task:
        task = Task.get_by_id(session = session,
                              task_id = task_id)
        if not task:
            return False

    # TODO Why are we adding this to session here? not clear
    session.add(task)
    child_file_save_id = input.get('child_file_save_id')
    project = task.project

    instance_list_new = untrusted_input.get('instance_list', None)
    gold_standard_file = untrusted_input.get('gold_standard_file', None)
    try:
        if child_file_save_id is None:
            file = File.get_by_id(session = session, file_id = task.file_id)
        else:
            file = File.get_by_id(session = session, file_id = child_file_save_id)
    except Exception as e:
        trace = traceback.format_exc()
        logger.error(f"File {task.file_id} is Locked")
        logger.error(trace)
        log['error']['file_locked'] = 'File is being saved by another process, please try again later.'
        return False, None
    annotation_update = Annotation_Update(
        session = session,
        task = task,
        file = file,
        project = project,
        member = member,
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
            project = project,
            member = member)

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
    file_id,
    log = regular_log.default()):
    data = request.get_json(force = True)  # Force = true if not set as application/json'

    if file_id is None: return "error file_id is None", 400

    instance_list_new = data.get('instance_list', None)
    and_complete = data.get('and_complete', None)

    project = Project.get(session, project_string_id)
    user = User.get(session)
    try:
        file = File.get_by_id_and_project(
            session = session,
            project_id = project.id,
            file_id = file_id)
    except Exception as e:
        trace = traceback.format_exc()
        logger.error(f"File {file_id} is Locked")
        logger.error(trace)
        log['error']['file_locked'] = 'File is being saved by another process, please try again later.'
        return False, None

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

    member_id = user.member_id if user else None

    Event.new(
        session = session,
        kind = "annotation_update",
        member_id = member_id,
        project_id = project.id,
        file_id = new_file.id,
        description = f"Changed {str(new_file.count_instances_changed)}"
    )

    return new_file.serialize_with_type(session), annotation_update
