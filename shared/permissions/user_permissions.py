# OPENCORE - ADD
from werkzeug.exceptions import Forbidden


class User_Permissions():
    """
    We could have this as it's own wrapper
    But since we already get the user object in a variety of other
    things, it just makes more sense to have it as a sub thing I think

    Maybe in future can have some kind of general
    @permissions( type_of_permissions, api_permissions, other.. etc)...


    """

    def general(user, apis_user_list):

        if user.security_disable_global is True:
            raise Forbidden("No access. (global)")

        result = User_Permissions.check_all_apis(
            apis_required_list = apis_user_list,
            user = user)

    def check_all_apis(apis_required_list,
                       user):

        if not apis_required_list:
            return True

        for api in apis_required_list:
            User_Permissions.check_api(
                api_to_check = api,
                user = user)

    def check_api(api_to_check,
                  user):

        """
        apis_required, a list of names of apis that
        are required

        If an API is in the list, it must be enabled
        """

        # special cases
        if api_to_check == "builder_or_trainer":
            if user.api_enabled_builder is True or \
                user.api_enabled_trainer is True:
                return True

        # Default case
        if getattr(user, api_to_check) is not True:
            raise Forbidden("API not enabled.")
