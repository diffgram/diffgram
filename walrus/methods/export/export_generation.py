# OPENCORE - ADD
from methods.regular.regular_api import *
import yaml
from shared.database.export import Export
from shared.database.source_control.working_dir import WorkingDirFileLink
from shared.database.source_control.file_diff import file_difference
from methods.machine_learning.semantic_segmentation import Semantic_segmentation_data_prep
from shared.database.attribute.attribute_template_group import Attribute_Template_Group
from shared.database.video.sequence import Sequence

from shared.data_tools_core import Data_tools
import traceback
from methods.export.export_utils import generate_file_name_from_export


data_tools = Data_tools().data_tools


def try_to_commit(session):
    try:
        session.commit()
    except:
        session.rollback()
        raise


def new_external_export(
        session,
        project,
        export_id,
        version=None,
        working_dir=None,
        use_request_context=True):
    """
    Create a new export data file

    This is run on first load

    session, session object
    project, project object


    Designed for external consumptions

    returns {"success" : True} if successfully

    Security model
     this is an internal function

     export web DOES the validation
     Job_permissions.check_job_after_project_already_valid()

    """

    logger.info("[Export processor] Started")
    result = False
    start_time = time.time()

    export = session.query(Export).filter(
        Export.id == export_id).first()

    member = None
    if use_request_context:
        user = User.get(session)

        export.user = user

        if user:
            member = user.member
        else:
            client_id = request.authorization.get('username', None)
            auth = Auth_api.get(session, client_id)
            member = auth.member

    session.add(export)

    if export.source == "task":

        if export.task and export.task.file:
            # Caution export.task not task

            file_list = [export.task.file]

    # While job could be None and still get files
    # if we do have a job id we may want to get
    # files not replaced in the directory yet.
    if export.source == "job":

        file_list = WorkingDirFileLink.file_list(
            session=session,
            limit=None,
            root_files_only=True,
            job_id=export.job_id,
            ann_is_complete=export.ann_is_complete
        )

    if export.source == "directory":
        # Question, why are we declaring this here?
        # Doesn't really make sense as export already has
        # it when created?
        export.working_dir_id = working_dir.id

        file_list = WorkingDirFileLink.file_list(
            session=session,
            working_dir_id=working_dir.id,
            limit=None,
            root_files_only=True,
            ann_is_complete=export.ann_is_complete
        )

    result, annotations = annotation_export_core(
        session=session,
        project=project,
        export=export,
        file_list=file_list)

    if result is False or result is None:
        return False

    filename = generate_file_name_from_export(export, session)

    if export.kind == "Annotations":

        export.yaml_blob_name = settings.EXPORT_DIR + \
                                str(export.id) + filename + '.yaml'

        export.json_blob_name = settings.EXPORT_DIR + \
                                str(export.id) + filename + '.json'

        try:
            yaml_data = yaml.dump(annotations, default_flow_style=False)
            data_tools.upload_from_string(export.yaml_blob_name, yaml_data, content_type='text/yaml', bucket_type = 'ml')
        except Exception as exception:
            trace_data = traceback.format_exc()
            logger.error("[Export, YAML] {}".format(str(exception)))
            logger.error(trace_data)

        json_data = json.dumps(annotations)
        data_tools.upload_from_string(export.json_blob_name, json_data, content_type = 'text/json', bucket_type = 'ml')

    end_time = time.time()
    logger.info("[Export processor] ran in {}".format(end_time - start_time))

    Event.new(
        kind="export_generation",
        session=session,
        member=member,
        success=result,
        project_id=project.id,
        run_time=end_time - start_time
    )

    return True, annotations


def build_label_colour_map(session, label_map):
    result = {}
    if not label_map:
        return result

    for key, val in label_map.items():
        file = File.get_by_id(session, file_id = key)
        result[key] = file.colour
    return result


