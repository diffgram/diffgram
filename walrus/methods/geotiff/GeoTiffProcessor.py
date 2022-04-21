import json
from shared.database.input import Input
from sqlalchemy.orm import Session
from shared.data_tools_core import Data_tools
from shared.settings import settings
from shared.database.source_control.file import File
from shared.database.point_cloud.point_cloud import PointCloud
from shared.database.geospatial.geo_asset import GeoAsset

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

    def __create_geo_data_parent_file(self) -> File:
        file = File.new(
            session = self.session,
            working_dir_id = self.input.directory_id,
            file_type = "geospatial",
            original_filename = self.input.original_filename,
            project_id = self.input.project_id,
            input_id = self.input.id,
            file_metadata = self.input.file_metadata
        )
        self.input.file_id = file.id
        return file

    def __upload_tiff_and_attach_to_asset(self, geo_asset: GeoAsset):
        """
            Uploads the pcd file in the given path to cloud storage and
            creates point cloud object
        :return:
        """
        blob_path = f"{settings.PROJECT_GEOSPATIAL_FILES_BASE_DIR}{str(self.input.project_id)}/assets/{str(geo_asset.id)}"
        self.data_tools.upload_to_cloud_storage(temp_local_path = self.input.temp_dir_path_and_filename,
                                                blob_path = blob_path)
        geo_asset.url_signed_blob_path = blob_path
        geo_asset.regenerate_url(session = self.session)

    def __create_geo_layer_child_file(self, parent_file: File) -> GeoAsset:
        geo_asset = GeoAsset.new(
            session = self.session,
            original_filename = self.input.original_filename,
            type = 'layer',
            file_id = parent_file.id,
            project_id = parent_file.project_id
        )
        return geo_asset

    def process_geotiff_data(self):
        """
            This function will validate the tiff file is a valid
            Cloud Optimized Geotiff file for usage in geo annotation.
        :return: (Boolean, log) if valid COG, False otherwise. Log describe any of the errors.
        """
        parent_file = self.__create_geo_data_parent_file()

        if self.input.type == 'from_geo_tiff':
            child_layer = self.__create_geo_layer_child_file(parent_file)
            self.__upload_tiff_and_attach_to_asset(geo_asset = child_layer)
            return True, self.log
        elif self.input.type == 'from_geo_tiff_json':
            raise NotImplementedError('from_geo_tiff_json is not supported yet.')
        else:
            raise Exception('Invalid Input type for geospatial processor.')

    def try_to_commit(self):
        try:
            self.session.commit()
        except:
            self.session.rollback()
            raise
