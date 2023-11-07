import cv2
import torch
from ultralytics import YOLO
from time import time
#import numpy as np
#import cupy as np
import numpy as np
import pyrealsense2 as rs
from vision.PointCloudGenerator import PointCloudGenerator
from vision.AngleCalculator import AngleCalculator

class Detector:
    def __init__(self, model_path, intrinsic_parameters_path):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("Using Device: ", self.device)
        self.model = self.load_model(model_path)
        self.results = None  # Initialize results here
        self.pipeline = None
        self.cap = None
        self.pcg = PointCloudGenerator(intrinsic_parameters_path)
        self.angle_calculator = AngleCalculator(intrinsic_parameters_path)



    def start_pipeline(self, video_path_or_cam_index):
        if isinstance(video_path_or_cam_index, int):
            # Create a pipeline
            self.pipeline = rs.pipeline()

            # Create a config and configure it to stream depth stream
            config = rs.config()
            config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

            # Start streaming
            self.pipeline.start(config)

            self.cap = cv2.VideoCapture(video_path_or_cam_index)
            width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            print(f"Webcam resolution: {width}x{height}")
        else:
            self.cap = cv2.VideoCapture(video_path_or_cam_index)
            width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            print(f"Webcam resolution: {width}x{height}")


    def load_model(self, model_path):
        model = YOLO(model_path)
        model.fuse()
        return model

    def predict(self, frame):
        return self.model(frame)

    def process_frame(self, pcg):
        # Wait for a coherent pair of frames: depth and color
        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()

        success, frame = self.cap.read()
        if success:
            start_time = time()  # Add this line to record the start time
            # Use the track method instead of predict
            self.results = self.model.track(frame, persist=True) # Set persists=True for tracking.              
            box_centers = self.calculate_box_centers(self.results)
            annotated_frame = self.results[0].plot(boxes=False)
            
            # Check if any objects were detected and their IDs are available # prints box dimensions and ids.
            #print(f"boxes: {self.results[0].boxes}, boxes.id: {self.results[0].boxes.id}")

            if self.results[0].boxes is not None:
                # Draw each mask center as a small green dot and display the tracking ID
                angles = []  # List to store all angles
                for i, box in enumerate(self.results[0].boxes.xyxy):
                    center_x, center_y = self.calculate_box_center(box)
                    angle = self.angle_calculator.calculate_angle(box, depth_frame)
                    angles.append(angle)  # Add the calculated angle to the list


                    if center_x is not None and center_y is not None:
                        # Get the corners of the bounding box
                        corners = [(box[0], box[1]), (box[0], box[3]), (box[2], box[1]), (box[2], box[3])]
                        # Calculate the depth at each corner
                        depths = [self.get_depth(corner[0], corner[1], depth_frame) for corner in corners]
                        # Calculate the average depth
                        avg_depth = sum(depths) / len(depths)
                        # Convert 2D to 3D using the average depth
                        point_3d = pcg.convert_2d_to_3d([(center_x, center_y)], [avg_depth])[0]
                        
                        
                        cv2.circle(annotated_frame, (center_x, center_y), radius=2, color=(255, 255, 0), thickness=-1)
                        if self.results[0].boxes.id is not None and i < len(self.results[0].boxes.id):
                            track_id = self.results[0].boxes.id[i]
                            cv2.putText(annotated_frame, f'ID: {int(track_id)}, X: {point_3d[0]:.2f}, Y: {point_3d[1]:.2f}, Z: {point_3d[2]:.2f}', (center_x, center_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        else:
                            cv2.putText(annotated_frame, f'X: {point_3d[0]:.2f}, Y: {point_3d[1]:.2f}, Z: {point_3d[2]:.2f}', (center_x, center_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)  
                
                # Calculate the average angle
                avg_angle = sum(angles) / len(angles) if angles else None
                # Print the average angle onto the annotated frame
                cv2.putText(annotated_frame, f'Avg Angle: {avg_angle:.2f}', (10, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            
            
            fps = self.calculate_fps(start_time)
            cv2.putText(annotated_frame, f'FPS: {int(fps)}', (20,70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2)

            # Get the 2D points and their corresponding depth values
            points_2d = self.calculate_box_centers(self.results)
            depth_values = [self.get_depth(x, y, depth_frame) for x, y in points_2d]

            return points_2d, depth_values, annotated_frame

        else:
            print("No boxes detected")  # Print a message if no boxes were detected
            return None, None

    def get_depth_frame(self):
        # Create a pipeline
        pipeline = rs.pipeline()

        # Create a config and configure it to stream depth stream
        config = rs.config()
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

        # Start streaming
        pipeline.start(config)

        # Wait for a depth frame
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()

        # Stop streaming
        pipeline.stop()

        return depth_frame

    def get_depth(self, x, y, depth_frame):
        """
        Get the depth value of the specified pixel in millimeters
        """
        depth_in_meters = depth_frame.get_distance(x, y)
        depth_in_millimeters = depth_in_meters * 1000
        return depth_in_millimeters

   

    def calculate_fps(self, start_time):
        end_time = time()
        fps = 1 / (end_time - start_time)
        return fps
    
    def calculate_mask_center(self, mask):
        # Check if the mask is empty
        if mask.shape[0] == 0:
            return None, None
        # Calculate the mean of the x and y coordinates
        
        center_x = np.mean(mask[:, 0])
        center_y = np.mean(mask[:, 1])

        return int(center_x), int(center_y)
    
    def calculate_mask_centers(self, results):
        mask_centers = []
        for result in results:
            # Check if masks were detected
            if result.masks is not None:
                for mask in result.masks.xy:  # Use xy attribute instead of segments
                    center_x, center_y = self.calculate_mask_center(mask)
                    mask_centers.append((center_x, center_y))
        return mask_centers
    
    def calculate_box_center(self, box):
        # The box coordinates are in the format (x1, y1, x2, y2)
        # Define the four corners of the box
        corners = [(box[0], box[1]), (box[0], box[3]), (box[2], box[1]), (box[2], box[3])]
        
        # Calculate the average x and y coordinates
        center_x = sum(corner[0] for corner in corners) / len(corners)
        center_y = sum(corner[1] for corner in corners) / len(corners)
        
        return int(center_x), int(center_y)
    
    def calculate_box_centers(self, results):
        box_centers = []
        if results is not None:
            for result in results:
                # Check if boxes were detected
                if result.boxes is not None:
                    for box in result.boxes.xyxy:  # Use xyxy attribute for boxes
                        center_x, center_y = self.calculate_box_center(box)
                        box_centers.append((center_x, center_y))
        return box_centers

    def get_frame_and_coordinates(self):
            points_2d, depth_values, annotated_frame = self.process_frame(self.pcg)
            if points_2d is not None and depth_values is not None:
                points_3d = self.pcg.convert_2d_to_3d(points_2d, depth_values)
            else:
                points_3d = None
            return annotated_frame, points_3d



if __name__ == "__main__":

    # Import required modules at the beginning of your vision file
    from vision.PointCloudGenerator import PointCloudGenerator
    from robot_movement.RobotInstructions import RobotInstructions
    from robot_movement.MoveRobot import MoveRobot
    from utils.utils import load_transformation_matrix
    from utils.utils import camera_to_robot_coordinates
    import numpy as np
    import cv2
    # Instantiate the Detector class with the model path
    detector = Detector('vision/best.pt')
    
    # Start the pipeline
    detector.start_pipeline(1)

    # Instantiate the PointCloudGenerator class with the intrinsic parameters file
    pcg = PointCloudGenerator('intrinsic_parameters.csv')
    
    # Instantiate the RobotInstructions class
    robot_instructions = RobotInstructions()
    
    # Instantiate the MoveRobot class
    move_robot = MoveRobot()

    # Load the transformation matrix
    camera_to_robot_transformation_matrix = load_transformation_matrix('camera_to_robot.csv')

    # Run while the video capture is open
    while detector.cap.isOpened():
        # Process a frame
        points_2d, depth_values, annotated_frame = detector.process_frame(pcg)  # Pass the pcg instance here



        # If no points were detected, continue to the next frame
        if points_2d is None or depth_values is None:
            continue

        # Convert the 2D points to 3D
        points_3d = pcg.convert_2d_to_3d(points_2d, depth_values)
        
        # Add the 3D points to the instructions
        robot_instructions.add_points(points_3d)

        current_point = robot_instructions.get_next_point()
        if current_point is not None:
            current_point_transformed = np.dot(camera_to_robot_transformation_matrix, np.append(current_point, 1))[:-1]

            ## Move the robot to the hardcoded point
            #move_robot.simple_move(current_point_transformed)

        # Update the annotated_frame display, or any other additional functionalities you need.
        cv2.putText(annotated_frame, f'Current Point: {[round(num, 2) for num in current_point]}', (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)    
        cv2.putText(annotated_frame, f'Transformed Point: {[round(num, 2) for num in current_point_transformed]}', (10, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)    
        cv2.putText(annotated_frame, f'Lock State: {"Locked" if robot_instructions.is_locked else "Unlocked"}', (10, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.imshow("Holes Detector", annotated_frame)

         # Close the video capture and depth stream when done
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Close the video capture and depth stream when done
    detector.close()