def annotation_export_core(
        session,
        project,
        export,
        file_list):
    """
    Generic method to export a file list
    """

    images_dir = settings.PROJECT_IMAGES_BASE_DIR + \
                 str(project.id) + "/"

    export.file_list_length = len(file_list)

    errors_result = check_for_errors(
        export = export,
        session = session)
    if errors_result is False:
        return False, None

    # If we build annotations directly then we could return them
    # If tf records than not
    # But some clean up stuff (ie marking complete) that's joint
    # Also not clear where we would be using a return dict of annotations here
    # Ohhh it returns annotations since we upload in YAML or JSON format for that
    # Maybe that should just be part of that process (instead of returning with a
    # seperate flag?)

    annotations = None

    # This is here as it's shared with with masks and
    # not masks, but needs to run before masks if masks

    # So we can have mask values increase in series
    # instead of using ids for example

    # Careful, want to use project default directory for labels for now

    label_file_list = WorkingDirFileLink.file_list(
        session=session,
        working_dir_id=export.project.directory_default_id,
        limit=None,
        type="label"
    )

    if export.kind == "TF Records":
        label_dict = data_tools.label_dict_builder(
            file_list=label_file_list)

    export_label_map = {}
    for label_file in label_file_list:
        export_label_map[label_file.id] = label_file.label.name

    # TODO masks if not part of TF records is not really handled great right now

    # TODO pass export object to track it?

    """

        Would be good to allow masks for regular records / JSON
        too, but not supported yet, so for now 
        we do the tf records check too.
    """

    if export.masks is True and export.kind == "TF Records":
        # Assumes deep lab style for now?
        semantic_prep = Semantic_segmentation_data_prep()

        semantic_prep.generate_mask_core(
            session=session,
            project=project,
            file_list=file_list,
            type="joint",
            label_dict=label_dict
        )

    if export.kind == "TF Records":

        export.tf_records_blob_name = settings.EXPORT_DIR + \
                                      str(export.id)

        # Still need to check masks again here
        # To determine what building method we are using?
        if export.masks is True:
            result = data_tools.tf_records_new(
                session=session,
                file_list=file_list,
                project_id=export.project_id,
                method="semantic_segmentation",
                output_blob_dir=export.tf_records_blob_name
            )

            export.tf_records_blob_name += "/train-0.record"

        if export.masks is False:
            result = data_tools.tf_records_new(
                session=session,
                project_id=export.project_id,
                file_list=file_list,
                method="object_detection",
                label_dict=label_dict,
                output_blob_dir=export.tf_records_blob_name)

            export.tf_records_blob_name += "/tfrecords_0.record"

    if export.kind == "Annotations":
        annotations = {}

        annotations['readme'] = export.serialize_readme()

        annotations['label_map'] = export_label_map
        annotations['label_colour_map'] = build_label_colour_map(session, export_label_map)

        # TODO maybe, would like "annotations"
        # To be one layer "deeper" in terms of nesting.
        annotations['export_info'] = export.serialize_for_inside_export_itself()

        # Other / shared stuff
        annotations["attribute_groups_reference"] = build_attribute_groups_reference(
            session=session,
            project=project)

        # TODO
        # so I guess the "new" yaml one can do it "on demand"
        # if you substitute version for working directory?
        for index, file in enumerate(file_list):

            # Image URL?
            packet = build_packet(
                file=file,
                session=session,
                file_comparison_mode=export.file_comparison_mode)

            # What about by filename?
            # Original filename is not gauranteed to be unique
            # Careful! if this is not unique it will overwrite
            # on export and difficult to debug
            # as it looks like its' working (ie file count is there)
            # but first file is "null"...
            # Prior we used hash here, but in context of a task
            # We may not re hash file (something to look at in future, maybe
            # we do want to hash it...)
            annotations[file.id] = packet

            export.percent_complete = (index / export.file_list_length) * 100

            if index % 10 == 0:
                # TODO would need to commit the session for this to be useful right?
                logger.info("Percent done {}".format(export.percent_complete))
                try_to_commit(session=session)  # push update

    export.status = "complete"
    export.percent_complete = 100

    return True, annotations


def build_attribute_groups_reference(
        session,
        project):
    """
    Given a project builds reference to values...
    """
    group_list = Attribute_Template_Group.list(
        session=session,
        group_id=None,
        mode="from_project",
        project_id=project.id,
        return_kind="objects"
    )

    group_list_serialized = []

    for group in group_list:
        group_list_serialized.append(group.serialize_with_attributes(session))

    return group_list_serialized


