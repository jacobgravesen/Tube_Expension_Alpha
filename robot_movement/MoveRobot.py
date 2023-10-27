from robolink import Robolink, Item
import numpy as np
from robodk.robomath import transl
from robodk.robomath import rotz, roty, rotx
import math
from robolink import Robolink, Item, ROBOTCOM_READY, RUNMODE_RUN_ROBOT
import csv
from utils.utils import load_transformation_matrix




class MoveRobot:
    def __init__(self, target_coords_handler, sim_robot_to_real_robot_angle_file):
        self.robodk = Robolink()
        self.station = self.robodk.Item('Station1')
        if not self.station.Valid():
            self.station = self.robodk.AddFile('Station1.rdk')
        self.robot = self.robodk.Item('UR5') 

        # Connect to the robot using default IP
        success = self.robot.Connect()  # Try to connect once
        # success = self.robot.ConnectSafe() # Try to connect multiple times
        status, status_msg = self.robot.ConnectedState()
        if status != ROBOTCOM_READY:
            # Stop if the connection did not succeed
            print(status_msg)
            raise Exception("Failed to connect: " + status_msg)

        # This will set to run the API programs on the robot and the simulator (online programming)
        self.robodk.setRunMode(RUNMODE_RUN_ROBOT)

        self.current_point = None
        self.target_coords_handler = target_coords_handler

        with open(sim_robot_to_real_robot_angle_file, 'r') as file:
            reader = csv.reader(file)
            self.rotation_angle = float(next(reader)[0])

        with open('vision/camera_to_robot.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header
            self.camera_to_robot_transformation = list(map(float, next(reader)))



    def rotate_point_around_base(self, point):
        # Convert the rotation angle to radians
        angle_rad = math.radians(self.rotation_angle)
        # Create the rotation matrix
        rotation_matrix = np.array([[math.cos(angle_rad), -math.sin(angle_rad), 0],
                                    [math.sin(angle_rad), math.cos(angle_rad), 0],
                                    [0, 0, 1]])
        # Apply the rotation to the point
        rotated_point = np.dot(rotation_matrix, point)
        return rotated_point

    
    def simple_move(self, point=[474.50, -109.30,608.95], orientation=[0, 90, 0], speed=30):
        # Set the robot speed
        self.robot.setSpeed(speed)
        # Convert the coordinates from your application's coordinate system to RoboDK's coordinate system
        x, y, z = np.array(point)

        # Print the original z value and tz
        print(f"Original z: {z}, tz: {self.camera_to_robot_transformation[2]}")

        # Apply the transformation
        tx, ty, tz, _, _, _ = self.camera_to_robot_transformation
        x += tx
        y += ty
        z += tz

        # Print the transformed z value
        print(f"Transformed z: {z}")

        # Define the orientation in radians
        roll, pitch, yaw = [math.radians(angle) for angle in orientation]
        roll += math.radians(35)

        # Create the pose matrix
        pose_matrix = transl(x, y, z) * rotx(roll) * roty(pitch) * rotz(yaw)
        print(pose_matrix)

        # Get all possible joint solutions for the given pose
        all_solutions = self.robot.SolveIK_All(pose_matrix) 

        # Iterate through each solution
        for new_robot_joints in all_solutions:
            # Retrieve flags as a list for each solution
            new_robot_config = self.robot.JointsConfig(new_robot_joints).list()

            # Check if the elbow is in an upward position and the wrist is in a non-flip position
            if new_robot_config[1] == 0:  # adjust this condition as needed
                print("Solution found for elbow Up!")
                # Move the robot to the pose
                self.robot.MoveL(new_robot_joints)
                break
        else:
            print("Warning! No solution with the elbow in an upward position found.")


    def move_robot_to_specific_point(self, point, min_height=10):
        # Check if the point has been set
        if point is not None:
            # Check if the height is above the minimum
            if point[1] >= min_height:
                # Convert the point from cm to mm
                point_mm = tuple(coordinate * 10 for coordinate in point)
                # Rearrange the coordinates
                transformed_point = (point_mm[2], point_mm[0], point_mm[1])
                # Apply the rotation
                rotated_point = self.rotate_point_around_base(transformed_point)
                # Print the coordinates
                print(f"Moving to point: {rotated_point}")
                # Move the robot to the rotated point
                self.simple_move(rotated_point)
            else:
                print(f'Warning! The target height {point[1]} is below the minimum height {min_height}.')
        else:
            print('Point not set')

    def move_to_all_required_points(self, min_height=20):
        # Get the initial number of points
        num_points = self.target_coords_handler.get_num_required_points()

        for _ in range(num_points):
            # Write the next point from required_points.csv to current_point.csv
            self.target_coords_handler.write_current_point_to_csv()

            # Get the current point from current_point.csv
            current_point = self.target_coords_handler.read_current_point_from_csv()

            if current_point is not None and len(current_point) >= 3:
                # Move the robot to the point'ø
                self.move_robot_to_specific_point(current_point, min_height)

                # Once the robot has reached the point, move the point to completed_points.csv
                self.target_coords_handler.move_completed_point()
            else:
                print('No more points in required_points.csv')
                break

    def move_to_first_required_point(self, min_height=8):
        # Write the first point from required_points.csv to current_point.csv
        self.target_coords_handler.write_current_point_to_csv()

        # Get the current point from current_point.csv
        current_point = self.target_coords_handler.read_current_point_from_csv()

        if current_point is not None and len(current_point) >= 3:
            # Move the robot to the point
            self.move_robot_to_specific_point(current_point, min_height)

            # Once the robot has reached the point, move the point to completed_points.csv
            self.target_coords_handler.move_completed_point()
        else:
            print('No more points in required_points.csv')

if __name__ == "__main__":
    # Create an instance of MoveRobot

    robot = MoveRobot()
    test_point = [609,63,47]
    #test_point = transform_xyz_to_yzx(test_point)
    robot.simple_move(test_point)

    """ THIS FUNCTION CHECKS FOR ELBOW UP POSITION BEFORE MOVING.
    def simple_move(self, point=[474.50, -109.30,608.95], orientation=[90,90,90], speed=5):
        # Set the robot speed
        self.robot.setSpeed(speed)

        # Convert the coordinates from your application's coordinate system to RoboDK's coordinate system
        x,y,z = np.array(point)

        # Define the orientation in radians
        roll, pitch, yaw = [math.radians(angle) for angle in orientation]

        # Create the pose matrix
        pose_matrix = transl(x, y, z) * rotx(roll) * roty(pitch) * rotz(yaw)

        # Get all possible joint solutions for the given pose
        all_solutions = self.robot.SolveIK_All(pose_matrix)

        # Iterate through each solution
        for new_robot_joints in all_solutions:
            # Retrieve flags as a list for each solution
            new_robot_config = self.robot.JointsConfig(new_robot_joints).list()

            # Check if the elbow is in an upward position
            if new_robot_config[1] == 0:
                print("Solution found!")
                # Move the robot to the pose
                self.robot.MoveL(new_robot_joints)
                break
        else:
            print("Warning! No solution with the elbow in an upward position found.")
    """


    """ THIS IS JUST THE OLD SIMPLE MOVE FUNCTION THAT WORK FINE WITHOUT ANY CONFIGURATION CHECKS.
    def simple_move(self, point=[474.50, -109.30,608.95], orientation=[90,90,90], speed=5):
        # Set the robot speed
        self.robot.setSpeed(speed)

        # Convert the coordinates from your application's coordinate system to RoboDK's coordinate system
        x,y,z = np.array(point)

        # Define the orientation in radians
        roll, pitch, yaw = [math.radians(angle) for angle in orientation]

        # Create the pose matrix
        pose_matrix = transl(x, y, z) * rotx(roll) * roty(pitch) * rotz(yaw)

        # Move the robot to the pose
        self.robot.MoveL(pose_matrix)
    """