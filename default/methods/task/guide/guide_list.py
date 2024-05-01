# OPENCORE - ADD
from methods.regular.regular_api import validate_input
from shared.database.source_control.working_dir import WorkingDir
from shared.database.task.guide import Guide
from shared.database.task.job.job import Job
from shared.database.session import sessionMaker
from typing import Dict, List, Union
from sqlalchemy.exc import SQLAlchemyError

@routes.route('/api/v1/project/<string:project_string_id>/guide/list', methods=['POST'])
@Project_permissions.user_has_project(
    roles=["admin", "Editor", "Viewer"],
    apis_user_list=['api_enabled_builder', 'security_email_verified']
)
def guide_list_api(project_string_id) -> (Dict[str, Union[str, bool, List[Dict[str, Union[str, int]]], Dict[str, Union[str, int]]]], int):
    """
    Guide list API endpoint.
    """
    input_data = validate_input(request, {'metadata': dict})
    metadata = input_data['metadata']

    with sessionMaker.session_scope() as session:
        try:
            project = Project.get(session=session, project_string_id=project_string_id)
            guide_list, metadata = guide_view_core(session=session, metadata_proposed=metadata, project=project)
            return jsonify(guide_list=guide_list, metadata=metadata, log={'success': True}), 200
        except SQLAlchemyError as e:
            return jsonify(log={'success': False, 'error': str(e)}), 500

def guide_view_core(session, metadata_proposed: dict, project, mode="serialize", user=None) -> (List[Dict[str, Union[str, int]]], dict):
    """
    Core function for guide view.
    """
    meta = default_metadata(metadata_proposed)

    query = session.query(Guide)
    query = query.filter(Guide.project == project)

    if meta["my_stuff_only"]:
        user = User.get(session)
        query = query.filter(Guide.member_created == user.member)

    if meta['job_id'] and meta['mode'] == 'attach':
        job = Job.get_by_id(session=session, job_id=meta['job_id'])
        ignore_id_list = []

        if job.guide_default_id:
            ignore_id_list.append(job.guide_default_id)
            serialized = job.guide_default.serialize_for_list_view()
            serialized["kind"] = "default"
            meta['guide_info']['guide_default_id'] = job.guide_default_id
            meta['output_file_list'].append(serialized)

        if job.guide_review_id:
            ignore_id_list.append(job.guide_review_id)
            serialized = job.guide_review.serialize_for_list_view()
            serialized["kind"] = "review"
            meta['guide_info']['guide_review_id'] = job.guide_review_id
            meta['output_file_list'].append(serialized)

        if len(ignore_id_list) != 0:
            query = query.filter(Guide.id.notin_(ignore_id_list))

    query = query.filter(Guide.archived == False)
    query = query.limit(meta["limit"])
    query = query.offset(meta["start_index"])

    try:
        guide_list = query.all()
    except SQLAlchemyError as e:
        return [], {'error': str(e)}

    if mode == "serialize":
        for guide in guide_list:
            serialized = guide.serialize_for_list_view()
            meta['output_file_list'].append(serialized)

    meta['end_index'] = meta['start_index'] + len(guide_list)
    meta['length_current_page'] = len(meta['output_file_list'])

    if not meta['length_current_page']:
        meta['no_results_match_meta'] = True

    return meta['output_file_list'], meta

def default_metadata(metadata_proposed: dict) -> dict:
    """
    Set default metadata.
    """
    meta = {
        'limit': 25,
        'start_index': 0,
        'my_stuff_only': False,
        'field': None,
        'job_id': None,
        'mode': None,
        'output_file_list': [],
        'guide_info': {}
    }

    if 'limit' in metadata_proposed:
        meta['limit'] = min(metadata_proposed['limit'], 1000)

    if 'my_stuff_only' in metadata_proposed:
        meta['my_stuff_only'] = metadata_proposed['my_stuff_only']

    if 'field' in metadata_proposed:
        meta['field'] = metadata_proposed['field']

    if 'job_id' in metadata_proposed:
        meta['job_id'] = metadata_proposed['job_id']

    if 'mode' in metadata_proposed:
        meta['mode'] = metadata_proposed['mode']

    return meta
