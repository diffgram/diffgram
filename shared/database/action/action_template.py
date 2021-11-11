from shared.database.common import *


class Action_Template(Base):
    """

    For adding more information to action kind.
    ie the "kind" may be "brain"
    and there is a Action_Template.kind == "brain".

    The goal is to be able to have say a list of things a user
    can select from,
    and add more stuff here over time (ie if a kind is available)
    or available for certain users etc...

    Called templated and not kind since Action.kind is already reserved,
    it's a Template of Action Kinds.

    For now templates are assumed to be global,
    but in future could have per project or custom made ones

    """

    __tablename__ = 'action_template'
    id = Column(Integer, primary_key = True)

    public_name = Column(String())

    # Kind matches Action.kind
    kind = Column(String())

    category = Column(String())

    is_available = Column(Boolean, default = True)

    # Future if we allow non global templates
    # Could store contraints here?
    """
    constraints = Column(MutableDict.as_mutable(JSONEncodedDict), 
                         default = {
                             'something' : []
                             })
    """

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys = [member_updated_id])

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

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
