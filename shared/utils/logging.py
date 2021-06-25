from shared.settings import settings
import logging
from dataclasses import dataclass
from typing import Any


@dataclass
class DiffgramLogger:
    logger_name: str
    logger: Any = None
    output_test_messages: bool = False

    logging_initialized = {}
    """
    Usage example

        default_abstract_logger = DiffgramLogger('default')

        default_abstract_logger.configure_concrete_logger(
	            system_mode = settings.DIFFGRAM_SYSTEM_MODE)

        logger = default_abstract_logger.get_concrete_logger()

    Assumption
        The default namespace is available in regular_api for the respective service
            so by default both the abstract and concrete logger are available.

        if we want to use a dedicated isolated logger for a separate module for some reason
        we can do

        default_abstract_logger = DiffgramLogger('service_name_isolated_module_name')
        or something like that

    Reconfigure
        Call configure_concrete_logger() anytime


    """

    def get_concrete_logger(self):
        return self.logger

    def configure_concrete_logger(self,
                                  system_mode: str):

        self.logger = None

        if system_mode in ['sandbox', 'testing', 'testing_e2e'] or \
            settings.RUNNING_LOCALLY == True:
            self.logger = self.configure_sandbox_testing_logger()
        elif system_mode == 'production':
            # self.logger = self.configure_sandbox_testing_logger()
            try:
                self.logger = self.configure_gcp_logger()
            except:
                self.logger = self.configure_sandbox_testing_logger()

        if self.logger is None and not DiffgramLogger.logging_initialized.get(self.logger_name):
            # Default to always create a logger, eg in case of some settings being mis-configured
            self.logger = self.configure_default_logger()
        return self.logger

    def configure_gcp_logger(self):
        # Imports the Google Cloud client library

        if DiffgramLogger.logging_initialized.get(self.logger_name):
            return logging.getLogger(self.logger_name)

        from google.cloud import logging as gcp_logging
        from google.cloud.logging.handlers import CloudLoggingHandler

        # Instantiates a client
        fmt_str = '[%(asctime)s] %(levelname)s %(module)s.py @ line %(lineno)d: %(message)s'
        logging.basicConfig(level = logging.INFO, format = fmt_str)
        logging_client = gcp_logging.Client()
        handler = CloudLoggingHandler(logging_client, name = self.logger_name)
        handler.setFormatter(logging.Formatter(fmt_str))
        logger = logging.getLogger(self.logger_name)
        logger.addHandler(handler)
        logger.info('Logger {} setup success.'.format(self.logger_name))
        DiffgramLogger.logging_initialized[self.logger_name] = True
        return logger

    def configure_sandbox_testing_logger(self):
        import colorlog
        from colorlog import ColoredFormatter

        if DiffgramLogger.logging_initialized.get(self.logger_name):
            return colorlog.getLogger(self.logger_name)

        # Add Stream handle to print logs in console.

        handler = colorlog.StreamHandler()
        formatter = ColoredFormatter(
            "%(log_color)s[%(asctime)s] %(levelname)s %(reset)s%(blue)s%(module)s.py Line %(lineno)d: %(reset)s%(white)s%(message)s",
            datefmt = None,
            reset = True,
            log_colors = {
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
            secondary_log_colors = {},
            style = '%'
        )

        handler.setFormatter(formatter)
        logger = colorlog.getLogger(self.logger_name)
        logger.setLevel(settings.SANDBOX_LOGGER_TYPE)
        logger.addHandler(handler)
        if self.output_test_messages is True:
            logger.debug('Logger color configurations success.')
            logger.info('Logger color configurations success.')
            logger.warning('Logger color configurations success.')
            logger.error('Logger color configurations success.')
            logger.critical('Logger color configurations success.')

        DiffgramLogger.logging_initialized[self.logger_name] = True
        return logger

    def configure_default_logger(self):

        fmt_str = '[%(asctime)s] %(levelname)s %(module)s.py @ line %(lineno)d: %(message)s'
        logging.basicConfig(level = logging.DEBUG, format = fmt_str)
        logger = logging.getLogger(self.logger_name)
        logger.info('Logger setup success.')
        DiffgramLogger.logging_initialized[self.logger_name] = True
        return logger
