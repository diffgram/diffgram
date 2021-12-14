from shared.settings import settings
from shared.database.user import User


class FeatureChecker:
    """
        This class will check if any of the feature flags are available for a given
        user on a give Diffgram Installation.

        Eventually this class will be using an external feature flag system SDK.
    """

    user: User
    install_fingerprint: str
    FEATURE_FLAGS: dict  # Temp dict while feature flag system is implemented.

    def __init__(self, user):
        self.user = user
        self.install_finger_print = settings.DIFFGRAM_INSTALL_FINGERPRINT
        # This Dict will eventually be replaced by calls to our feature flag system.
        self.FEATURE_FLAGS = {
            'ON_FREE_TIER': settings.ON_FREE_TIER,
            'FREE_TIER__MAX_VIDEOS_PER_DATASET': settings.FREE_TIER__MAX_VIDEOS_PER_DATASET,
            'FREE_TIER__MAX_USERS_PER_PROJECT': settings.FREE_TIER__MAX_USERS_PER_PROJECT,
            'FREE_TIER__MAX_IMAGES_PER_DATASET': settings.FREE_TIER__MAX_IMAGES_PER_DATASET,
        }

    def get_flag(self, flag_name):
        return self.FEATURE_FLAGS[flag_name]
