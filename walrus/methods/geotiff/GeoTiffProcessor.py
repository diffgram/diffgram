import json
from shared.database.input import Input
from sqlalchemy.orm import Session
from shared.data_tools_core import Data_tools
from shared.settings import settings
from shared.database.source_control.file import File
from shared.database.point_cloud.point_cloud import PointCloud

from shared.shared_logger import get_shared_logger

logger = get_shared_logger()


class GeoTiffProcessor:
    """
        This class handles the creation of all the files and relationships
        to support geo annotation.
    """

    def __init__(self, session: Session, input: Input, log: dict):
        self.session = session
        self.input = input
        self.log = log
        self.data_tools = Data_tools().data_tools

    def __create_geo_data_parent_file(self):
        return

    def __create_geo_layer_child_file(self):
        return


    def process_geotiff_data(self):
        """
            This function will validate the tiff file is a valid
            Cloud Optimized Geotiff file for usage in geo annotation.
        :return: (Boolean, log) if valid COG, False otherwise. Log describe any of the errors.
        """


        return True, self.log

    def try_to_commit(self):
        try:
            self.session.commit()
        except:
            self.session.rollback()
            raise
