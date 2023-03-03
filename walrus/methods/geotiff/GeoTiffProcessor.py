import os
import shutil
from datetime import datetime
from shared.database.input import Input
from sqlalchemy.orm import Session
from shared.data_tools_core import Data_tools
from shared.settings import settings
from shared.database.source_control.file import File
from shared.database.point_cloud.point_cloud import PointCloud
from shared.database.geospatial.geo_asset import GeoAsset
from osgeo import gdal
from shared.regular.regular_log import log_has_error
from osgeo_utils.samples.validate_cloud_optimized_geotiff import validate
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

    def __validate_COG_tiff(self):
        filename = self.input.temp_dir_path_and_filename
        warnings, errors, details = validate(ds = filename, check_tiled = None, full_check = False)
        if warnings:
            logger.warning('The following warnings were found:')
            # for warning in warnings:
            #     logger.warning(' - ' + warning)
        if errors:
            logger.error('%s is NOT a valid cloud optimized GeoTIFF.' % filename)
            logger.error('The following errors were found:')
            # i = 0
            # self.log['error']['COG'] = 'Invalid COG Tiff File:'
            # for error in errors:
            #     self.log['error'][i] = error
            #     logger.error(error)
            #     i += 1

            return False, self.log
        else:
            print('%s is a valid cloud optimized GeoTIFF' % filename)

        if not errors:
            headers_size = min(details['data_offsets'][k] for k in details['data_offsets'])
            if headers_size == 0:
                headers_size = gdal.VSIStatL(filename).size
            print('\nThe size of all IFD headers is %d bytes' % headers_size)
        return True, self.log

    def __create_geo_data_parent_file(self) -> File:
        file = File.new(
            session = self.session,
            working_dir_id = self.input.directory_id,
            file_type = "geospatial",
            original_filename = self.input.original_filename,
            project_id = self.input.project_id,
            input_id = self.input.id,
            file_metadata = self.input.file_metadata,
            ordinal = self.input.ordinal
        )
        self.input.file_id = file.id
        return file

    def __reproject_tiff_file(self, path_to_file: str) -> str:
        timestamp = datetime.timestamp(datetime.now())
        temp_foleder_name = f"temp_geo_{timestamp}"

        os.mkdir(temp_foleder_name)

        filename = f"{temp_foleder_name}/{self.input.original_filename}"

        input_raster = gdal.Open(path_to_file)
        gdal.Warp(filename, input_raster, dstSRS = 'EPSG:3857')

        return {
            "filename": filename,
            "folder": temp_foleder_name
        }

    def __covert_to_cog(self, path_to_file: str) -> str:
        timestamp = datetime.timestamp(datetime.now())
        temp_foleder_name = f"temp_cog_{timestamp}"

        os.mkdir(temp_foleder_name)

        filename = f"{temp_foleder_name}/{self.input.original_filename}"

        input_raster = gdal.Open(path_to_file)
        gdal.Translate(
            destName = filename,
            srcDS = input_raster,
            options = '-of COG -co COMPRESS=LZW'
        )

        return {
            "filename": filename,
            "folder": temp_foleder_name
        }

    def __cleanup_temp_file(self, folder_name: str) -> None:
        shutil.rmtree(folder_name)

    def __upload_tiff_and_attach_to_asset(self, geo_asset: GeoAsset):
        """
            Uploads the tiff file in the given path to cloud storage and
            geotiffobject
        :return:
        """
        final_file_path = None
        path_to_cog_file = None

        path_to_file_with_proper_projection = self.__reproject_tiff_file(self.input.temp_dir_path_and_filename)

        valid = self.__validate_COG_tiff()

        if not valid:
            path_to_cog_file = self.__covert_to_cog(path_to_file_with_proper_projection["filename"])
            final_file_path = path_to_cog_file['filename']
        else:
            final_file_path = path_to_file_with_proper_projection['filename']

        blob_path = f"{settings.PROJECT_GEOSPATIAL_FILES_BASE_DIR}{str(self.input.project_id)}/assets/{str(geo_asset.id)}"
        self.data_tools.upload_to_cloud_storage(temp_local_path = final_file_path,
                                                blob_path = blob_path,
                                                content_type = 'image/tiff')
        geo_asset.url_signed_blob_path = blob_path

        self.__cleanup_temp_file(path_to_file_with_proper_projection["folder"])

        if path_to_cog_file:
            self.__cleanup_temp_file(path_to_cog_file["folder"])

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
