# OPENCORE - ADD
from abc import ABC, abstractmethod


class TaskTemplateAfterLaunchStrategy(ABC):
    """
        This is an abstract class to define a behaviour after launching
        a job. Since behaviour may change depending on task template
        configs, different implementations of this class will exist.
        The class is being used to implement a Strategy Pattern for
        the different types of job launches, where the context class will be LaunchControl class:
        https://en.wikipedia.org/wiki/Strategy_pattern
    """

    def __init__(self, session, task_template, log):
        self.session = session
        self.task_template = task_template
        self.log = log


    @abstractmethod
    def execute_after_launch_strategy(self):
        raise NotImplementedError
