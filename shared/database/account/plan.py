from shared.database.common import *
from shared.database.account.plan_template import PlanTemplate


class Plan(Base):
    __tablename__ = 'plan'

    """

    A representation of the customer's billing information.

    An instance of a PlanTempate

    To track customer specific things, ie date started etc.

    A customer may have more than one plan over time

    In the context that it is common for customers to switch plans
    and for plans to change (ie more or less expensive, features etc.)

    
    """

    id = Column(Integer, primary_key = True)

    template_id = Column(Integer, ForeignKey('plan_template.id'))
    template = relationship(PlanTemplate,
                            foreign_keys = [template_id])
    # Just calling this template instead of "plan_template"
    # for easier reading   ie project.plan.template.value

    is_active = Column(Boolean, default = True)

    premium_plan_user_count = Column(Integer)  # currency, 100 = $1
    is_annual_pricing = Column(Boolean)
    # if is_annual_pricing is False then it's monthly
    # calculated_charge is amount shown for period (eg annual/monthly)
    calculated_charge = Column(Integer)  # currency, 100 = $1
    per_user_final = Column(Integer)  # check value ~= calculated_charge / premium_plan_user_count

    # User / front end supplied?
    marketing_promo_code = Column(String)
    marketing_promo_rate_found = Column(Float)
    marketing_plan_rate = Column(Integer)
    marketing_savings = Column(Integer)
    marketing_total = Column(Integer)

    # State of calculator when ordered?
    roi_monthly_engineering_cost = Column(Integer)  # not currency? 1 = $1
    roi_monthly_supervisor_cost = Column(Integer)
    roi_project_value = Column(Integer)
    roi_eng_automation_benefit = Column(Float)
    roi_annotation_productivity_benefit = Column(Float)
    roi_project_quality_improvement = Column(Float)

    roi_total_benefit = Column(Integer)
    roi_multiple = Column(Integer)

    # feel like a lot more here over time
    # cycle_frequency ? how often we are checking

    # Credit limit?
    # or is this part of account?

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys = [member_updated_id])

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_ended = Column(DateTime)

    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    @staticmethod
    def list(
        session,
        is_active = True):
        """
        list plans

        session, db session object

        defaults to returning plan objects

        """

        query = session.query(Plan)

        query = query.filter(
            Plan.is_active == is_active)

        return query.all()

    @staticmethod
    def get_by_id(
        session,
        plan_id):

        query = session.query(Plan)

        query = query.filter(Plan.id == plan_id)

        return query.first()

    @staticmethod
    def new(
        session,
        member,
        plan_template,

        premium_plan_user_count: int,
        is_annual_pricing: bool,
        calculated_charge: int,
        per_user_final: int,

        marketing_promo_code: str,
        marketing_promo_rate_found: float,
        marketing_plan_rate: int,
        marketing_savings: int,
        marketing_total: int,

        roi_monthly_engineering_cost: int,
        roi_monthly_supervisor_cost: int,
        roi_project_value: int,
        roi_eng_automation_benefit: float,
        roi_annotation_productivity_benefit: float,
        roi_project_quality_improvement: float,

        roi_total_benefit: int,
        roi_multiple: int
    ):

        plan = Plan(
            template = plan_template,
            member_created = member,

            premium_plan_user_count = premium_plan_user_count,
            is_annual_pricing = is_annual_pricing,
            calculated_charge = calculated_charge,
            per_user_final = per_user_final,

            marketing_promo_code = marketing_promo_code,
            marketing_promo_rate_found = marketing_promo_rate_found,
            marketing_plan_rate = marketing_plan_rate,
            marketing_savings = marketing_savings,
            marketing_total = marketing_total,

            roi_monthly_engineering_cost = roi_monthly_engineering_cost,
            roi_monthly_supervisor_cost = roi_monthly_supervisor_cost,
            roi_project_value = roi_project_value,
            roi_eng_automation_benefit = roi_eng_automation_benefit,
            roi_annotation_productivity_benefit = roi_annotation_productivity_benefit,
            roi_project_quality_improvement = roi_project_quality_improvement,

            roi_total_benefit = roi_total_benefit,
            roi_multiple = roi_multiple
        )
        session.add(plan)
        session.flush()

        return plan

    def update_projects(
        self,
        session,
        project_list,
        member
    ):
        """
        session, db session object
        plan_template, db PlanTemplate object

        """
        # update all projcts attached to billing account?
        # Attach plan to billing account?

        for project in project_list:
            session.add(project)
            project.plan = self

        # CAUTION assumes user (to actually add default plan)
        # Save plan to user
        if member.user:
            member.user.default_plan = self
            session.add(member)

        return True
