try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *

from shared.database.account.plan import Plan
from shared.database.account.plan_template import PlanTemplate


@routes.route('/api/v1/project/<string:project_string_id>' +
              '/account/plan/new',
              methods = ['POST'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
@limiter.limit("3 per day")
def new_plan_api(project_string_id):
    """

    """
    spec_list = [
        {"premium_plan_user_count": {
            'kind': int,
            'required': True
        }
        },
        {"plan_template_public_name": {
            'kind': str,
            'required': True
        }
        },
        {"calculated_charge": {
            'kind': int,
            'required': True
        }
        },
        {"annual_pricing": {
            'kind': bool,
            'required': True
        }
        },
        {"per_user_final": {
            'kind': int,
            'required': True
        }
        },
        {"marketing_promo_code": {
            'kind': str,
            'required': False
        }
        },
        {"marketing_promo_rate_found": {
            'kind': str,
            'required': False
        }
        },
        {"marketing_plan_rate": {
            'kind': int,
            'required': False
        }
        },
        {"marketing_savings": {
            'kind': int,
            'required': False
        }
        },
        {"marketing_total": {
            'kind': int,
            'required': False
        }
        },
        {"roi_monthly_engineering_cost": {
            'kind': int,
            'required': False
        }
        },
        {"roi_monthly_supervisor_cost": {
            'kind': int,
            'required': False
        }
        },
        {"roi_project_value": {
            'kind': int,
            'required': False
        }
        },
        {"roi_eng_automation_benefit": {
            'kind': float,
            'required': False
        }
        },
        {"roi_annotation_productivity_benefit": {
            'kind': float,
            'required': False
        }
        },
        {"roi_project_quality_improvement": {
            'kind': float,
            'required': False
        }
        },
        {"roi_total_benefit": {
            'kind': int,
            'required': False
        }
        },
        {"roi_multiple": {
            'kind': int,
            'required': False
        }
        }]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    if not settings.ALLOW_STRIPE_BILLING:
        return jsonify(log = {'error': {'ALLOW_STRIPE_BILLING': 'Not Allowed for this version'}}), 400

    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)

        if project.api_billing_enabled is not True:
            log['error']['billing'] = "Please save a credit card to enable billing first."
            return jsonify(log = log), 400

        print('public', input['plan_template_public_name'])
        plan_template = PlanTemplate.get_by_public_name(
            session = session,
            public_name = input['plan_template_public_name'])
        if plan_template is None:
            log['error']['plan_template'] = "Invalid plan_template_public_name"
            return jsonify(log = log), 400

        if plan_template.is_public is not True:
            log['error']['plan_template'] = "No public plan found"
            return jsonify(log = log), 400
        if plan_template.is_available is not True:
            log['error']['plan_template'] = "Plan not available"
            return jsonify(log = log), 400

        # Get by primary user? or security concerns here
        # account = Account.get_by_id(session, account_id)
        user = User.get(session = session)

        project_list = user.projects

        # TODO using project.plan as a proxy
        # But really should have more "definitive" way to get plan...

        # Question do we want this here? gotta be a better way to check....
        if project is None:
            log['error']['project'] = "No project. Please create a project first."
            return jsonify(log = log), 400

        if project.plan:

            # TODO update old plan? ie end date / is active?

            # only allow switching from free to paid plans
            # once on a paid plan contact us to update it...
            if project.plan.template.is_free is False:
                log['error']['plan'] = "Already on a paid plan. Please contact us to update your plan."
                return jsonify(log = log), 400

        plan = Plan.new(
            plan_template = plan_template,
            member = user.member,

            premium_plan_user_count = input['premium_plan_user_count'],
            is_annual_pricing = input['annual_pricing'],
            calculated_charge = input['calculated_charge'],
            per_user_final = input['per_user_final'],

            marketing_promo_code = input['marketing_promo_code'],
            marketing_promo_rate_found = input['marketing_promo_rate_found'],
            marketing_plan_rate = input['marketing_plan_rate'],
            marketing_savings = input['marketing_savings'],
            marketing_total = input['marketing_total'],

            roi_monthly_engineering_cost = input['roi_monthly_engineering_cost'],
            roi_monthly_supervisor_cost = input['roi_monthly_supervisor_cost'],
            roi_project_value = input['roi_project_value'],
            roi_eng_automation_benefit = input['roi_eng_automation_benefit'],
            roi_annotation_productivity_benefit = input['roi_annotation_productivity_benefit'],
            roi_project_quality_improvement = input['roi_project_quality_improvement'],

            roi_total_benefit = input['roi_total_benefit'],
            roi_multiple = input['roi_multiple']
        )

        session.add(plan)
        session.flush()

        result = plan.update_projects(
            session = session,
            project_list = project_list,
            member = user.member)

        # EMAIL
        # Assumption this is for upgraded plans

        subject = "New paid plan"

        # Wrapping with str in case it's None. Shouldn't be possible but just in case

        message = str(project.name) + " project with user " + str(project.user_primary.email) + \
                  " user count:  " + str(plan.premium_plan_user_count)

        communicate_via_email.send(
            "anthony@diffgram.com", subject, message)

        # TODO reference old plan to new plan?

        # TODO send welcome email
        # TODO send email alert to us that a plan was purchashed?

        log['success'] = True
        return jsonify(log = log), 200


def limits():
    """
    ie allow a user to upgrade their plan, but
    not downgrade it?
    """
    pass


def update_plan():
    pass
