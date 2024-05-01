from typing import List, Optional

import methods.regular.regular_api as regular_api
from shared.database.task.job import Job
from shared.database.task.credential import Credential_Type
from shared.database.task.credential_type_to_job import Credential_Type_To_Job
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel

class CredentialTypeAttachRequest(BaseModel):
    credential_type_list: List[int]
    job_id: int
    kind: str
    add_or_remove: str

@regular_api.routes.route('/api/v1/credential/type/attach/job', methods=['POST'])
@regular_api.limiter.limit("20 per day")
def credential_type_attach_to_job_api() -> dict:
    """
    API to attach credential to a job
    Basic value quality checking
    Then calls ct_to_job_core()
    Permissions checked at ct_to_job_core()
    """
    input_data = CredentialTypeAttachRequest(**regular_api.regular_input.master(request=request).get('input'))

    with regular_api.sessionMaker.session_scope() as session:
        for credential_type_id in input_data.credential_type_list:
            credential_type = Credential_Type.get_by_id(session, credential_type_id)
            if not credential_type:
                return regular_api.jsonify(log={'error': {'credential_type': 'Credential type not found'}}), 400

            result, log, ct_to_job = ct_to_job_core(session=session,
                                                    log=log,
                                                    credential_type=credential_type,
                                                    job_id=input_data.job_id,
                                                    kind=input_data.kind,
                                                    add_or_remove=input_data.add_or_remove
                                                    )
            if not result:
                return regular_api.jsonify(log=log), 400

        return regular_api.jsonify(log={'success': True}), 200

def ct_to_job_core(session,
                   log: dict,
                   credential_type: Credential_Type,
                   job_id: int,
                   kind: str,
                   add_or_remove: str
                   ) -> tuple[bool, dict, Optional[Credential_Type_To_Job]]:
    """
    Constructs credential to job link
    Basic value checking

    Arguments
        session, db session
        log, regular log dict
        credential_type, class Credential_Type object
        job, class Job object
        kind, string

    Returns
        result, bool
        log, updated log
        ONE OF
            credential_type_to_job object
            None
    """
    job = Job.get_by_id(session, job_id)

    kind = kind.lower()
    if kind not in ["requires", "awards", "remove"]:
        log['error'] = {'kind': "Invalid kind"}
        return False, log, None

    add_or_remove = add_or_remove.lower()
    if add_or_remove not in ["add", "remove"]:
        log['error'] = {'kind': "Invalid add_or_remove"}
        return False, log, None

    if not job:
        log['error'] = {'job': "Invalid job"}
        return False, log, None

    try:
        existing = session.query(Credential_Type_To_Job).filter_by(credential_type_id=credential_type.id, job_id=job.id).first()

        if add_or_remove == "add":
            if existing:
                log['error'] = {'credential_type': "Existing credential attachement"}
                return False, log, None

            credential_type_to_job = Credential_Type_To_Job()
            session.merge(credential_type_to_job)

            credential_type_to_job.credential_type = credential_type
            credential_type_to_job.job = job
            credential_type_to_job.kind = kind

            return True, log, credential_type_to_job

        if add_or_remove == "remove":
            if not existing:
                log['error'] = {'credential_type': "No existing credential"}
                return False, log, None

            session.delete(existing)

        session.commit()

    except SQLAlchemyError as e:
        session.rollback()
        log['error'] = {'database': f"Error while processing: {str(e)}"}
        return False, log, None

    return True, log, None
