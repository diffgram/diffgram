# OPENCORE - ADD

class EnvAdapter():

    """
    OS Environment Adapter to Python

    Goal is to convert env vars to python friendly types
    Context of for example bools not storable in env vars
    and python built-in bool(value) does not work - eg bool('False') == true!

    Inspired by https://github.com/jazzband/django-configurations/blob/master/configurations/values.py#L124
    The whole class based system felt ab it heavy to use the entire thing.
    And not sure if we are ready yet for a full fledged env loader library 

    Usage example
    import EnvAdapter
    env_adapter = EnvAdapter()
    setting_that_is_bool = env_adapter.bool(os.environ.get('setting_that_is_bool', False))

    """

    true_values = ('yes', 'y', 'true', '1')     # assumes we will use .lower()
    false_values = ('no', 'n', 'false', '0', '')

    def bool(self, value):
        # this assumes it's a string, otherwise will pass the existing value

        # Assume if already python type to just return it.
        # e.g. from a default env value.
        if isinstance(value, bool): 
            return value

        if not isinstance(value, str):
            return value

        normalized_value = value.strip().lower()

        if normalized_value in self.true_values:
            return True

        elif normalized_value in self.false_values:
            return False

        else:
            raise ValueError('Cannot interpret '
                             'boolean value {0!r}'.format(value))