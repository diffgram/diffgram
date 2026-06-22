from methods.regular.regular_api import *  # Importing necessary functions from the regular_api module
from shared.database.sync_events.sync_event import SyncEvent  # Importing SyncEvent class from sync_event module

@routes.route('/api/v1/sync-events/list', methods=['POST'])  # Defining the API endpoint for sync-events list
def sync_events_list():
    spec_list = [{'metadata': dict}]  # Defining the expected input format
    log, input, untrusted_input = regular_input.master(request=request, spec_list=spec_list)  # Validating and parsing the input

    if len(log["error"].keys()) >= 1:  # If there are any errors in the input, return them
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:  # Starting a new database session
        # Extracting the metadata from the input
        metadata = input['metadata']
        sync_events = sync_events_list_core(session=session,
                                            date_from=metadata.get('date_from'),
                                            date_to=metadata.get('date_to'),
                                            status=metadata.get('status'),
                                            job_id=metadata.get('job_id'),
                                            dataset_source_id=metadata.get('dataset_source_id'),
                                            dataset_destination_id=metadata.get('dataset_destination_id'),
                                            created_task_id=metadata.get('created_task_id'),
                                            completed_task_id=metadata.get('completed_task_id'),
                                            event_effect_type=metadata.get('event_effect_type'),
                                            event_trigger_type=metadata.get('event_trigger_type'),
                                            incoming_directory_id=metadata.get('incoming_directory_id'),
                                            project_string_id=metadata.get('project_string_id'),
                                            )
        log['success'] = True  # Setting the success flag to True
        return jsonify(log=log, sync_events_list=sync_events), 200  # Returning the sync events list and success status


def sync_events_list_core(session,
                          date_from=None,
                          date_to=None,
                          status=None,
                          job_id=None,
                          dataset_source_id=None,
                          dataset_destination_id=None,
                          created_task_id=None,
                          completed_task_id=None,
                          event_effect_type=None,
                          event_trigger_type=None,
                          incoming_directory_id=None,
                          project_string_id=None,
                          limit=30,
                          output_mode='serialize'):
    # Checking permissions for the project
    Project_permissions.by_project_core(project_string_id=project_string_id, Roles=["admin", "Editor", "Viewer"])
    project = Project.get(session, project_string_id)  # Getting the project object

    query = session.query(SyncEvent).filter(SyncEvent.project_id == project.id)  # Querying the sync events for the project

    # Adding filters to the query based on the input
    if date_from:
        query = query.filter(SyncEvent.created_date >= date_from)
    if date_to:
        query = query.filter(SyncEvent.created_date <= date_to)
    if status:
        query = query.filter(SyncEvent.status == status)
    if job_id:
        query = query.filter(SyncEvent.job_id == job_id)
    if dataset_source_id:
        query = query.filter(SyncEvent.dataset_source_id == dataset_source_id)
    if dataset_destination_id:
        query = query.filter(SyncEvent.dataset_destination_id == dataset_destination_id)
    if created_task_id:
        query = query.filter(SyncEvent.created_task_id == created_task_id)
    if completed_task_id:
        query = query.filter(SyncEvent.completed_task_id == completed_task_id)
    if event_effect_type:
        query = query.filter(SyncEvent.event_effect_type == event_effect_type)
    if event_trigger_type:
        query = query.filter(SyncEvent.event_trigger_type == event_trigger_type)
    if incoming_directory_id:
        query = query.filter(SyncEvent.incoming_directory_id == incoming_directory_id)

    query = query.order_by(SyncEvent.created_date.desc())  # Ordering the query by the created date
    query = query.limit(limit)  # Limiting the number of results
    sync_events_list = query.all()  # Executing the query and getting the results

    # Serializing the results if output_mode is set to 'serialize'
    result = sync_events_list if output_mode == "objects" else [sync_event.serialize() for sync_event in sync_events_list]

    return result
