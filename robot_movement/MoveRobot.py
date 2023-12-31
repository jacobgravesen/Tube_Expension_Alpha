from robolink import Robolink, Item
import numpy as np
from robodk.robomath import transl
from robodk.robomath import rotz, roty, rotx
import math
from robolink import Robolink, Item, ROBOTCOM_READY, RUNMODE_RUN_ROBOT
import csv
from utils.utils import load_transformation_matrix
from scipy.spatial.transform import Rotation as R
import robodk
import time

class MoveRobot:
    def __init__(self, target_coords_handler, sim_robot_to_real_robot_angle_file):
        self.robodk = Robolink()
        self.station = self.robodk.Item('Station1')
        if not self.station.Valid():
            self.station = self.robodk.AddFile('Station1.rdk')
        self.robot = self.robodk.Item('UR5') 
        self.robot_speed = 60

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

    def read_plate_angle(self, file_path='robot_movement/plate_angle.csv'):
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            angle = float(next(reader)[0])
        return angle

    def rotate_point_around_base(self, point):
        # Convert the rotation angle to radians
        angle_rad = math.radians(-45)  # adjust this value as needed
        # Create the rotation matrix
        rotation_matrix = np.array([[math.cos(angle_rad), -math.sin(angle_rad), 0],
                                    [math.sin(angle_rad), math.cos(angle_rad), 0],
                                    [0, 0, 1]])
        # Apply the rotation to the point
        rotated_point = np.dot(rotation_matrix, point)
        return rotated_point
    
    def move_robot_to_point(self, point):
        if point is not None and len(point) >= 3:
            # Convert the coordinates to RoboDK's coordinate system
            x, y, z = np.array(point)
            """
            # Define the interpolation range
            y_start = 0
            y_end = 230
            interp_start = 0
            interp_end = -10

            # Apply the interpolation to the y-coordinate
            if y < y_start:
                y_interp = 0
            elif y > y_end:
                y_interp = interp_end
            else:
                y_interp = interp_start + ((y - y_start) / (y_end - y_start)) * (interp_end - interp_start)

            y += y_interp
            """
            """
            # Define the interpolation range for z
            z_start = 0
            z_end = 450
            interp_start_z = 0
            interp_end_z = 10

            # Apply the interpolation to the z-coordinate
            if z < z_start:
                z_interp = 0
            elif z > z_end:
                z_interp = interp_end_z
            else:
                z_interp = interp_start_z + ((z - z_start) / (z_end - z_start)) * (interp_end_z - interp_start_z)

            z += z_interp
            """
            # Create the pose matrix with no orientation
            pose_matrix = transl(x-75-20-50, y-338, z+86) # 55

            #pose_matrix = tool_matrix * pose_matrix 

            #tool_transformation = transl(-120,0, 0)
            #pose_matrix = tool_transformation * pose_matrix
            
            # Create a 4x4 rotation matrix around the z-axis
          
            rotation_angle_rad = math.radians(-45)  # adjust this value as needed
            rotation_matrix_list = [[math.cos(rotation_angle_rad), -math.sin(rotation_angle_rad), 0, 0],
                                    [math.sin(rotation_angle_rad), math.cos(rotation_angle_rad), 0, 0],
                                    [0, 0, 1, 0],
                                    [0, 0, 0, 1]]

            # Convert the list of lists to a robodk.robomath.Mat object
            rotation_matrix_robodk = robodk.robomath.Mat(rotation_matrix_list)

            # Apply the rotation
            pose_matrix = rotation_matrix_robodk * pose_matrix

            
            
            # Define the orientation in radians
            roll, pitch, yaw = [math.radians(angle) for angle in [0, 90, 0]]
            
            # Apply the orientation
            pose_matrix = pose_matrix * rotx(roll) * roty(pitch) * rotz(yaw)

            angle = self.read_plate_angle()
            #pose_matrix = pose_matrix * rotx(math.radians(-angle))
            
            #self.robot.MoveL(pose_matrix)
            #pose_matrix = pose_matrix * transl(0,0,40)
            #self.robot.setSpeed(self.robot_speed/5)

            #self.robot.MoveL(pose_matrix)
            #self.robot.setSpeed(self.robot_speed)
            #pose_matrix = pose_matrix * transl(0,0,-40)
            #self.robot.MoveL(pose_matrix)

            # Enable collision checking
            kinematic_fence_y = -230 # was -245
            if point[1] < kinematic_fence_y:
                print(f"Point {point} is too close to the kinematic fence. Skipping this point.")
            else:
                self.robodk.setCollisionActive(1)
                # Check if the pose is reachable by the robot and if the movement would result in a collision
                if self.robot.Valid(pose_matrix) or self.robot.MoveL_Test(pose_matrix) < 0:
                    print(f"Pose {pose_matrix} is  reachable by the robot or would not result in a collision. Skipping this pose.")

                    print("Moving to goal: ", pose_matrix)
                    # Move the robot to the pose
                    self.robot.MoveL(pose_matrix*transl(0,0,-40))
                    self.robot.setSpeed(self.robot_speed/3)
                    self.robot.MoveL(pose_matrix)
                    self.robot.setSpeed(self.robot_speed)
                    self.robot.MoveL(pose_matrix*transl(0,0,-40))


    def move_to_first_required_point(self, point=None):
        try:
            if point is None:
                # Step 1: Write the first point from required_points.csv to current_point.csv
                self.target_coords_handler.write_current_point_to_csv()

                # Step 2: Get the current point from current_point.csv
                point = self.target_coords_handler.read_current_point_from_csv()

                # Check if point is None
                if point is None:
                    print("No more points in the list")
                    return
                
                self.robot.setSpeed(self.robot_speed)
                #self.move_robot_to_point([point[0]-30, point[1], point[2]])

                #self.robot.setSpeed(self.robot_speed/5)
                self.move_robot_to_point([point[0], point[1], point[2]])
                #self.robot.setSpeed(self.robot_speed)
                #self.move_robot_to_point([point[0]-30, point[1], point[2]])

                self.target_coords_handler.move_completed_point()
        except Exception as e:
            print(f"An error occured: {e}")

    def move_to_all_required_points(self):
        # Get the initial number of points
        num_points = self.target_coords_handler.get_num_required_points()

        for _ in range(num_points):
            time.sleep(1)
            try:
                print("Moving to next point:")
                self.move_to_first_required_point()
            except Exception as e:
                print(f"An error occurred: {e}")
                continue
            
        self.return_to_base()


    def return_to_base(self):
        # Define the base joint values
        self.robot.setSpeed(self.robot_speed)
        base_joint_values = [-41.27, -70.23, -125.56, -164.61, -93.61, -89.76]

        # Move the robot to the base joint values
        self.robot.MoveJ(base_joint_values)