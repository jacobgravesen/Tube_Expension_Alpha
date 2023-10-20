import numpy as np
import pandas as pd
from future_works.RobotCameraCalibrator import RobotCameraCalibrator

class CameraToRobotBaseTransformer:
    def __init__(self, camera_to_robot_csv_file):
        # Load transformation parameters from CSV file
        self.params = pd.read_csv(camera_to_robot_csv_file)
        self.calibrator = RobotCameraCalibrator()

    def transform(self, camera_coords):
        # Get transformation matrix from calibrator
        transformation_matrix = self.calibrator.calculate_transformation()

        # Convert camera coordinates to homogeneous coordinates
        camera_coords_homogeneous = np.append(camera_coords, 1)

        # Apply transformation
        robot_coords_homogeneous = np.dot(transformation_matrix, camera_coords_homogeneous)

        # Convert back to non-homogeneous coordinates
        robot_coords = robot_coords_homogeneous[:3] / robot_coords_homogeneous[3]

        return robot_coords