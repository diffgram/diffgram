import json
from pypcd import pypcd
import numpy

class PCDFileBuilder:
    """
       Handles creation of PCD files from list of points data
    """

    def __init__(self, point_list):
        self.point_list = point_list

    def generate_pcd_file(self, save_path):
        pcd_data = []
        for row in self.point_list:
            pcd_data.append([
                row['x'],
                row['y'],
                row['z'],
                row['intensity'] if row['intensity'] else 1.0,
            ])
        arr = numpy.array(pcd_data, dtype = numpy.float32)
        new_cloud = pypcd.make_xyz_rgb_point_cloud(arr)
        new_cloud.save(save_path)
