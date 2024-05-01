# Prevents running tests in non-testing environments
# --------------------------------------------------
# This code checks if the DIFFGRAM_SYSTEM_MODE setting is equal to 'testing'. If not, it raises an exception
# to prevent any tests from being run in other environments or databases. This is an important measure
# to ensure that tests are run in a controlled and predictable environment, and to avoid unintended
# consequences of running tests in production or other sensitive environments.
#
# However, this approach has some limitations. Currently, configuration data for different deployment
# phases (local, testing, staging, production) is handled in the shared.settings module, which may not
# be ideal. It would be better to have a more robust and flexible solution for managing configuration
# data for different environments.
#
# In summary, this line of code is a safety measure to prevent tests from running in non-testing
# environments, but it also highlights the need for a better solution for handling configuration data
# for different deployment phases.
