import time
import sys
import signal
from methods.regular.regular_api import logger
from shared.helpers.sessionMaker import session_scope
from shared.utils.singleton import Singleton
from signal import signal, SIGINT, SIGTERM, SIG_IGN
from shared.regular import regular_log


class GracefulKiller(metaclass = Singleton):
    kill_now = False
    killing_gracefully = False
    # To reason this do: SLEEP_TIME x MAX_CHECKS
    # For default case we will wait for the walrus to finish processing for 1 hours 55mins max.
    MAX_CHECKS = 12 * 55 * 2
    SLEEP_TIME = 5

    def __init__(self):
        signal(SIGINT, self.exit_gracefully)
        signal(SIGTERM, self.exit_gracefully)
        logger.info('Listening for SIGTERM events for graceful shutdown')

    def exit_process(self):
        logger.info('bye! :)')
        sys.exit(0)

    def set_inputs_with_error_status(self, item_list):
        from methods.input.process_media import Process_Media
        with session_scope() as session:
            for item in item_list:
                if item.input is not None and item.input.id is None and item.input.media_type in ['frame']:
                    p_media = Process_Media(input = item.input, session = session)
                    parent_input = p_media.get_parent_input_with_retry()
                    parent_input.status = "failed"
                    parent_input.status_text = "Error processing [Graceful Kill Max Time]. Please retry"
                    session.add(parent_input)
                elif item.input is not None and item.input.id is not None:
                    item.input.status = "failed"
                    item.input.status_text = "Error processing [Graceful Kill Max Time]. Please retry"
                    session.add(item.input)

    def exit_gracefully(self, *args):
        """
            Checks for inputs being processed by the service before
            killing
        :param args:
        :return:
        """
        from methods.input.process_media_queue_manager import process_media_queue_manager

        logger.info('Exiting gracefully...')
        if self.killing_gracefully:
            return

        self.killing_gracefully = True
        process_media_queue_manager.STOP_PROCESSING_DATA = True

        num_retries = 0

        logger.warning('Staring Graceful Shutdown...')
        while num_retries < self.MAX_CHECKS:
            # Check if there are still inputs processing
            if process_media_queue_manager.VIDEO_QUEUE.qsize() == 0 \
                and process_media_queue_manager.FRAME_QUEUE.qsize() == 0 \
                    and len(process_media_queue_manager.PROCESSING_INPUT_LIST) == 0:

                logger.warning('No More Inputs to Process shutting down...')
                self.kill_now = True
                break
            else:
                logger.warning('Pending Data to Process: ')
                logger.warning('VIDEO_QUEUE: {}'.format(process_media_queue_manager.VIDEO_QUEUE.qsize()))
                logger.warning('FRAME_QUEUE: {}'.format(process_media_queue_manager.FRAME_QUEUE.qsize()))
                logger.warning('PROCESSING_INPUTS: {}'.format(len(process_media_queue_manager.PROCESSING_INPUT_LIST)))

            time.sleep(self.SLEEP_TIME)
            num_retries += 1

        if self.kill_now:
            self.exit_process()
        else:
            logger.error('Unable to shutdown gracefully. MAX RETRIES After {} seconds.'.format(
                self.MAX_CHECKS * self.SLEEP_TIME))
            logger.error('VIDEO_QUEUE: {}'.format(process_media_queue_manager.VIDEO_QUEUE.qsize()))
            logger.error('FRAME_QUEUE: {}'.format(process_media_queue_manager.FRAME_QUEUE.qsize()))
            logger.error('PROCESSING_INPUTS: {}'.format(len(process_media_queue_manager.PROCESSING_INPUT_LIST)))
            self.set_inputs_with_error_status(process_media_queue_manager.PROCESSING_INPUT_LIST)
            # TODO: set failed inputs to failed status
            self.exit_process()
