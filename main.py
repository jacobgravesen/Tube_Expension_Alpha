from PyQt5.QtWidgets import QApplication #Import first to initialise the
import supervision as sv
import numpy as np
from ultralytics import YOLO
import cv2
from GUI.ui import MainWindow, setup_application
from PyQt5.QtWidgets import QApplication
from vision.Detector import Detector
from vision.PointCloudGenerator import PointCloudGenerator

from robot_movement.RobotInstructions import RobotInstructions

from robot_movement.TargetCoordsHandler import TargetCoordsHandler

from robot_movement.MoveRobot import MoveRobot
from utils.utils import load_transformation_matrix
from utils.utils import camera_to_robot_coordinates


# Instantiate the Detector class with the model path
detector = Detector('vision/best.pt', 'vision/intrinsic_parameters.csv')
# Start the pipeline
detector.start_pipeline(0)

# Instantiate the RobotInstructions class
robot_instructions = RobotInstructions(detector)

# Instantiate the TargetCoordsHandler class
target_coords_handler = TargetCoordsHandler()

# Instantiate the MoveRobot class
move_robot = MoveRobot(target_coords_handler, 'robot_movement/sim_robot_to_real_robot.csv')

# Create a QApplication instance using setup_application
app = setup_application()

# Create a MainWindow instance
window = MainWindow(robot_instructions, target_coords_handler)
window.show()
# Load the transformation matrix
camera_to_robot_transformation_matrix = load_transformation_matrix('vision/camera_to_robot.csv')



  
# Run while the video capture is open
while detector.cap.isOpened():
    # Get the processed frame and the 3D coordinates
    annotated_frame, points_3d = detector.get_frame_and_coordinates()

    # If no points were detected, continue to the next frame
    if annotated_frame is None or points_3d is None:
        continue

     # Write the 3D points to the CSV file
    #target_coords_handler.write_predictions_to_csv(points_3d)

    
    cv2.imshow("Holes Detector", annotated_frame)
    print(points_3d)


    # Close the video capture and depth stream when done
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        app.quit()
        break




    '''
    # Add the 3D points to the instructions
    robot_instructions.xs(points_3d)

    current_point = robot_instructions.get_next_point()
    current_point_transformed = np.dot(camera_to_robot_transformation_matrix, np.append(current_point, 1))[:-1]

    current_point = robot_instructions.get_next_point()
    if current_point is not None:
        current_point_transformed = np.dot(camera_to_robot_transformation_matrix, np.append(current_point, 1))[:-1]


        #move_robot.simple_move(current_point_transformed)
        robot_move_point = camera_to_robot_coordinates([6.3, 4.7, 60.9])
        # Move the robot to the hardcoded point
        move_robot.simple_move(robot_move_point)
                

    cv2.putText(annotated_frame, f'Current Point: {[round(num, 2) for num in current_point]}', (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)    
    cv2.putText(annotated_frame, f'Transformed Point: {[round(num, 2) for num in current_point_transformed]}', (10, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)    
    cv2.putText(annotated_frame, f'Lock State: {"Locked" if robot_instructions.is_locked else "Unlocked"}', (10, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    '''