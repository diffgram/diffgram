from shared.database.common import *


class Credential_Type_To_Job(Base):
    __tablename__ = 'credential_type_to_job'

    """
    
    
    """

    credential_type_id = Column(Integer, ForeignKey('credential_type.id'), primary_key = True)
    credential_type = relationship("Credential_Type")

    job_id = Column(Integer, ForeignKey('job.id'), primary_key = True)
    job = relationship("Job")

    kind = Column(String)  # [requires, awards, ...]

    # TODO add time created / time updated?

    def get_by_credential_and_job_ids(session,
                                      credential_type_id,
                                      job_id):
        """
        If valid input
        Returns ONE OF
            Success
                class Credential_Type_To_Job object
                None if it doesn't exist
            Error
                False
        """

        if credential_type_id is None or job_id is None:
            return False

        return session.query(Credential_Type_To_Job).filter(
            Credential_Type_To_Job.job_id == job_id,
            Credential_Type_To_Job.credential_type_id == credential_type_id).first()

    def get_by_job_id(session,
                      job_id,
                      requires_only = False,
                      awards_only = False,
                      ids_only = False):

        if job_id is None:
            return False

        if ids_only is True:
            query = session.query(Credential_Type_To_Job.credential_type_id)
        else:
            query = session.query(Credential_Type_To_Job)

        query = query.filter(Credential_Type_To_Job.job_id == job_id)

        if requires_only is True:
            query = query.filter(Credential_Type_To_Job.kind == "requires")

        if awards_only is True:
            query = query.filter(Credential_Type_To_Job.kind == "awards")

        result_list = query.all()

        if ids_only is True:
            # For some reason trying to do id only returns a type of
            # <class 'sqlalchemy.util._collections.result'>
            # Which is in format of (id, ) ie (40, ) instead of just 40
            # https://stackoverflow.com/questions/9486180/sql-alchemy-orm-returning-a-single-column-how-to-avoid-common-post-processing
            result_list = [id for (id,) in result_list]

        return result_list

    def serialize_for_list_view(self):

        credential_type = self.credential_type.serialize_for_list_view()
        credential_type['kind'] = self.kind
        return credential_type
