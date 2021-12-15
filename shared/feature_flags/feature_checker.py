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
            'FREE_TIER__MAX_VIDEOS_PER_DATASET',
            'FREE_TIER__MAX_USERS_PER_PROJECT',
            'FREE_TIER__MAX_IMAGES_PER_DATASET',
            'FREE_TIER__MAX_TEXT_FILES_PER_DATASET',
            'FREE_TIER__MAX_SENSOR_FUSION_FILES_PER_DATASET',
            'FREE_TIER__MAX_FRAMES_PER_VIDEO',
            'FREE_TIER__MAX_INSTANCES_PER_EXPORT',
            'FREE_TIER__MAX_PROJECTS',
        ]

    def get_or_create_free_plan(self):
        plant_template = PlanTemplate.get_by_public_name(
            session = self.session,
            public_name = 'Free'
        )
        if not plant_template:
            plant_template = PlanTemplate.create_free_plan(session = self.session)

        plan = Plan.new(
            session = self.session,
            member = self.user.member,
            plan_template = plant_template,
            premium_plan_user_count = -1,
            is_annual_pricing = False,
            calculated_charge = -1,
            per_user_final = -1,
            marketing_promo_code = '',
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

    def get_flag(self, flag_name):
        if not settings.ALLOW_PLANS:
            return None

        if flag_name not in self.FEATURE_FLAGS:
            return None

        plan = None
        if self.user:
            if self.user.default_plan:
                plan = self.user.default_plan
                logger.info('User on plan {}'.format(plan.template.public_name))
            else:
                plan = self.get_or_create_free_plan()
                # Attach free plan to users who don't have the plan
                self.user.default_plan = plan
                self.session.add(self.user)
                logger.info('Attached new free plan to user {}'.format(self.user.id))

        elif self.project:
            plan = self.project.plan
            if not plan:
                plan = self.get_or_create_free_plan()
                # Attach free plan to project that don't have the plan
                self.project.plan = plan
                self.session.add(self.project)
                logger.info('Attached new free plan to project {}'.format(self.project.project_string_id))
            logger.info('project on plan {}'.format(plan.template.public_name))
        if not plan:
            return None

        plan_template = plan.template
        if flag_name == 'FREE_TIER__MAX_VIDEOS_PER_DATASET':
            return plan_template.limit_files
        if flag_name == 'FREE_TIER__MAX_USERS_PER_PROJECT':
            return plan_template.limit_users_per_project
        if flag_name == 'FREE_TIER__MAX_IMAGES_PER_DATASET':
            return plan_template.limit_files
        if flag_name == 'FREE_TIER__MAX_TEXT_FILES_PER_DATASET':
            return plan_template.limit_files
        if flag_name == 'FREE_TIER__MAX_SENSOR_FUSION_FILES_PER_DATASET':
            return plan_template.limit_files
        if flag_name == 'FREE_TIER__MAX_FRAMES_PER_VIDEO':
            return plan_template.limit_files
        if flag_name == 'FREE_TIER__MAX_INSTANCES_PER_EXPORT':
            return plan_template.limit_instances
        if flag_name == 'FREE_TIER__MAX_PROJECTS':
            return plan_template.limit_projects
