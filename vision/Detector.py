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
import csv

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

    def load_intrinsic_parameters(self, filename):
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            lines = list(reader)
            camera_matrix = np.array([list(map(float, line)) for line in lines[1:4]])
            distortion_coefficients = np.array(list(map(float, lines[5])))
        return camera_matrix, distortion_coefficients


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
         # Load intrinsic parameters
        camera_matrix, distortion_coefficients = self.load_intrinsic_parameters('vision/intrinsic_parameters.csv')

         # Get the focal length from the camera matrix
        fx = camera_matrix[0, 0]
        fy = camera_matrix[1, 1]

        # Wait for a coherent pair of frames: depth and color
        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        
        success, frame = self.cap.read()
        if success:
            start_time = time()  # Add this line to record the start time
            
            # Rectify the image
            frame = cv2.undistort(frame, camera_matrix, distortion_coefficients)

            # Use the track method instead of predict
            self.results = self.model.track(frame, persist=False) # Set persists=True for tracking.              
            box_centers = self.calculate_box_centers(self.results)
            annotated_frame = self.results[0].plot(boxes=False)

            # Define the coordinates of the two points
            height, width = frame.shape[:2]
            center_y = height // 2
            triangle_width = 70
            triangle_p_1 = (width // 2 - triangle_width, center_y)
            triangle_p_2 = (width // 2 + triangle_width, center_y)

             # Draw two red dots at the defined points
            cv2.circle(annotated_frame, triangle_p_1, radius=4, color=(0, 0, 255), thickness=-1)
            cv2.circle(annotated_frame, triangle_p_2, radius=4, color=(0, 0, 255), thickness=-1)

             # Calculate the angle of the plane
            box = [triangle_p_1[0], triangle_p_1[1], triangle_p_2[0], triangle_p_2[1]]
            self.angle = self.angle_calculator.calculate_angle(box, depth_frame)
            cv2.putText(annotated_frame, f'Angle: {float(self.angle):.1f}', (20,360), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,200,0), 2)

        
            # Check if any objects were detected and their IDs are available # prints box dimensions and ids.
            #print(f"boxes: {self.results[0].boxes}, boxes.id: {self.results[0].boxes.id}")

            if self.results[0].boxes is not None:
                # Draw each mask center as a small green dot and display the tracking ID
                for i, box in enumerate(self.results[0].boxes.xyxy):
                    center_x, center_y = self.calculate_box_center(box)

                    if center_x is not None and center_y is not None:
                        # Get the corners of the bounding box
                        corners = [(box[0], box[1]), (box[0], box[3]), (box[2], box[1]), (box[2], box[3])]
                        # Calculate the depth at each corner
                        depths = [self.get_depth(corner[0], corner[1], depth_frame) for corner in corners]
                        # Calculate the average depth
                        avg_depth = sum(depths) / len(depths)
                        # Convert 2D to 3D using the average depth
                        point_3d = pcg.convert_2d_to_3d([(center_x, center_y)], [avg_depth])[0]

                        kinematic_fence = -245
                        if point_3d[1] < kinematic_fence:
                            circle_color = (0,0,255)
                        elif abs(point_3d[2]) == 0:
                            circle_color = (0, 165, 255)
                        else:
                            circle_color = (255,255,0)
                        cv2.circle(annotated_frame, (center_x, center_y), radius=2, color=circle_color, thickness=-1)
                        #if self.results[0].boxes.id is not None and i < len(self.results[0].boxes.id):
                        #    track_id = self.results[0].boxes.id[i]
                        #    cv2.putText(annotated_frame, f'ID: {int(track_id)}, X: {point_3d[0]:.0f}, Y: {point_3d[1]:.0f}, Z: {point_3d[2]:.0f}', (center_x, center_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
                        #else:
                        #    cv2.putText(annotated_frame, f'X: {point_3d[0]:.0f}, Y: {point_3d[1]:.0f}, Z: {point_3d[2]:.0f}', (center_x, center_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)      

                        #if self.results[0].boxes.id is not None and i < len(self.results[0].boxes.id):
                        #    track_id = self.results[0].boxes.id[i]
                        #    cv2.putText(annotated_frame, f'{point_3d[0]:.0f}', (center_x, center_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                        #else:
                        #    cv2.putText(annotated_frame, f'{point_3d[0]:.0f}', (center_x, center_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)      


                        n_holes = len(self.results[0].boxes) if self.results[0].boxes is not None else 0
                        cv2.putText(annotated_frame, f'#Holes: {n_holes}', (20,325), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,200,0), 2)

                        # Calculate the physical width of the bounding box
                        #physical_width = self.calculate_physical_width(box, avg_depth, fx)


                        # Display the width on the frame
                        #cv2.putText(annotated_frame, f'{physical_width:.0f}', (center_x, center_y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

            
            fps = self.calculate_fps(start_time)
            cv2.putText(annotated_frame, f'FPS: {int(fps)}', (20,290), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,200,0), 2)

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

    def calculate_average_angle(self, angles):
        # Exclude angles where the absolute value is 0
        valid_angles = [angle for angle in angles if np.sum(angle) != 0]
        print("THIS IS SIMPLE ANGLES: ", angles)
        print("HEEEEEEEEEEEEEEEEY LOOOOOOOOOOOOOOOOOOK HEEEEEEEEEEERE!!!!:", valid_angles)
        # Calculate the average angle
        self.avg_angle = sum(valid_angles) / len(valid_angles) if valid_angles else None
        print("Average angle: ", self.avg_angle)
        return self.avg_angle

    def get_angle(self):
        return self.angle
   

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
    
    def calculate_physical_width(self, box, depth, f):
        # Calculate the width of the bounding box in pixels
        pixel_width = box[2] - box[0]  # assuming box is in the format (x1, y1, x2, y2)
        
        # Calculate the physical width of the bounding box
        physical_width = depth * (pixel_width / f)
        
        return physical_width
