import math
import numpy as np
import csv

class AngleCalculator:
    def __init__(self, intrinsic_parameters_path):
        with open(intrinsic_parameters_path, newline='') as file:
            reader = csv.reader(file)
            data = list(reader)
            self.camera_matrix = np.array(data[1:4], dtype=np.float64)
            self.distortion_coefficients = np.array(data[5], dtype=np.float64)

    def calculate_angle(self, box, depth_frame):
        # Get the depth at the top left and top right corners of the bounding box
        depth_x1 = self.get_depth(int(box[0]), int(box[1]), depth_frame) 
        depth_x2 = self.get_depth(int(box[2]), int(box[1]), depth_frame) 

        # Convert x1 and x2 from pixel coordinates to camera coordinates
        x1_cam = (box[0] - self.camera_matrix[0, 2]) * depth_x1 / self.camera_matrix[0, 0]
        x2_cam = (box[2] - self.camera_matrix[0, 2]) * depth_x2 / self.camera_matrix[0, 0]

        # Calculate the real-world distance between x1 and x2
        distance = x2_cam - x1_cam

        # Calculate the depth difference
        depth_diff = depth_x2 - depth_x1

        # Calculate the angle in radians
        angle_rad = math.atan2(depth_diff, distance)

        # Convert the angle to degrees
        angle_deg = math.degrees(angle_rad)

        return angle_deg

    def get_depth(self, x, y, depth_frame):
        """
        Get the depth value of the specified pixel in millimeters
        """
        depth_in_meters = depth_frame.get_distance(x, y)
        depth_in_millimeters = depth_in_meters * 1000
        return depth_in_millimeters