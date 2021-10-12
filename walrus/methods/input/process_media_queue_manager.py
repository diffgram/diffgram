import threading
from shared.data_tools_core import Singleton
from shared.settings import settings
from queue import PriorityQueue
from methods.input.process_media import process_media_queue_worker, processing_input_manager, start_queue_check_loop
from methods.utils.graceful_killer import GracefulKiller


class ProcessMediaQueueManager(metaclass = Singleton):

    def __init__(self):
        self.VIDEO_QUEUE = PriorityQueue()
        self.FRAME_QUEUE = PriorityQueue()
        self.frame_queue_lock = threading.Lock()
        self.video_queue_lock = threading.Lock()
        self.STOP_PROCESSING_DATA = False
        self.threads = []

        self.video_threads = settings.PROCESS_MEDIA_NUM_VIDEO_THREADS
        self.frame_threads = settings.PROCESS_MEDIA_NUM_FRAME_THREADS
        self.killer = GracefulKiller(processing_input_manager)

    def stop_processing(self):
        self.STOP_PROCESSING_DATA = True

    def start_process_media_threads(self):
        # Kick off worker threads for global queue

        for i in range(self.video_threads):
            t = threading.Thread(
                target = process_media_queue_worker,
                args = (
                    self.VIDEO_QUEUE, 'video', processing_input_manager, self.frame_queue_lock, self.video_queue_lock)
            )
            t.daemon = True  # Allow hot reload to work
            t.start()
            self.threads.append(t)

        for i in range(self.frame_threads):
            t = threading.Thread(
                target = process_media_queue_worker,
                args = (
                    self.FRAME_QUEUE, 'frame', processing_input_manager, self.frame_queue_lock, self.video_queue_lock)
            )
            t.daemon = True  # Allow hot reload to work
            t.start()
            self.threads.append(t)

        t = threading.Timer(3, start_queue_check_loop, [self.VIDEO_QUEUE, self.FRAME_QUEUE])
        t.daemon = True  # Allow hot reload to work
        t.start()


process_media_queue_manager = ProcessMediaQueueManager()
