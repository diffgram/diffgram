import time
import json
from shared.database.export import Export
from shared.settings import settings
from shared.database.source_control.working_dir import WorkingDirFileLink
from shared.database.source_control.file import File
from shared.database.project import Project
from shared.database.annotation.instance import Instance
from shared.machine_learning.semantic_segmentation_data_prep import Semantic_segmentation_data_prep
from shared.database.attribute.attribute_template_group import Attribute_Template_Group
from shared.database.video.sequence import Sequence
from shared.database.task.task import Task
from shared.database.event.event import Event
from shared.shared_logger import get_shared_logger
from shared.data_tools_core import Data_tools
import traceback
from shared.export.export_utils import generate_file_name_from_export
from sqlalchemy.orm.session import Session

logger = get_shared_logger()
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
    member,
    version = None,
    working_dir = None):
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

    session.add(export)

    if export.source == "task":

        if export.task and export.task.file:
            # Caution export.task not task

            file_list = [export.task.file]

    if export.source == "job":

        status = None
        if export.ann_is_complete is True:
            status = "complete"

        task_list = Task.list(
            session = session,
            job_id = export.job_id,
            status = status,
            project_id = export.project_id,
            limit_count = None
        )

        file_list = []
        for task in task_list:
            file_list.append(task.file)

    if export.source == "directory":

        export.working_dir_id = working_dir.id

        file_list = WorkingDirFileLink.file_list(
            session = session,
            working_dir_id = working_dir.id,
            limit = None,
            root_files_only = True,
            ann_is_complete = export.ann_is_complete,
            include_children_compound = True
        )

    result, annotations = annotation_export_core(
        session = session,
        project = project,
        export = export,
        file_list = file_list)

    if result is False or result is None:
        return False, None

    filename = generate_file_name_from_export(export, session)

    if export.kind == "Annotations":
        export.json_blob_name = settings.EXPORT_DIR + \
                                str(export.id) + filename + '.json'

        json_data = json.dumps(annotations)
        data_tools.upload_from_string(export.json_blob_name, json_data, content_type = 'text/json', bucket_type = 'ml')

    end_time = time.time()
    logger.info(f"[Export processor] ran in {end_time - start_time}")

    Event.new(
        kind = "export_generation",
        session = session,
        member = member,
        success = result,
        project_id = project.id,
        run_time = end_time - start_time
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

    images_dir = f"{settings.PROJECT_IMAGES_BASE_DIR + str(project.id)}/"

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
        session = session,
        working_dir_id = export.project.directory_default_id,
        limit = None,
        type = "label"
    )

    if export.kind == "TF Records":
        label_dict = data_tools.label_dict_builder(
            file_list = label_file_list)

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
            session = session,
            project = project,
            file_list = file_list,
            type = "joint",
            label_dict = label_dict
        )

    if export.kind == "TF Records":

        export.tf_records_blob_name = settings.EXPORT_DIR + \
                                      str(export.id)

        # Still need to check masks again here
        # To determine what building method we are using?
        if export.masks is True:
            result = data_tools.tf_records_new(
                session = session,
                file_list = file_list,
                project_id = export.project_id,
                method = "semantic_segmentation",
                output_blob_dir = export.tf_records_blob_name
            )

            export.tf_records_blob_name += "/train-0.record"

        if export.masks is False:
            result = data_tools.tf_records_new(
                session = session,
                project_id = export.project_id,
                file_list = file_list,
                method = "object_detection",
                label_dict = label_dict,
                output_blob_dir = export.tf_records_blob_name)

            export.tf_records_blob_name += "/tfrecords_0.record"

    if export.kind == "Annotations":
        annotations = {}

        annotations['readme'] = export.serialize_readme()

        annotations['label_map'] = export_label_map
        annotations['label_colour_map'] = build_label_colour_map(session, export_label_map)

        annotations['export_info'] = export.serialize_for_inside_export_itself()

        # Other / shared stuff
        annotations["attribute_groups_reference"] = build_attribute_groups_reference(
            session = session,
            project = project)

        for index, file in enumerate(file_list):
            try:
                packet = build_packet(
                    file = file,
                    session = session)

                annotations[file.id] = packet

                export.percent_complete = (index / export.file_list_length) * 100

                if index % 10 == 0:
                    logger.info(f"Percent done {export.percent_complete}")
                    try_to_commit(session = session)  # push update
            except Exception as e:
                declare_export_failed(export = export, reason = str(e), session = session)
    export.status = "complete"
    export.percent_complete = 100

    return True, annotations


