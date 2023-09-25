from methods.regular.regular_api import *
import threading
from shared.data_tools_core import Singleton
from shared.settings import settings
from queue import PriorityQueue
from shared.ingest.prioritized_item import PrioritizedItem
from methods.input.process_media import Process_Media
from methods.utils.graceful_killer import GracefulKiller
from shared.utils.memory_checks import check_and_wait_for_memory
from shared.utils.cpu_checks import check_and_wait_for_cpu
global Update_Input
from shared.database.input import Input
import traceback
import random


class ProcessMediaQueue():

    def __init__(self, name=None, threads_count=1, limit=None):
        self.queue = PriorityQueue()
        self.lock = threading.Lock()
        self.threads_count = threads_count
        self.name : str = name 
        self.limit : int = limit 


class RemoteQueue():

    def __init__(self, getter_function=None, cycle_time=2, name=None):
        self.getter_function: function = getter_function
        self.cycle_time: float = cycle_time
        self.name: str = name


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

        self.default_media_remote_queue = RemoteQueue(
            getter_function=self.get_remote_media_items,
            cycle_time=random.randint(2, 4),
            name="Default Media"
            )

        self.file_operations_remote_queue = RemoteQueue(
            getter_function=self.get_remote_items_file_operations,
            cycle_time=4,
            name="File Ops"
            )

        self.auto_retry_remote_queue = RemoteQueue(
            getter_function=self.refresh_stale_with_auto_retry,
            cycle_time=random.randint(120, 180),
            name="Auto Retry"
            )

        self.queue_list = [self.VIDEO_QUEUE, self.ALL_OTHER_QUEUE, self.COPY_QUEUE]

        self.remote_queues_list = [self.default_media_remote_queue, 
                                   self.file_operations_remote_queue, 
                                   self.auto_retry_remote_queue]

        self.STOP_PROCESSING_DATA = False
        self.PROCESSING_INPUT_LIST = []
        self.threads = []

        self.killer = GracefulKiller()

    

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
            self.process_media_queue_getter(process_media_queue)


    def process_media_queue_getter(self, process_media_queue):
        # docs/process_media_queue_getter

        process_media_queue.lock.acquire()
        if not process_media_queue.queue.empty():
            item = process_media_queue.queue.get()

            logger.info(f"[Local Item Starting] ID: {str(item.input_id)} Queue: {process_media_queue.name}")

            process_media_queue.lock.release()
            self.process_media_unit_of_work(item)
            process_media_queue.queue.task_done()

            logger.info(f"[Local Item Completed] ID: {str(item.input_id)} Queue: {process_media_queue.name}")

        else:
            process_media_queue.lock.release()
            time.sleep(0.1)




    def is_queue_over_limit(self, process_media_queue):
        if process_media_queue.limit is None:
            return False
        current_size = process_media_queue.queue.qsize()
        if current_size > process_media_queue.limit:
            logger.warn(f"Limit Queue: {process_media_queue.name} Size {str(current_size)} is above limit of {process_media_queue.limit}")
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

        self.start_all_local_queues()

        if settings.PROCESS_MEDIA_REMOTE_QUEUE_ON == True:    
            self.start_all_remote_queues()

        logger.info(f"[Process Media] Started.")


    def start_all_local_queues(self):
        for process_media_queue in self.queue_list:
            for i in range(process_media_queue.threads_count):
                t = threading.Thread(
                    target = self.process_media_queue_worker,
                    args = [process_media_queue]
                )
                t.daemon = True  # Allow hot reload to work
                t.start()
                self.threads.append(t)


    def start_all_remote_queues(self):

        for remote_queue in self.remote_queues_list:
            t = threading.Thread(
                target = self.start_remote_queue,
                args = [remote_queue]
            )
            t.daemon = True  # Allow hot reload to work
            t.start()


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


    def start_remote_queue(self, remote_queue: RemoteQueue):

        while True:

            if self.STOP_PROCESSING_DATA:
                logger.warning('Rejected Item: processing, data stopped. Waiting for termination...')
                break

            self.remote_queue_one_cycle(remote_queue)


    def check_and_wait_hardware_resources(self):
        check_and_wait_for_memory(memory_limit_float = 85.0)
        check_and_wait_for_cpu(limit = 80.0)


    def check_if_any_queue_is_over(self):
        for process_media_queue in self.queue_list:
            limit = self.is_queue_over_limit(process_media_queue)
            if limit is True:
                return True
            
        logger.info(f"[Limiter] All Local Queues OK")
        return False


    def remote_queue_one_cycle(self, remote_queue: RemoteQueue):

        time.sleep(remote_queue.cycle_time)

        self.check_and_wait_hardware_resources()

        limit = self.check_if_any_queue_is_over()
        if limit is True:
            return               

        logger.info(f"[[{remote_queue.name}] Heartbeat] V: {settings.DIFFGRAM_VERSION_TAG} T: {threading.get_ident()}")
        try:
            remote_queue.getter_function()
        except Exception as exception:
            logger.error(f"[Remote Queue [{remote_queue.name}] Getter Failed with:] {str(exception)}")
            logger.error(traceback.format_exc())


    def refresh_stale_with_auto_retry(self):
        from methods.input.input_update import Update_Input
        with sessionMaker.session_scope_threaded() as session:
            try:
                update_input = Update_Input(session = session).automatic_retry()
            except Exception as exception:
                logger.error(f"{str(exception)}")


    def get_remote_input(self, session, limit=1):
        input = session.query(Input).with_for_update(skip_locked = True).filter(
                Input.processing_deferred == True,
                Input.archived == False,
                Input.status != 'success',
                or_(Input.mode == None, Input.mode != 'copy_file')
            ).limit(limit).all()
        return input


    def get_remote_input_file_operations(self, session):
        input = session.query(Input).with_for_update(skip_locked = True).filter(
                Input.processing_deferred == True,
                Input.archived == False,
                Input.status != 'success',
                Input.mode == 'copy_file'
            ).limit(10).all()
        return input


    def route_all_items(self, item_list):
        for item in item_list:
            self.router(item)


    def get_remote_media_items(self):

        item_list = []

        with sessionMaker.session_scope_threaded() as session:

            input_list = self.get_remote_input(session, limit=2)

            if input_list is None: return

            for input in input_list:
                session.add(input)
                input.processing_deferred = False
                input.status = 'local_processing_queue'
                input.status_text = f'Version: {settings.DIFFGRAM_VERSION_TAG}'

                item = PrioritizedItem(
                    priority = 100,  # 100 is current default priority
                    input_id = input.id)
        
                item_list.append(item)

        # Note we closed the session before we route the item
        # This prevents some timing issues since we get a lock on the input
        self.route_all_items(item_list)


    def get_remote_items_file_operations(self):

        item_list = []

        with sessionMaker.session_scope_threaded() as session:

            input_list = self.get_remote_input_file_operations(session)

            logger.debug(f'input_list {input_list}')
            if input_list is None: return

            for input in input_list:
                session.add(input)
                input.processing_deferred = False
                input.status = 'local_processing_queue'

                item = PrioritizedItem(
                    priority = 100,  # 100 is current default priority
                    input_id = input.id,
                    mode = input.mode)  # Note mode supplied here to route to file ops queue

                item_list.append(item)

        self.route_all_items(item_list)




