from robolink import Robolink, Item
import numpy as np
from robodk.robomath import transl
from robodk.robomath import rotz, roty, rotx
import math


class MoveRobot:
    def __init__(self, target_coords_handler):
        self.robodk = Robolink()
        self.station = self.robodk.Item('Station1')
        if not self.station.Valid():
            self.station = self.robodk.AddFile('Station1.rdk')
        self.robot = self.robodk.Item('UR5') 

        self.current_point = None
        self.target_coords_handler = target_coords_handler

    
    def simple_move(self, point=[474.50, -109.30,608.95], orientation=[math.radians(0), 90, math.radians(0)], speed=20): # used to be orientation=[90,90,90] # Now: orientation=[math.radians(0),90,math.radians(0)]. This is dusche dobre.
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

            # Check if the elbow is in an upward position and the wrist is in a non-flip position
            if new_robot_config[1] == 0:  # adjust this condition as needed
                print("Solution found for elbow Up!")
                # Move the robot to the pose
                self.robot.MoveL(new_robot_joints)
                break
        else:
            print("Warning! No solution with the elbow in an upward position found.")

    def move_robot_to_specific_point(self, point, min_height=20):
        # Check if the point has been set
        if point is not None:
            # Check if the height is above the minimum
            if point[1] >= min_height:
                # Convert the point from cm to mm
                point_mm = tuple(coordinate * 10 for coordinate in point)
                # Rearrange the coordinates
                transformed_point = (point_mm[2], point_mm[0], point_mm[1])
                # Move the robot to the transformed point
                self.simple_move(transformed_point)
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

    def move_to_first_required_point(self, min_height=20):
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