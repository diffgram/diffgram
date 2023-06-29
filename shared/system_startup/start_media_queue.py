try:
    from walrus.methods.input.process_media_queue_manager import ProcessMediaQueueManager
except:
    from methods.input.process_media_queue_manager import ProcessMediaQueueManager

process_media_queue_manager = ProcessMediaQueueManager()
process_media_queue_manager.start()