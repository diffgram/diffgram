from methods.regular.regular_api import *

from shared.database.task.credential.credential import Credential
from shared.database.task.credential.credential_type import Credential_Type
from shared.database.task.credential.credential_type_to_job import Credential_Type_To_Job


# TODO permissions

@routes.route('/api/v1' +
              '/credential/list',
              methods = ['POST'])
def credential_list_api():
    spec_list = [{'metadata': dict}]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)

    with sessionMaker.session_scope() as session:
        metadata_proposed = input['metadata']

        ### MAIN ###
        credential_list, metadata = credential_view_core(
            session = session,
            metadata_proposed = metadata_proposed)
        ### ###

        log['success'] = True
        return jsonify(credential_list = credential_list,
                       metadata = metadata,
                       log = log), 200


def credential_view_core(session,
                         metadata_proposed,
                         output_mode = "serialize",
                         user = None):
    """
    output_mode
        serialize is in context of web, ie serialize the resulting list
            currently defaults to this context
        objects returns the database objects, ie for auto commit

    mode_options
        Assume functions apply to all unless specfically stated


    """

    meta = default_metadata(metadata_proposed)

    start_time = time.time()
    output_file_list = []
    limit_counter = 0

    # If in context of job id

    """
    Here we are combinining two different tables
        Credential_Type_To_Job
        Credential_Type

    Credential_Type_To_Job has all of the ones already in the job
    Where as Credential_Type has all available ones

    """
    query = None
    # Caution, if query resolves to None we exit early

    if meta['job_id']:

        # Get sub query of Credential Types attached to the job
        attached_query = session.query(Credential_Type_To_Job).filter(
            Credential_Type_To_Job.job_id == meta['job_id'])
        job_link_sub_query = attached_query.subquery('job_link_sub_query')
        # Future, could apply additional filters here if needed
        credential_list_attached = attached_query.all()

        query = session.query(Credential_Type)

        if meta['mode_options'] == "job_edit":
            # We use the full Credential_Type_To_Job object later, so
            # grab the ids here (instead of querying class.id directly)
            ignore_id_list = [i.credential_type_id for i in credential_list_attached]

            # Careful to use notin_() since it will be a list (can't use != apparently.)
            query = query.filter(Credential_Type.id.notin_(ignore_id_list))

    else:
        if meta['mode_options'] in ["job_edit", "direct_route"]:

            if meta["builder_or_trainer"]["mode"] == "builder":
                query = session.query(Credential_Type)

            if meta["builder_or_trainer"]["mode"] == "trainer":
                query = session.query(Credential)

    # TODO Seperate route for Credential types
    # by project and user permissions

    # TODO review case of query potentially not being defined
    # ie if job and not job mode edit?

    # Handle edge case of no job id, and no mode option fitting...
    # May need other meta props here and not a fan of this...
    # Not super great place to catch this type of error
    # Need to think on more generic ways to handle verifying paraemters for more complex queries like this are valid
    if query is None:
        return output_file_list, meta

    # Applies to both job id and not job id
    if meta["builder_or_trainer"]["mode"] == "builder":
        project = Project.get(session = session,
                              project_string_id = meta["project_string_id"])

        query = query.filter(or_(Credential_Type.project == project,
                                 Credential_Type.public == True))

        query = query.filter(Credential_Type.archived == False)

    ### START FILTERS ###

    # TODO this is in context of "Builder" at the moment,
    # For a "Trainer" it would be the credential instances...

    if meta["my_stuff_only"] == True:

        # assumes in context of user doing search not a user passed through API
        user = User.get(session)
        ##

        if meta["builder_or_trainer"]["mode"] == "builder":
            query = query.filter(Credential_Type.member_created == user.member)

        if meta["builder_or_trainer"]["mode"] == "trainer":
            query = query.filter(Credential.user == user)

    # if meta["field"]:
    # Get field id? or ...
    # WIP
    # query = query.filter(Job.field == None)

    #### END FILTERS ###

    # Question, why do we have a mode option here at all?

    if meta['mode_options'] in ["job_edit", "job_detail", "direct_route"]:
        query = query.limit(meta["limit"])
        query = query.offset(meta["start_index"])

        credential_list = query.all()

    if output_mode == "serialize":

        if meta['job_id']:

            for credential_link in credential_list_attached:
                serialized = credential_link.serialize_for_list_view()
                output_file_list.append(serialized)
                limit_counter += 1

        if meta['mode_options'] in ["job_edit", "direct_route"]:

            # Caution, credential_list could contain
            # instances or templates... not a fan of this setup.
            for credential in credential_list:

                if meta["builder_or_trainer"]["mode"] == "builder":
                    serialized = credential.serialize_for_list_view()

                if meta["builder_or_trainer"]["mode"] == "trainer":
                    serialized = credential.serialize()

                output_file_list.append(serialized)
                limit_counter += 1

            meta['end_index'] = meta['start_index'] + len(credential_list)

    meta['length_current_page'] = len(output_file_list)

    if limit_counter == 0:
        meta['no_results_match_meta'] = True

    end_time = time.time()

    return output_file_list, meta


def default_metadata(meta_proposed):
    """
    all fields needed by listed here
    """

    server_side_limit = 1000  # Clarify this is limit of results returned PER PAGE , user can go to next page to see more results

    name = None
    field = None
    # type = None
    # status?

    meta = {}

    meta['limit'] = 25

    meta["start_index"] = 0

    # TODO use some kind of regular method for these key checks...
    meta["my_stuff_only"] = meta_proposed.get("my_stuff_only", None)
    meta["field"] = meta_proposed.get("field", None)
    meta["job_id"] = meta_proposed.get("job_id", None)

    meta["mode_view"] = meta_proposed.get("mode_view", None)
    meta["mode_options"] = meta_proposed.get("mode_options", None)
    meta["builder_or_trainer"] = meta_proposed.get("builder_or_trainer", None)
    meta["project_string_id"] = meta_proposed.get("project_string_id", None)

    """
    # WIP WIP WIP

    #meta['name'] = meta_proposed.get("name", None)
    #meta['search_term'] = meta_proposed.get('search_term', None)
    meta_limit_proposed = meta_proposed.get('limit', None)
        
    if meta_limit_proposed:
        if meta_limit_proposed <= server_side_limit:
            meta["limit"] = meta_limit_proposed
        else:
            meta["limit"] = server_side_limit
                    
    request_next_page = meta_proposed.get('request_next_page', None)

    if request_next_page is True and meta_proposed.get('previous', None):
        meta['image']["start_index"] = int(meta_proposed['previous']['image'].get('end_index', 0))
    """

    return meta
