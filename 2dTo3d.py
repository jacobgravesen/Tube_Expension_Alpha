import numpy as np

class CoordinateTransformer:
    def __init__(self, calibration_parameters):
        self.calibration_parameters = calibration_parameters

    def calculate_real_world_coordinates(self, pixel_coordinates, depth_value):
        # Extract the focal length, optical center, and distortion coefficients from the calibration parameters
        f_x = self.calibration_parameters['focal_length_x']
        f_y = self.calibration_parameters['focal_length_y']
        c_x = self.calibration_parameters['optical_center_x']
        c_y = self.calibration_parameters['optical_center_y']
        k1, k2, p1, p2, k3 = self.calibration_parameters['distortion_coefficients']

        # Subtract the optical center from the pixel coordinates
        x_shifted = pixel_coordinates[0] - c_x
        y_shifted = pixel_coordinates[1] - c_y

        # Correct for lens distortion
        r_squared = x_shifted**2 + y_shifted**2
        x_corrected = x_shifted * (1 + k1*r_squared + k2*r_squared**2 + k3*r_squared**3) + 2*p1*x_shifted*y_shifted + p2*(r_squared + 2*x_shifted**2)
        y_corrected = y_shifted * (1 + k1*r_squared + k2*r_squared**2 + k3*r_squared**3) + p1*(r_squared + 2*y_shifted**2) + 2*p2*x_shifted*y_shifted

        # Multiply by the depth value and divide by the focal length to get real-world coordinates
        X = x_corrected * depth_value / f_x
        Y = y_corrected * depth_value / f_y

        return X, Y

    def transform_to_robot_frame(self, camera_coordinates):
        # Extract the rotation matrix and translation vector from the calibration parameters
        R = np.array(self.calibration_parameters['rotation_matrix'])
        T = np.array(self.calibration_parameters['translation_vector'])

        # Convert the camera coordinates to homogeneous coordinates
        camera_coordinates_homogeneous = np.append(camera_coordinates, 1)

        # Apply the rotation and translation
        robot_coordinates_homogeneous = R @ camera_coordinates_homogeneous + T

        # Convert back to non-homogeneous coordinates
        robot_coordinates = robot_coordinates_homogeneous[:3] / robot_coordinates_homogeneous[3]

        return robot_coordinates