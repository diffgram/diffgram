from shared.database.common import *


class Org_To_User(Base):
    __tablename__ = 'org_to_user'

    """
    
    
    """

    org_id = Column(Integer, ForeignKey('org.id'), primary_key = True)
    org = relationship("Org")

    user_id = Column(Integer, ForeignKey('userbase.id'), primary_key = True)
    user = relationship("User")

    # ["Admin", "Restricted Annotator"]
    user_permission_level = Column(String())  # New May 30, 2019

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    def new(session,
            org_id,
            user_id,
            user_permission_level = "Annotator"):

        org_to_user = Org_To_User(
            org_id = org_id,
            user_id = user_id,
            user_permission_level = user_permission_level)

        session.add(org_to_user)

        return org_to_user

    def get_by_user_id(session,
                       user_id,
                       data_mode = "object"):

        query = session.query(Org_To_User)

        query = query.filter(Org_To_User.user_id == user_id)

        if data_mode == "object":
            return query.all()

        if data_mode == "count":
            return query.count()

    def get_by_ids(session,
                   user_id,
                   org_id):

        query = session.query(Org_To_User)

        query = query.filter(
            Org_To_User.user_id == user_id,
            Org_To_User.org_id == org_id)

        return query.first()

    def serialize_user(self):

        user = self.user

        if user is None:
            return {'Error': 'User is None'}

        # Dec 27, 2019 need member id for front end table unique key

        return {
            'member_id': self.user.member_id,
            'first_name': self.user.first_name,
            'profile_image_thumb_url': self.user.profile_image_thumb_url,
            'username': self.user.username,
            'permission_level': self.user_permission_level,
            'member_kind': 'human'
        }
