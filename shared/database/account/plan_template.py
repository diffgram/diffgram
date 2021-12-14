from shared.database.common import *


class PlanTemplate(Base):
    __tablename__ = 'plan_template'

    """
    
    Basically the goals of this are to
     * Record all info needed to do accurate billing
     * Record info needed to record terms of contract (ie as plans change, we want to know
       who was promised what etc.?)
     * Record info needed for limits, seperate from billing?
       ie for free plans, limit of how many instances etc.

    Context that when we change plans in the future, 
    can simply create a new plan template, and leave old ones as is? 
    Or if needed can bulk update? 
    
    Ie so we had to we could have a unique plan for a specific customer, but default is shared

    see new() for an example

    **Assumption** that this gets attach to an instance of a plan
    to track customer specific things, ie date started etc.

    ie plan.template.limit_instances = something?
    
    """

    id = Column(Integer, primary_key = True)

    public_name = Column(String)
    internal_name = Column(String)

    kind = Column(String)

    limit_instances = Column(Integer)  # 1 is one instance
    limit_projects = Column(Integer)  # 1 is one project

    # Overall limit, so assume that a video file is 1 file (not counting frames here)
    limit_files = Column(Integer)
    limit_users_per_project = Column(Integer)
    limit_video_frames_per_file = Column(Integer)

    included_monthly_training_credits = Column(Integer)  # 1 is one credit

    cost_monthly = Column(Integer)  # ie 100 = $1.00

    may_buy_instances = Column(Boolean)
    cost_per_1000_instances = Column(Integer)  # ie 900 = $9
    # Assumption this is a "Standard" instance?

    cost_per_training_hour = Column(Integer)  # ie 600 = $6
    cost_annual = Column(Integer)  # Future

    # features
    # if None assume no feature?
    feature_sla = Column(String)  # ie standard, custom etc.
    feature_support = Column(String)
    feature_user_management = Column(String)

    is_available = Column(Boolean)
    is_public = Column(Boolean)
    is_free = Column(Boolean)

    # Should we have an is_paid?
    # default credit limit?

    export_models_allowed = Column(Boolean)

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    def serialize_for_user(self):
        return {
            'id': self.id,
            'public_name': self.public_name,
            'cost_monthly': self.cost_monthly,
            'cost_per_1000_instance': self.cost_per_1000_instances
        }

    def get_by_public_name(
        session,
        public_name):
        query = session.query(PlanTemplate).filter(
            PlanTemplate.public_name == public_name)

        return query.first()

    def create_premium_plan():
        return PlanTemplate.new(
            public_name = 'premium',
            internal_name = 'premium_jan_2021',
            limit_instances = None,
            limit_projects = 100,
            limit_files = 100000,
            limit_users_per_project = 20,
            limit_video_frames_per_file = 20000,
            cost_monthly = 129000,  # default cost
            cost_per_1000_instances = None,
            is_available = True,
            is_public = True,
            is_free = False,
            export_models_allowed = True,
            feature_sla = False,
            feature_support = True,
            feature_user_management = True)

    @staticmethod
    def new(public_name,
            internal_name,
            limit_instances,
            limit_projects,
            limit_files,
            limit_users_per_project,
            limit_video_frames_per_file,
            cost_monthly,
            cost_per_1000_instances,
            is_available = True,
            is_public = False,
            is_free = False,
            export_models_allowed = True,
            feature_sla = True,
            feature_support = True,
            feature_user_management = True
            ):
        """
        Assumption this is called internally
        by us

        Why do we have this here?
        Doesn't really make any sense...
        """

        plan_template = PlanTemplate(
            public_name = public_name,
            internal_name = internal_name,
            limit_instances = limit_instances,
            limit_projects = limit_projects,
            limit_files = limit_files,
            limit_users_per_project = limit_users_per_project,
            limit_video_frames_per_file = limit_video_frames_per_file,
            cost_monthly = cost_monthly,
            cost_per_1000_instances = cost_per_1000_instances,
            is_available = is_available,
            is_public = is_public,
            is_free = is_free,
            export_models_allowed = export_models_allowed,
            feature_sla = feature_sla,
            feature_support = feature_support,
            feature_user_management = feature_user_management
        )
        return plan_template