def build_attribute_groups_reference(session: 'Session', project: Project):
    """
    Given a project builds reference to values...
    """
    group_list = Attribute_Template_Group.list(
        session = session,
        group_id = None,
        project_id = project.id,
        return_kind = "objects"
    )

    group_list_serialized = []

    for group in group_list:
        group_list_serialized.append(group.serialize_with_attributes_and_labels(session))

    return group_list_serialized


def build_packet(file,
                 session = None):
    if file.type == "video":
        return build_video_packet(file, session)

    if file.type == "geospatial":
        return build_geopacket(file, session)

    if file.type == "image":
        return build_image_packet(file, session)

    if file.type == "text":
        return build_text_packet(file, session)

    if file.type == "sensor_fusion":
        return build_sensor_fusion_packet(file, session)

    if file.type == "compound":
        return build_compound_file_packet(file, session)


def build_compound_file_packet(file: File, session: Session):
    child_files = file.get_child_files(session = session)
    result = {
        'file': file.serialize_base_file()
    }
    for child_file in child_files:
        result[child_file.id] = build_packet(file = child_file,
                                             session = session)
    return result


def build_geopacket(file, session):
    geo_assets = file.get_geo_assets(session = session)
    assets_serialized = []

    for asset in geo_assets:
        # Serialization triggers URL generation
        asset.serialize(session = session)
        geo_dict = {
            'original_filename': asset.original_filename,
            'signed_expiry': asset.url_signed_expiry,
            'signed_url': asset.url_signed,
        }
        assets_serialized.append(geo_dict)

    instance_dict_list = []
    relations_list = []

    instance_list = Instance.list(
        session = session,
        file_id = file.id)

    for instance in instance_list:
        if instance.type == 'relation':
            continue
        instance_dict_list.append(build_instance(instance, file))

    for relation in instance_list:
        if relation.type != 'relation':
            continue
        relations_list.append(build_relation(relation = relation))


    return {'file': {
        'id': file.id,
        'created_time': str(file.created_time),
        'ann_is_complete': file.ann_is_complete,
        'type': file.type
    },
        'geo_assets': assets_serialized,
        'instance_list': instance_dict_list}


