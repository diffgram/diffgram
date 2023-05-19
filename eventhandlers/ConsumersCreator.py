import pika
from EventsConsumer import EventsConsumer
from ActionConsumer import ActionsConsumer
from JobsConsumer import JobsConsumer
from SchedulerConsumer import SchedulerConsumer
from shared.settings import settings
from shared.shared_logger import get_shared_logger
from pika.channel import Channel
import ssl

logger = get_shared_logger()


class ConsumerCreator:
    connection: pika.SelectConnection
    channel: Channel or None
    events_consumer: EventsConsumer
    jobs_consumer: JobsConsumer
    actions_consumer: ActionsConsumer
    scheduler_consumer: SchedulerConsumer
    stopping: bool

    def __init__(self):
        self.channel = None
        self.stopping = False
        self.create_consumers()

    def on_channel_open(self, channel):
        logger.info('Connection opened')
        self.channel = channel
        self.setup_consumers()

    def on_channel_closed(self, channel, reason):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.
        :param pika.channel.Channel channel: The closed channel
        :param Exception reason: why the channel was closed
        """
        logger.warning('Channel %i was closed: %s', channel, reason)
        self.channel = None
        if not self.stopping:
            self.connection.close()

    def add_on_channel_close_callback(self):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.
        """
        logger.info('Adding channel close callback')
        self.channel.add_on_close_callback(self.on_channel_closed)

    def setup_consumers(self):
        self.events_consumer = EventsConsumer(channel = self.channel, connection = self.connection)
        self.actions_consumer = ActionsConsumer(channel = self.channel, connection = self.connection)
        self.jobs_consumer = JobsConsumer(channel = self.channel, connection = self.connection)
        self.scheduler_consumer = SchedulerConsumer(channel = self.channel, connection = self.connection)

    def open_channel(self):

        self.connection.channel(on_open_callback = self.on_channel_open)

    def on_connection_open(self, _unused_connection):

        self.open_channel()

    def on_connection_open_error(self, _unused_connection, err):
        logger.error('Connection open failed, reopening in 5 seconds: %s', err)
        self.connection.ioloop.call_later(5, self._connection.ioloop.stop)

    def stop(self):
        """Stop  by closing the channel and connection. We
        set a flag here so that we stop scheduling new messages to be
        published. The IOLoop is started because this method is
        invoked by the Try/Catch below when KeyboardInterrupt is caught.
        Starting the IOLoop again will allow the publisher to cleanly
        disconnect from RabbitMQ.
        """
        logger.info('Stopping')
        self.stopping = True
        self.close_channel()
        self.close_connection()

    def close_channel(self):
        """Invoke this command to close the channel with RabbitMQ by sending
        the Channel.Close RPC command.
        """
        if self.channel is not None:
            logger.info('Closing the channel')
            self.channel.close()

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        if self.connection is not None:
            logger.info('Closing connection')
            self.connection.close()

    def on_connection_closed(self, _unused_connection, reason):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.
        :param pika.connection.Connection connection: The closed connection obj
        :param Exception reason: exception representing reason for loss of
            connection.
        """
        self.channel = None
        if self.stopping:
            self.connection.ioloop.stop()
        else:
            logger.warning('Connection closed, reopening in 5 seconds: %s',
                           reason)
            self.connection.ioloop.call_later(5, self.connection.ioloop.stop)

    def create_consumers(self):
        ssl_options = None
        if settings.RABBITMQ_USE_SSL:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            ssl_context.set_ciphers('ECDHE+AESGCM:!ECDSA')
            ssl_options = pika.SSLOptions(context = ssl_context)
        self.connection = pika.SelectConnection(
            pika.ConnectionParameters(host = settings.RABBITMQ_HOST,
                                      port = settings.RABBITMQ_PORT,
                                      ssl_options = ssl_options,
                                      heartbeat = 10,
                                      credentials = pika.PlainCredentials(settings.RABBITMQ_DEFAULT_USER,
                                                                          settings.RABBITMQ_DEFAULT_PASS)),
            on_open_callback = self.on_connection_open,
            on_open_error_callback = self.on_connection_open_error,
            on_close_callback = self.on_connection_closed
        )

    def run(self):
        """Run the example code by connecting and then starting the IOLoop.
        """
        while not self.stopping:
            self.connection = None
            self.deliveries = {}
            self.acked = 0
            self.nacked = 0
            self.message_number = 0

            try:
                self.create_consumers()
                self.connection.ioloop.start()
            except KeyboardInterrupt:
                self.stop()
                if (self.connection is not None and
                    not self.connection.is_closed):
                    self.connection.ioloop.start()

        logger.info('Stopped')

    def stop_processing(self):
        self.channel.stop_consuming()

    def start_processing(self):
        self.channel.start_consuming()
