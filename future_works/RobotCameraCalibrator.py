import numpy as np
import cv2
from scipy.optimize import least_squares

class RobotCameraCalibrator:

    def __init__(self):
        self.robot_poses = []  # Store robot's poses [(x1, y1, z1, roll1, pitch1, yaw1), ...]
        self.camera_poses = []  # Store camera's poses [(rvec1, tvec1), ...]
        
    def add_robot_pose(self, x, y, z, roll, pitch, yaw):
        self.robot_poses.append((x, y, z, roll, pitch, yaw))

    def add_camera_pose(self, rvec, tvec):
        self.camera_poses.append((rvec, tvec))

    def calculate_transformation(self):
        if len(self.robot_poses) != len(self.camera_poses):
            print("The number of robot poses must be equal to the number of camera poses.")
            return None

        initial_guess = np.zeros(6)  # Initial guess for [tx, ty, tz, rx, ry, rz]

        res = least_squares(self.error_function, initial_guess)

        return self.vector_to_transformation_matrix(res.x)

    def error_function(self, x):
        transformation_matrix = self.vector_to_transformation_matrix(x)
        errors = []

        for robot_pose, camera_pose in zip(self.robot_poses, self.camera_poses):
            robot_point = np.array([robot_pose[0], robot_pose[1], robot_pose[2], 1])
            camera_point = np.array(camera_pose)  # Assume camera_pose is (x, y, z)
            
            transformed_robot_point = transformation_matrix.dot(robot_point)
            
            error = np.linalg.norm(transformed_robot_point - camera_point)
            errors.append(error)

        return np.array(errors)

    def vector_to_transformation_matrix(self, x):
        tx, ty, tz, rx, ry, rz = x
        rot_matrix = cv2.Rodrigues(np.array([rx, ry, rz]))[0]
        trans_matrix = np.array([[tx], [ty], [tz]])
        
        transformation_matrix = np.hstack([rot_matrix, trans_matrix])
        transformation_matrix = np.vstack([transformation_matrix, [0, 0, 0, 1]])
        
        return transformation_matrix