def build_video_packet(file, session):
    """
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
        project = file.project,
        session = session)

    # For global Attributes
    parent_instance_list = Instance.list(
        session = session,
        file_id = file.id,
        limit = None
    )
    parent_instance_list_serialized = []
    for instance in parent_instance_list:
        parent_instance_list_serialized.append(build_instance(instance, file))

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
        'offset_in_seconds': file.video.offset_in_seconds,
        'global_frame_start': file.video.calculate_global_reference_frame(
            frame_number = 0)
    }

    sequence_list = session.query(Sequence).filter(
        Sequence.video_file_id == file.id).all()
    sequence_list_serialized = []

    for sequence in sequence_list:

        sequence_dict = sequence.serialize_for_export()
        instance_list_serialized = []

        instance_list = Instance.list(  # Using this checks for soft deleted by default
            session = session,
            sequence_id = sequence.id,
            limit = None)

        # Each instance has it's frame number
        for instance in instance_list:
            instance_list_serialized.append(
                build_instance(instance, file, include_label = False))

        sequence_dict['instance_list'] = instance_list_serialized
        sequence_list_serialized.append(sequence_dict)

    # Could also include the "keyframes" thing.

    return {
        'file': {
            'id': file.id,
            'original_filename': file.original_filename,
            'blob_url': mp4_video_signed_url,
            'created_time': str(file.created_time),
            'ann_is_complete': file.ann_is_complete,
            'type': file.type
        },
        'video': video_dict,
        'parent_instance_list': parent_instance_list_serialized,
        'sequence_list': sequence_list_serialized
    }


def build_image_packet(
    file,
    session = None):
    """
    Generic method to generate a dict of information given a file
    """

    file.image.serialize_for_source_control(session = session)

    image_dict = {'width': file.image.width,
                  'height': file.image.height,
                  'rotation_degrees': file.image.rotation_degrees,
                  'image_signed_expiry': file.image.url_signed_expiry,
                  'image_signed_url': file.image.url_signed,
                  'original_filename': file.image.original_filename}

    instance_dict_list = []


    instance_list = Instance.list(
        session = session,
        file_id = file.id)
    for instance in instance_list:
        instance_dict_list.append(build_instance(instance, file))


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
    session = None):
    """
    Generic method to generate a dict of information given a file
    """

    file.text_file.serialize(session = session)
    tokens = file.text_file.get_text_tokens(file.text_tokenizer)
    text_dict = {
        'original_filename': file.text_file.original_filename,
        'signed_expiry': file.text_file.url_signed_expiry,
        'signed_url': file.text_file.url_signed,
        'tokens': tokens
    }

    instance_dict_list = []
    relations_list = []

    instance_list = Instance.list(
        session = session,
        file_id = file.id)

    for instance in instance_list:
        if instance.type == 'relation':
            continue
        instance_dict_list.append(build_instance(instance, file))

    for relation in instance_list:
        if relation.type != 'relation':
            continue
        relations_list.append(build_relation(relation = relation))


    instance_dict_list = instance_dict_list + relations_list

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


def build_sensor_fusion_packet(
    file,
    session = None):
    """
    Generic method to generate a dict of information given a file
    """
    point_cloud_dict = {}
    point_cloud_file = file.get_child_point_cloud_file(session = session);
    if point_cloud_file:
        point_cloud_file.point_cloud.serialize(session = session)
        point_cloud_dict = {
            'original_filename': point_cloud_file.point_cloud.original_filename,
            'image_signed_expiry': point_cloud_file.point_cloud.url_signed_expiry,
            'image_signed_url': point_cloud_file.point_cloud.url_signed,
        }

    instance_dict_list = []


    instance_list = Instance.list(
        session = session,
        file_id = file.id)

    for instance in instance_list:
        instance_dict_list.append(build_instance(instance, file))


    return {
        'file': {
            'id': file.id,
            'original_filename': file.original_filename,
            'blob_url': point_cloud_file.point_cloud.url_signed if point_cloud_file.point_cloud else None,
            'created_time': str(file.created_time),
            'ann_is_complete': file.ann_is_complete,
            'type': file.type
        },
        'point_cloud': point_cloud_dict,
        'instance_list': instance_dict_list
    }


def build_relation(relation: Instance):
    out = {
        'type': relation.type,
        'label_file_id': relation.label_file_id, 
        'attribute_groups': relation.attribute_groups,
        'from_instance_id': relation.from_instance_id,
        'to_instance_id': relation.to_instance_id
    }
    return out


def base_instance_packet(instance):

    attribute_groups = instance.attribute_groups
    if attribute_groups:
        attribute_groups = dict(attribute_groups)     # Cast from SQLAlchemy to serializable form 

    return {
        'id': instance.id,
        'type': instance.type,
        'attribute_groups': attribute_groups,
        'label_file_id': instance.label_file_id
    }


def build_instance(instance, file, include_label = False):

    out = base_instance_packet(instance)

    if file.type == 'video':
        out['frame_number'] = instance.frame_number
        out['global_frame_number'] = instance.global_frame_number
        out['local_sequence_number'] = instance.number
        out['number'] = instance.number     # legacy
        out['interpolated'] = instance.interpolated

    if instance.radius:
         out['radius'] = instance.radius

    if instance.bounds:
         out['bounds'] = instance.bounds

    if instance.angle:
         out['angle'] = instance.angle

    if instance.x_min or instance.y_min or instance.x_max or instance.y_max:
         out['x_min'] = instance.x_min
         out['y_min'] = instance.y_min
         out['x_max'] = instance.x_max
         out['y_max'] = instance.y_max

    if instance.type == 'curve':
         out['p1'] = instance.p1
         out['p2'] = instance.p2
         out['cp'] = instance.cp

    if instance.type in ['geo_point', 'geo_circle', 'geo_polyline', 'geo_polygon', 'geo_box']:
        out['lonlat'] = instance.lonlat
        out['coords'] = instance.coords
        out['bounds_lonlat'] = instance.bounds_lonlat

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

    if instance.type == 'keypoints':
        out['nodes'] = instance.nodes
        out['edges'] = instance.edges

    if instance.type == 'cuboid_3d':
        out['rotation_euler_angles'] = instance.rotation_euler_angles
        out['position_3d'] = instance.position_3d
        out['center_3d'] = instance.center_3d
        out['max_point_3d'] = instance.max_point_3d
        out['min_point_3d'] = instance.min_point_3d
        out['dimensions_3d'] = instance.dimensions_3d
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


setattr(Export, "build_packet", build_packet)
