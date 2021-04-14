# OPENCORE - ADD
from abc import ABC, abstractmethod


def with_connection(f):
    """
        This decorator checks if the connections object is available to avoid function calls
        with no connection.
    :param f:
    :return:
    """
    def wrapper(*args):
        if args[0].connection_client is None:
            raise ConnectionError('Please call connect() before starting data fetch.')
        return f(*args)

    return wrapper


class Connector(ABC):

    def __init__(self, auth_data, config_data):
        self.auth_data = auth_data
        self.config_data = config_data
        self.connection_client = None

    @abstractmethod
    def connect(self):
        """
            This should be the first method called to connect to the source.
            All implementations should return a ConnectionError exception in case
            connection is unsuccessful.
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def get_meta_data(self):
        """
            This method should bring a dict for all the metadata specific to the connector.
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def fetch_data(self, opts):
        """
            This function fetches an object from the data source an returns the
            the actual file.
        :param opts: Options object for the specific implementation
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def put_data(self, opts):
        """
            This function puts an object from diffgram to the source
        :param opts: Options object for the specific implementation
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def test_connection(self):
        """
            This function checks if there is a succseful connecction to the source
        :return: True/False
        """
        raise NotImplementedError

