from shared.settings import settings
from shared.database.user import User
from shared.database.account.plan_template import PlanTemplate
from shared.database.account.plan import Plan
from sqlalchemy.orm.session import Session
from shared.database.project import Project
from shared.shared_logger import get_shared_logger

logger = get_shared_logger()


class FeatureChecker:
    """
        This class will check if any of the feature flags are available for a given
        user on a give Diffgram Installation.

        Eventually this class will be using an external feature flag system SDK.
    """

    user: User
    session: Session
    project: Project
    install_fingerprint: str
    FEATURE_FLAGS: list  # Temp list while feature flag system is implemented.

    def __init__(self, session: Session, user: User, project: Project):
        self.user = user
        self.project = project
        self.session = session
        self.install_finger_print = settings.DIFFGRAM_INSTALL_FINGERPRINT
        # This Dict will eventually be replaced by calls to our feature flag system.
        self.FEATURE_FLAGS = [
            'MAX_VIDEOS_PER_DATASET',
            'MAX_USERS_PER_PROJECT',
            'MAX_IMAGES_PER_DATASET',
            'MAX_TEXT_FILES_PER_DATASET',
            'MAX_SENSOR_FUSION_FILES_PER_DATASET',
            'MAX_FRAMES_PER_VIDEO',
            'MAX_INSTANCES_PER_EXPORT',
            'MAX_PROJECTS',
        ]

    def get_free_plan_template(self):
        if settings.IS_OPEN_SOURCE:
            return PlanTemplate.get_by_internal_name(
                session = self.session,
                internal_name = 'open_source_free_plan'
            )
        else:
            return PlanTemplate.get_by_internal_name(
                session = self.session,
                internal_name = 'default_free_plan'
            )

    def get_or_create_free_plan(self):
        plan_template = self.get_free_plan_template()
        if not plan_template:
            plan_template = PlanTemplate.create_free_plan(session = self.session)

        PlanTemplate.update_default_free_plan_values(session = self.session, plan_template = plan_template)

        plan = Plan.new(
            session = self.session,
            member = self.user.member if self.user else None,
            plan_template = plan_template,
            premium_plan_user_count = -1,
            is_annual_pricing = False,
            calculated_charge = -1,
            per_user_final = -1,
            marketing_promo_code = None,
            marketing_promo_rate_found = -1,
            marketing_plan_rate = -1,
            marketing_savings = -1,
            marketing_total = -1,
            roi_monthly_engineering_cost = -1,
            roi_monthly_supervisor_cost = -1,
            roi_project_value = -1,
            roi_eng_automation_benefit = -1,
            roi_annotation_productivity_benefit = -1,
            roi_project_quality_improvement = -1,
            roi_total_benefit = -1,
            roi_multiple = -1

        )
        return plan

    def get_limit_from_plan(self, flag_name):
        if flag_name not in self.FEATURE_FLAGS:
            return None

        plan = None

        # 1. Get from Project
        if self.project:
            plan = self.project.plan

        # 2. Get from user
        if not plan:
            if self.user:
                plan = self.user.default_plan
                logger.info(f"User on plan {plan.template.public_name}")

        # 3. Failsafe, assume free
        if not plan:
            plan = self.get_or_create_free_plan()
            # Attach free plan to project that don't have the plan
            self.project.plan = plan
            self.session.add(self.project)
            logger.info(f"Attached new free plan to project {self.project.project_string_id}")

            # Attach free plan to users who don't have the plan
            self.user.default_plan = plan
            self.session.add(self.user)
            logger.info(f"Attached new free plan to user {self.user.id}")

            logger.info(f"project on plan {plan.template.public_name}")
        if not plan:
            return None

        plan_template = plan.template
        if flag_name == 'MAX_VIDEOS_PER_DATASET':
            return plan_template.limit_files
        if flag_name == 'MAX_USERS_PER_PROJECT':
            return plan_template.limit_users_per_project
        if flag_name == 'MAX_IMAGES_PER_DATASET':
            return plan_template.limit_files
        if flag_name == 'MAX_TEXT_FILES_PER_DATASET':
            return plan_template.limit_files
        if flag_name == 'MAX_SENSOR_FUSION_FILES_PER_DATASET':
            return plan_template.limit_files
        if flag_name == 'MAX_FRAMES_PER_VIDEO':
            return plan_template.limit_files
        if flag_name == 'MAX_INSTANCES_PER_EXPORT':
            return plan_template.limit_instances
        if flag_name == 'MAX_PROJECTS':
            return plan_template.limit_projects
