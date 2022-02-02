from shared.database.common import *


class Exam(Base):
    """

    This is a very thin class at the moment, but potentially can expand in future

    ie for grading summaries, auto grading,
    anti cheating things, stats, etc. etc.

    From the "Deep class" perspective, thinking of this more as a sub class to
    Jobs, making jobs deeper, than its own indepedent class?

    Oct 22/ 2019
    We don't even list the job here??
    TODO also list the job_id here in case we want to jump back ot it?

    """
    __tablename__ = 'exam'
    id = Column(Integer, primary_key = True)

    credentials_awarded = Column(Boolean)

    user_taking_exam_id = Column(Integer, ForeignKey('userbase.id'))
    user_taking_exam = relationship("User")

    def serialize(self):
        return {
            'id': self.id,
            'credentials_awarded': self.credentials_awarded,
            'user_taking_exam_id': self.user_taking_exam_id,
        }
