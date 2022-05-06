from shared.database.common import *
from typing import List
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.dialects.postgresql import JSONB


class Action_Template(Base, SerializerMixin):
    """
        This represents any of the possible "step" options when building a flow.
        For example:
            - Prelabel Data
            - Add to Task Template
            - Send Email
            - Post to Webhook
        Most of these are added as part of the alembic migrations on database creation.
        For example check:
            alembic_2021_11_12_10_08_7059bb6bc019_add_default_action_templates.py
        for the default templates available.

    """

    __tablename__ = 'action_template'
    id = Column(Integer, primary_key = True)

    public_name = Column(String())

    icon = Column(String())

    description = Column(String())

    trigger_data = Column(MutableDict.as_mutable(JSONB))

    condition_data = Column(MutableDict.as_mutable(JSONB))

    completion_condition_data = Column(MutableDict.as_mutable(JSONB))

    # Kind matches Action.kind
    kind = Column(String())

    category = Column(String())

    is_available = Column(Boolean, default = True)
    is_global = Column(Boolean, default = True)

    # Future if we allow non global templates
    # Could store contraints here?
    """
    constraints = Column(MutableDict.as_mutable(JSONEncodedDict), 
                         default = {
                             'something' : []
                             })
    """

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship('Member', foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship('Member', foreign_keys = [member_updated_id])

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    @staticmethod
    def list(session) -> List["Action_Template"]:
        """
            Returns all Action templates available in the installation.
        """

        return session.query(Action_Template).all()

    @staticmethod
    def get_by_kind(session,
                    kind):
        """

        Assume templates to be global for now

        Assumes kind already checked / valid,
        ie by route_kind_using_strategy_pattern


        """

        return session.query(Action_Template).filter(
            Action_Template.kind == kind).first()

    @staticmethod
    def get_by_id(session, id):
        return session.query(Action_Template).filter(
            Action_Template.id == id).first()

    @staticmethod
    def new(session,
            public_name,
            icon,
            description,
            kind,
            category,
            trigger_data,
            condition_data,
            completion_condition_data,
            is_global = True):
        result = Action_Template(
            public_name = public_name,
            kind = kind,
            category = category,
            icon = icon,
            description = description,
            trigger_data = trigger_data,
            condition_data = condition_data,
            completion_condition_data = completion_condition_data,
            is_global = is_global,
        )

        session.add(result)
        session.flush()
        return result

    def serialize(self):
        data = self.to_dict(rules = (
            '-member_created',
            '-member_updated'))

        return data
