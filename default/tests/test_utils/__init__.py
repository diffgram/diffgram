from shared.settings import settings

# This line is to prevent developers to run test in other databases or enviroments. We should rethink how to handle
# configuration data for the different deployment phases (local, testing, staging, production)
if settings.DIFFGRAM_SYSTEM_MODE != 'testing':
    raise Exception('DIFFGRAM_SYSTEM_MODE must be in "testing" mode to perform any kind of test')
