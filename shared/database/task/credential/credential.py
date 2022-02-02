from shared.database.common import *


class Credential(Base):
    """

    A user may have many credentials

    A task may require many credentials
    Pay rates may be based on credentials...

    A credential could be any thing from passing an exam
    to a real world credential (ie medical degree)...

    Could also be things like "reviewer" ... or "level"

    """
    __tablename__ = 'credential'
    id = Column(Integer, primary_key = True)

    credential_type_id = Column(Integer, ForeignKey('credential_type.id'))
    credential_type = relationship("Credential_Type")

    user_id = Column(Integer, ForeignKey('userbase.id'))
    user = relationship("User")

    # Org?

    status = Column(String())  # or status?
    #  [ valid / Active / accepted, in approval, completed, hidden etc. ]

    # qualifications?

    external_id = Column(String())

    # Question Sept 5, 2019, why would we want an image id here
    # if we are referencing a credential type?
    image_id = Column(Integer, ForeignKey('image.id'))
    image = relationship("Image")

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    # How do we want to express expiry? as  datetime or?

    """
    Efficiency?
        Past speed awards
    Rating / badges (like "great xyz")

    Real world stuff
        link to scan / image
        id... 
        type...

    Passed "xyz" exam
        how do we represent that? ie link to a past job

    History?

    """

    def new(
        user,
        image = None,
        credential_type = None,
        status = "active",
        external_id = None
    ):

        credential = Credential(
            credential_type = credential_type,
            image = image,
            user = user,
            status = status,
            external_id = external_id
        )
        return credential

    @staticmethod
    def get_by_user_id(session,
                       user_id,
                       status_is_valid = True):

        if user_id is None:
            return False

        query = session.query(Credential).filter(
            Credential.user_id == user_id)

        if status_is_valid is True:
            query = query.filter(Credential.status == "active")

        return query.all()

    def serialize(self):

        image = None
        if self.image:
            image = self.image.serialize()

        credential_type = None
        if self.credential_type:
            credential_type = self.credential_type.serialize_for_list_view()

        return {
            'id': self.id,
            'status': self.status,
            'credential_type': credential_type,
            'image': image,
            'time_created': self.time_created,
            'time_updated': self.time_updated
        }
