import json
from shared.database.input import Input
from sqlalchemy.orm import Session

from methods.sensor_fusion.pcd_file_builder import PCDFileBuilder

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
        self.__load_3d_data(sensor_fusion_spec)

        return True, self.log
