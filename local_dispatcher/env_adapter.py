# OPENCORE - ADD

class EnvAdapter():

    """
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