# OPENCORE - ADD
from shared.database.common import *


class User_To_Job(Base):
    __tablename__ = 'user_to_job'

    """
    WIP 

    Jobs linked to users
    
    """

    job_id = Column(Integer, ForeignKey('job.id'), primary_key=True)
    job = relationship("Job")

    user_id = Column(Integer, ForeignKey('userbase.id'), primary_key=True)
    user = relationship("User")

    status = Column(String(), default="active")
    #  [ Active / accepted, in approval, completed, hidden etc. ]
    # More advanced "Application" class in the future maybe?

    trainer_auction_payout_per_instance_last = Column(Integer)

    def serialize_trainer_info_default(self):

        return {
            'status': self.status
        }

    def serialize(self):
        # Trying out a new id only
        return self.user_id

    def get_job_ids_from_user(session,
                              user_id):
        valid_job_ids_list = []
        user_to_job_relations_list = User_To_Job.get_all_by_user_id(
            session=session,
            user_id=user_id)
        for user_to_job in user_to_job_relations_list:
            valid_job_ids_list.append(user_to_job.job_id)

        return valid_job_ids_list

    def get_all_by_user_id(session,
                           user_id,
                           status_is_active=False,
                           count_only=False):

        if user_id is None:
            return False

        query = session.query(User_To_Job).filter(
            User_To_Job.user_id == user_id)

        if status_is_active is True:
            query = session.query(User_To_Job).filter(
                User_To_Job.status == "active")

        if count_only is True:
            return query.count()

        return query.all()

    @staticmethod
    def get_single_by_ids(session,
                          user_id,
                          job_id):

        if user_id is None or job_id is None:
            return False

        query = session.query(User_To_Job).filter(
            User_To_Job.user_id == user_id,
            User_To_Job.job_id == job_id)

        return query.first()

    @staticmethod
    def get_by_job_id(session,
                      job_id):

        if job_id is None:
            return False

        query = session.query(User_To_Job).filter(
            User_To_Job.job_id == job_id)

        return query.all()

    @staticmethod
    def list(
            session,
            user_id_ignore_list: list = None,
            job=None,
            serialize=False,
            user = None):

        query = session.query(User_To_Job)

        if user_id_ignore_list:
            query = query.filter(
                User_To_Job.user_id.notin_(user_id_ignore_list))

        if job:
            query = query.filter(User_To_Job.job == job)

        if user:
            query = query.filter(User_To_Job.user == user)

        if serialize == True:
            # TODO this could be part of generic
            query_results_list = query.all()
            out = []
            for result in query_results_list:
                out.append(result.serialize())
            return out

        return query.all()