def build_packet(file,
                 session=None,
                 file_comparison_mode="latest"):
    if file.type == "video":
        return build_video_packet(file, session)

    if file.type == "image":
        return build_image_packet(file, session, file_comparison_mode)

    if file.type == "text":
        return build_text_packet(file, session, file_comparison_mode)


def build_video_packet(file, session):
    """
    Assumes it's "latest" and doesn't do vs_orignal yet

    * Serializes video information
    * Gets all frames *with instances* for the video FILE
    * Each frame it gets the instance list

    It assumes that we don't need to say do the width for each
    image since it's the same for the video.

    We could also export it by sequence.
    ie for each video, we export the frames for the sequence...

    """

    # Question, could we use an existing serialize method for this part?
    # Feels a bit funny to repeat it like this here.
    file.video.regenerate_url(
        project=file.project,
        session=session)

    # Context of making it easier to inspect and download media
    mp4_video_signed_url = file.video.file_signed_url

    if settings.DIFFGRAM_STATIC_STORAGE_PROVIDER == 'gcp':
        if mp4_video_signed_url:
            mp4_video_signed_url += ".mp4"

    video_dict = {
        'width': file.video.width,
        'height': file.video.height,
        'frame_rate': file.video.frame_rate,
        'frame_count': file.video.frame_count,
        'original_fps': file.video.original_fps,
        'fps_conversion_ratio': file.video.fps_conversion_ratio,
        'mp4_video_signed_url': mp4_video_signed_url,
        'mp4_video_signed_expiry': file.video.url_signed_expiry,
        'offset_in_seconds' : file.video.offset_in_seconds,
        	'global_frame_start' : file.video.calculate_global_reference_frame(
				frame_number = 0)
    }

    sequence_list = session.query(Sequence).filter(
        Sequence.video_file_id == file.id).all()
    sequence_list_serialized = []

    for sequence in sequence_list:

        sequence_dict = sequence.serialize_for_export()
        instance_list_serialized = []

        instance_list = Instance.list(  # Using this checks for soft deleted by default
            session=session,
            sequence_id=sequence.id,
            limit=None)

        # Each instance has it's frame number
        for instance in instance_list:
            instance_list_serialized.append(
                build_instance(instance, include_label=False))

        sequence_dict['instance_list'] = instance_list_serialized
        sequence_list_serialized.append(sequence_dict)

    # Could also include the "keyframes" thing.

    return {'file': {
        'id': file.id,
        'original_filename': file.original_filename,
        'blob_url': mp4_video_signed_url,
        'created_time': str(file.created_time),
        'ann_is_complete': file.ann_is_complete,
        'type': file.type
        # note str() otherwise get "non serializeable"

    },
        'video': video_dict,
        'sequence_list': sequence_list_serialized}


def build_image_packet(
        file,
        session=None,
        file_comparison_mode=None):
    """
    Generic method to generate a dict of information given a file
    """

    file.image.regenerate_url(session=session)

    image_dict = {'width': file.image.width,
                  'height': file.image.height,
                  'image_signed_expiry': file.image.url_signed_expiry,
                  'image_signed_url': file.image.url_signed,
                  'original_filename': file.image.original_filename}

    instance_dict_list = []

    if file_comparison_mode == "latest":

        instance_list = Instance.list(
            session=session,
            file_id=file.id)
        for instance in instance_list:
            instance_dict_list.append(build_instance(instance))

    if file_comparison_mode == "vs_original":
        # We could use the raw dict of the {'unchanged', 'added', 'deleted'}
        # sets BUT then it would make the below a little different
        # TODO review this
        #

        result, instance_dict = file_difference(
            session=session,
            file_id_alpha=file.id,
            file_id_bravo=file.root_id)

        for change_type in instance_dict.keys():
            for instance in instance_dict[change_type]:
                out = build_instance(instance)

                out['change_type'] = change_type

                instance_dict_list.append(out)

    return {'file': {
        'id': file.id,
        'original_filename': file.original_filename,
        'blob_url': file.image.url_signed,
        'created_time': str(file.created_time),
        'ann_is_complete': file.ann_is_complete,
        'type': file.type
    },
        'image': image_dict,
        'instance_list': instance_dict_list}


