import numpy as np

def load_transformation_matrix(filename):
    # Load the parameters
    parameters = np.genfromtxt(filename, delimiter=',', skip_header=1)
    tx, ty, tz, rx, ry, rz = parameters

    # Convert rotation parameters from degrees to radians
    rx, ry, rz = np.radians([rx, ry, rz])

    # Create rotation matrix
    Rx = np.array([[1, 0, 0, 0], [0, np.cos(rx), -np.sin(rx), 0], [0, np.sin(rx), np.cos(rx), 0], [0, 0, 0, 1]])
    Ry = np.array([[np.cos(ry), 0, np.sin(ry), 0], [0, 1, 0, 0], [-np.sin(ry), 0, np.cos(ry), 0], [0, 0, 0, 1]])
    Rz = np.array([[np.cos(rz), -np.sin(rz), 0, 0], [np.sin(rz), np.cos(rz), 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    R = np.dot(Rz, np.dot(Ry, Rx))

    # Create translation matrix
    T = np.array([[1, 0, 0, tx], [0, 1, 0, ty], [0, 0, 1, tz], [0, 0, 0, 1]])

    # Combine rotation and translation into a single transformation matrix
    camera_to_robot_transformation_matrix = np.dot(T, R)

    return camera_to_robot_transformation_matrix

def camera_to_robot_coordinates(camera_coordinates):
    """Converts the coordinate frame of the camera, to one that the robot uses.
    Also converts cm to mm
    """
    x_camera, y_camera, z_camera = camera_coordinates
    x_robot = z_camera * 10
    y_robot = x_camera * 10
    z_robot = y_camera * 10
    
    return [x_robot, y_robot, z_robot]