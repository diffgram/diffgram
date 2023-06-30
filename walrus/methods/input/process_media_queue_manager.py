from methods.regular.regular_api import *
import threading
from shared.data_tools_core import Singleton
from shared.settings import settings
from queue import PriorityQueue
from shared.ingest.prioritized_item import PrioritizedItem
from methods.input.process_media import Process_Media
from methods.utils.graceful_killer import GracefulKiller
from shared.utils.memory_checks import check_and_wait_for_memory
global Update_Input
from shared.database.input import Input
import traceback


class ProcessMediaQueue():

    def __init__(self, name=None, threads_count=1, limit=None):
        self.queue = PriorityQueue()
        self.lock = threading.Lock()
        self.threads_count = threads_count
        self.name : str = name 
        self.limit : int = limit 


class ProcessMediaQueueManager(metaclass = Singleton):

    def __init__(self):

        self.VIDEO_QUEUE = ProcessMediaQueue(
            name = "video",
            threads_count = settings.PROCESS_MEDIA_NUM_VIDEO_THREADS,
            limit = 1
            )

        self.ALL_OTHER_QUEUE = ProcessMediaQueue(
            name = "all_other",
            threads_count = settings.PROCESS_MEDIA_NUM_FRAME_THREADS,
            limit = 30
            )

        self.COPY_QUEUE = ProcessMediaQueue(
            name = "copy",
            threads_count = 3,
            limit = None
            )

        self.queue_list = [self.VIDEO_QUEUE, self.ALL_OTHER_QUEUE, self.COPY_QUEUE]

        self.STOP_PROCESSING_DATA = False
        self.PROCESSING_INPUT_LIST = []
        self.threads = []

        self.frame_threads = settings.PROCESS_MEDIA_NUM_FRAME_THREADS
        self.killer = GracefulKiller()

        self.remote_queue_sleep_time = 2
    

    def router(self, item : PrioritizedItem):
        logger.info(f"item.mode {item.mode}")
        if item.media_type and item.media_type == "video":
            self.VIDEO_QUEUE.queue.put(item)
        elif item.mode == 'copy_file':
            self.COPY_QUEUE.queue.put(item)
        else:
            self.ALL_OTHER_QUEUE.queue.put(item)
          
        logger.info(f"{str(item.input_id)} Added to queue.")


    def process_media_queue_worker(self, process_media_queue):
        while True:
            over_limit = self.is_queue_over_limit(process_media_queue)
            if over_limit is True:
                time.sleep(1)
                continue

            self.process_media_queue_getter(process_media_queue)


    def process_media_queue_getter(self, process_media_queue):
        # docs/process_media_queue_getter

        process_media_queue.lock.acquire()
        if not process_media_queue.queue.empty():
            item = process_media_queue.queue.get()
            process_media_queue.lock.release()
            self.process_media_unit_of_work(item)
            process_media_queue.queue.task_done()
        else:
            process_media_queue.lock.release()
            time.sleep(0.1)


    def is_queue_over_limit(self, process_media_queue):
        if process_media_queue.limit is None:
            return False
        current_size = process_media_queue.queue.qsize()
        if current_size > process_media_queue.limit:
            logger.warn(f"Queue: {process_media_queue.name} Size {str(current_size)} is above limit of {process_media_queue.limit}")
            return True
        else:
            return False

    def add_item_to_processing_list(self, item: PrioritizedItem):
        self.PROCESSING_INPUT_LIST.append(item)

    def remove_item_from_processing_list(self, item: PrioritizedItem):
        self.PROCESSING_INPUT_LIST.remove(item)

    def stop_processing(self):
        self.STOP_PROCESSING_DATA = True

    def start(self):

        for process_media_queue in self.queue_list:
            for i in range(process_media_queue.threads_count):
                t = threading.Thread(
                    target = self.process_media_queue_worker,
                    args = [process_media_queue]
                )
                t.daemon = True  # Allow hot reload to work
                t.start()
                self.threads.append(t)

        t = threading.Timer(20, self.start_remote_queue_check)
        t.daemon = True  # Allow hot reload to work
        t.start()

        logger.info(f"[Process Media] Started.")


    def process_media_unit_of_work(self, item):

        with sessionMaker.session_scope_threaded() as session:

            process_media = Process_Media(
                session = session,
                input_id = item.input_id,
                input = item.input,
                item = item)

            self.add_item_to_processing_list(item)

            if settings.PROCESS_MEDIA_TRY_BLOCK_ON is True:
                try:
                    process_media.main_entry()

                except Exception as e:
                    logger.error(f"[Process Media] Main failed on {item.input_id}")
                    logger.error(str(e))
                    logger.error(traceback.format_exc())
            else:
                process_media.main_entry()
            
            self.remove_item_from_processing_list(item)


    def start_remote_queue_check(self):

        # /docs/remote-queue-start_queue_check_loop

        if settings.PROCESS_MEDIA_REMOTE_QUEUE_ON == False:
            return

        while True:
            if self.STOP_PROCESSING_DATA:
                logger.warning('Rejected Item: processing, data stopped. Waiting for termination...')
                break

            time.sleep(self.remote_queue_sleep_time)

            check_and_wait_for_memory(memory_limit_float = 85.0)

            for process_media_queue in self.queue_list:
                over_limit = self.is_queue_over_limit(process_media_queue)
                if over_limit is True:
                    continue               

            logger.info(f"[Media Queue Heartbeat] V: {settings.DIFFGRAM_VERSION_TAG}")
            try:
                self.get_remote_items()
            except Exception as exception:
                logger.error(f"[Remote Queue [Media] Getter Failed with:] {str(exception)}")
                logger.error(traceback.format_exc())

            try:
                self.get_remote_items_file_operations()
            except Exception as exception:
                logger.error(f"[Remote [File Ops] Getter Failed with:] {str(exception)}")
                logger.error(traceback.format_exc())


    def refresh_stale_with_auto_retry(self, session):
        from methods.input.input_update import Update_Input
        try:
            update_input = Update_Input(session = session).automatic_retry()
        except Exception as exception:
            logger.error(f"Couldn't find Update_Input {str(exception)}")


    def get_remote_input(self, session):
        input = session.query(Input).with_for_update(skip_locked = True).filter(
                Input.processing_deferred == True,
                Input.archived == False,
                Input.status != 'success',
                Input.mode != 'copy_file'
            ).first()
        return input


    def get_remote_input_file_operations(self, session):
        input = session.query(Input).with_for_update(skip_locked = True).filter(
                Input.processing_deferred == True,
                Input.archived == False,
                Input.status != 'success',
                Input.mode == 'copy_file'
            ).first()
        return input


    def get_remote_items(self):

        from methods.input.input_update import Update_Input

        with sessionMaker.session_scope_threaded() as session:

            self.refresh_stale_with_auto_retry(session = session)

            input = self.get_remote_input(session)

            if input is None: return

            session.add(input)
            input.processing_deferred = False

            item = PrioritizedItem(
                priority = 100,  # 100 is current default priority
                input_id = input.id)

            self.router(item)


    def get_remote_items_file_operations(self):

        with sessionMaker.session_scope_threaded() as session:

            input = self.get_remote_input_file_operations(session)

            if input is None: return

            session.add(input)
            input.processing_deferred = False

            item = PrioritizedItem(
                priority = 100,  # 100 is current default priority
                input_id = input.id,
                mode = input.mode)  # Note mode supplied here to route to file ops queue

            self.router(item)



