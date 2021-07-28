from shared.database.system_events.system_events import SystemEvents
from shared.system_startup.system_startup_base import SystemStartupBase


class DefaultServiceSystemStartupChecker(SystemStartupBase):

    def __init__(self):
        self.service_name = 'default_service'

    def execute_startup_checks(self):
        SystemEvents.system_startup_events_check(self.service_name)