def build_text_packet(
        file,
        session=None,
        file_comparison_mode=None):
    """
    Generic method to generate a dict of information given a file
    """

    file.text_file.regenerate_url()
    text_dict = {
        'original_filename': file.text_file.original_filename,
        'image_signed_expiry': file.image.url_signed_expiry,
        'image_signed_url': file.image.url_signed,
    }

    instance_dict_list = []

    if file_comparison_mode == "latest":

        instance_list = Instance.list(
            session=session,
            file_id=file.id)

        for instance in instance_list:
            instance_dict_list.append(build_instance(instance))

    if file_comparison_mode == "vs_original":
        # We could use the raw dict of the {'unchanged', 'added', 'deleted'}
        # sets BUT then it would make the below a little different
        # TODO review this
        #

        result, instance_dict = file_difference(
            session=session,
            file_id_alpha=file.id,
            file_id_bravo=file.root_id)

        for change_type in instance_dict.keys():
            for instance in instance_dict[change_type]:
                out = build_instance(instance)

                out['change_type'] = change_type

                instance_dict_list.append(out)

    return {'file': {
        'id': file.id,
        'original_filename': file.original_filename,
        'blob_url': file.text_file.url_signed,
        'created_time': str(file.created_time),
        'ann_is_complete': file.ann_is_complete,
        'type': file.type
    },
        'text': text_dict,
        'instance_list': instance_dict_list}


def build_instance(instance, include_label=False):
    """
    instance.attribute_groups is a SQL Alchemy type mutable dict
    it does not serialize by default
    so we cast it to a new thing using dict() which is basically
    just copying key values

    instance.attribute_groups may be None
    if it's None then dict() thing appears to fail

    using dict() is preffered to json dumps as that seems to create
    a bunch of random slashes.
    """
    attribute_groups = instance.attribute_groups
    if attribute_groups:
        attribute_groups = dict(attribute_groups)

    # Warning: Add new instance types in conditional
    # Don't add them here - otherwise this creates a lot of 
    # not needed data

    out = {  # 'hash'  : instance.hash,
        'type': instance.type,
        'label_file_id': instance.label_file_id,    # for images
        'frame_number': instance.frame_number,
        'global_frame_number': instance.global_frame_number,
        'number': instance.number,
        'x_min': instance.x_min,
        'y_min': instance.y_min,
        'x_max': instance.x_max,
        'y_max': instance.y_max,
        'p1': instance.p1,
        'p2': instance.p2,
        'cp': instance.cp,
        'angle': instance.angle,
        'attribute_groups': attribute_groups,
        'interpolated': instance.interpolated,
        # 'local_sequence_number' : instance.number,
    }

    # Limit output, eg so an instance ina frame doesn't have a ton
    # of extra tokens
    # TODO refactor to own functions, eg
    # right now text tokens now display x_min when it's not needed
    # TODO also check if this applies to other serialization forms
    # eg in instance.py

    if instance.type == 'cuboid':
        out['front_face'] = instance.front_face
        out['rear_face'] = instance.rear_face

    if instance.type == 'ellipse':
        out['center_x'] = instance.center_x
        out['center_y'] = instance.center_y
        out['width'] = instance.width
        out['height'] = instance.height

    if instance.type == 'text_token':
        out['start_char'] = instance.start_char
        out['end_char'] = instance.end_char
        out['start_token'] = instance.start_token
        out['end_token'] = instance.end_token
        out['start_sentence'] = instance.start_sentence
        out['end_sentence'] = instance.end_sentence
        out['sentence'] = instance.sentence

    if instance.mask_url:
        out['mask'] = instance.mask_url

    if instance.points.get('points', None):
        out['points'] = instance.points.get('points', None)

    if include_label is True:
        out['label'] = {
            'id': instance.label_file.label.id,
            'label_name': instance.label_file.label.name
        }

    return out



def check_for_errors(
        export: Export,
        session):
    # Could also have a "warnings" thing in future
    # This is different from the "check_export_billing" section

    if export.file_list_length == 0:
        declare_export_failed(
            export = export,
            reason = "File List is Empty. Have tasks been completed? Potential Fix: To view all files: Un-select 'Complete Files Only'.",
            session = session)
        return False

    return True


def declare_export_failed(
        export: Export,
        reason: str,
        session):

    export.status = "failed"
    export.status_text = reason
    session.add(export)


setattr(Export, "new_external_export", new_external_export)
setattr(Export, "build_packet", build_packet)
