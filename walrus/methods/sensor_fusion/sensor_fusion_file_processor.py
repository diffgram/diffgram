import json
from shared.database.input import Input
from sqlalchemy.orm import Session
from shared.data_tools_core import Data_tools
from methods.sensor_fusion.pcd_file_builder import PCDFileBuilder
from shared.settings import settings
from shared.database.source_control.file import File
from shared.database.point_cloud.point_cloud import PointCloud


class SensorFusionFileProcessor:
    """
        This class handles the creation of all the files and relationships
        to support sensor fusion annotation.
        This includes, generating point clouds, binding cameras and any
        other data related to the scene to annotate.
    """

    def __init__(self, session: Session, input: Input, log: dict):
        self.session = session
        self.input = input
        self.log = log
        self.data_tools = Data_tools().data_tools

    def __load_sensor_fusion_json(self) -> dict:
        if self.input.temp_dir_path_and_filename is None:
            self.log['error']['json_file_path'] = 'temp_dir_path_and_filename is None.Needs to exists for loading JSON.'

        with open(self.input.temp_dir_path_and_filename) as json_data:
            sensor_fusion_spec = json.load(json_data)

            return sensor_fusion_spec

    def __load_3d_data(self, sensor_fusion_spec) -> str:
        if sensor_fusion_spec.get('point_list') is None:
            return

        pcd_file_builder = PCDFileBuilder(point_list = sensor_fusion_spec.get('point_list'))

        pcd_save_path = self.input.temp_dir_path_and_filename.split('.json')[0]
        pcd_save_path = pcd_save_path + '.pcd'
        pcd_file_builder.generate_pcd_file(save_path = pcd_save_path)
        return pcd_save_path

    def __upload_pcd(self, file_3d, pcd_file_path):
        """
            Uploads the pcd file in the given path to cloud storage and
            creates point cloud object
        :return:
        """
        blob_path = '{}{}/{}'.format(settings.PROJECT_PCD_FILES_BASE_DIR, str(self.input.project_id), str(file_3d.id))
        self.data_tools.upload_to_cloud_storage(temp_local_path = pcd_file_path, blob_path = blob_path)

        point_cloud = PointCloud.new(
            session = self.session,
            original_filename = pcd_file_path,
            url_signed_blob_path = blob_path
        )
        point_cloud.regenerate_url(session = self.session)
        file_3d.point_cloud_id = point_cloud.id
        return point_cloud

    def __create_sensor_fusion_file(self):
        """
            Creates the parent sensor fusion file
        :return:
        """
        file = File.new(
            session = self.session,
            working_dir_id = self.input.directory_id,
            file_type = "sensor_fusion",
            original_filename = self.input.original_filename,
            project_id = self.input.project_id,
            input_id = self.input.id,
            file_metadata = self.input.file_metadata
        )

        return file

    def __add_file_to_input(self, file):
        self.input.file_id = file.id

    def __create_3d_point_cloud_file(self, parent_sensor_fusion_file):
        """
            Creates the 3D point cloud file
        :param blob_path:
        :param parent_sensor_fusion_file:
        :return:
        """
        filename = self.input.original_filename.split('_sf.json')[0]
        file = File.new(
            session = self.session,
            working_dir_id = self.input.directory_id,
            file_type = "point_cloud_3d",
            parent_id = parent_sensor_fusion_file.id,
            original_filename = filename,
            project_id = self.input.project_id,
            input_id = self.input.id,
            file_metadata = self.input.file_metadata
        )
        return file

    def process_sensor_fusion_file_contents(self):
        """
            This function will load the sensor fusion file specification
            JSON into memory and determine the actions that need to be performed
            to have all the data correctly binded in a single annotation scene.
            This includes:
                - Generating PCD files from point cloud data
                - (Todo) Attaching Cameras
                - (Todo) Attaching Radar Data
                - (Todo) Binding video files with frames
        :return:
        """
        sensor_fusion_spec = self.__load_sensor_fusion_json()

        # Load 3D Data
        pcd_path = self.__load_3d_data(sensor_fusion_spec)

        sensor_fusion_file = self.__create_sensor_fusion_file()

        file_3d = self.__create_3d_point_cloud_file(sensor_fusion_file)

        point_cloud_obj = self.__upload_pcd(file_3d, pcd_path)

        self.__add_file_to_input(sensor_fusion_file)

        return True, self.log
