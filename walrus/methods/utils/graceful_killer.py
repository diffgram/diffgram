import signal
import time
import sys
from walrus.methods.regular.regular_api import logger
from shared.helpers.sessionMaker import session_scope


class GracefulKiller:
    kill_now = False
    killing_gracefully = False
    # To reason this do: SLEEP_TIME x MAX_CHECKS
    # For default case we will wait for the walrus to finish processing for 1 hours 55mins max.
    MAX_CHECKS = 12 * 55 * 2  # 1 hour 55 minutes max wait time
    SLEEP_TIME = 5

    def __init__(self, processing_input_manager):
        self.processing_input_manager = processing_input_manager
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        logger.info('Listening for SIGTERM events for graceful shutdown')

    def exit_process(self):
        sys.exit(0)

    def set_inputs_with_error_status(self, input_list):
        with session_scope() as session:
            for input in input_list:
                if not input.id and input.media_type == 'frame':
                    p_media = process_media.Process_Media(input = input, session = session)
                    p_media.proprogate_frame_instance_update_errors_to_parent()
                else:
                    input.status = "failed"
                    input.status_text = "Error processing [Graceful Kill Max Time]. Please retry"
                    session.add(input)

    def exit_gracefully(self, *args):
        """
            Checks for inputs being processed by the service before
            killing
        :param args:
        :return:
        """
        import walrus.methods.input.process_media as process_media

        if self.killing_gracefully:
            return

        self.killing_gracefully = True
        process_media.STOP_PROCESSING_DATA = True
        num_retries = 0

        logger.warning('Staring Graceful Shutdown...')
        while num_retries < self.MAX_CHECKS:
            # Check if there are still inputs processing
            if process_media.VIDEO_QUEUE.qsize() == 0 \
                and process_media.FRAME_QUEUE.qsize() == 0 \
                and len(self.processing_input_manager.items) == 0:
                logger.warning('No More Inputs to Process shutting down...')
                self.kill_now = True
                break
            else:
                logger.warning('Pending Data to Process: ')
                logger.warning('VIDEO_QUEUE: {}'.format(process_media.VIDEO_QUEUE.qsize()))
                logger.warning('FRAME_QUEUE: {}'.format(process_media.FRAME_QUEUE.qsize()))
                logger.warning('PROCESSING_INPUTS: {}'.format(len(self.processing_input_manager.items)))

            time.sleep(self.SLEEP_TIME)

        if self.kill_now:
            self.exit_process()
        else:
            logger.error('Unable to shutdown.MAX RETRIES After {} seconds.'.format(self.MAX_CHECKS * self.SLEEP_TIME))
            self.set_inputs_with_error_status(process_media.processing_input_manager.items)


if __name__ == '__main__':
    killer = GracefulKiller()
