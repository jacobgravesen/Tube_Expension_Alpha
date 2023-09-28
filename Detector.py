import cv2
import torch
from ultralytics import YOLO
from time import time
#import numpy as np
#import cupy as np
import numpy as np
import pyrealsense2 as rs


class Detector:
    def __init__(self, model_path):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("Using Device: ", self.device)
        self.model = self.load_model(model_path)
        self.results = None  # Initialize results here

    def load_model(self, model_path):
        model = YOLO(model_path)
        model.fuse()
        return model

    def predict(self, frame):
        return self.model(frame)

    def run_segmentation(self, video_path_or_cam_index, pcg):
        if isinstance(video_path_or_cam_index, int):
            # Create a pipeline
            pipeline = rs.pipeline()

            # Create a config and configure it to stream depth stream
            config = rs.config()
            config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

            # Start streaming
            pipeline.start(config)

            cap = cv2.VideoCapture(video_path_or_cam_index)
            cap = cv2.VideoCapture(video_path_or_cam_index)
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            print(f"Webcam resolution: {width}x{height}")
        else:
            cap = cv2.VideoCapture(video_path_or_cam_index)
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            print(f"Webcam resolution: {width}x{height}")

        while cap.isOpened():
            start_time = time()
            success, frame = cap.read()
            if success:
                # Use the track method instead of predict
                self.results = self.model.track(frame, persist=True)                # mask_centers = self.calculate_mask_centers(results)
                box_centers = self.calculate_box_centers(self.results)
                annotated_frame = self.results[0].plot(boxes=False)

                # Wait for a coherent pair of frames: depth and color
                frames = pipeline.wait_for_frames()
                depth_frame = frames.get_depth_frame()

                # Check if any objects were detected and their IDs are available
                if self.results[0].boxes is not None and self.results[0].boxes.id is not None:
                    # Draw each mask center as a small green dot and display the tracking ID
                    for (center_x, center_y), track_id in zip(box_centers, self.results[0].boxes.id):
                        if center_x is not None and center_y is not None:
                            depth = self.get_depth(center_x, center_y, depth_frame)
                            point_3d = pcg.convert_2d_to_3d([(center_x, center_y)], [depth])[0]
                            cv2.circle(annotated_frame, (center_x, center_y), radius=2, color=(255, 255, 0), thickness=-1)
                            cv2.putText(annotated_frame, f'{int(track_id)}', (center_x, center_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                            cv2.putText(annotated_frame, f'Depth: {int(depth)}', (center_x, center_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                            cv2.putText(annotated_frame, f'3D: X={point_3d[0]:.2f}, Y={point_3d[1]:.2f}, Z={point_3d[2]:.2f}', (center_x, center_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                fps = self.calculate_fps(start_time)
                cv2.putText(annotated_frame, f'FPS: {int(fps)}', (20,70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2)
                cv2.imshow("Holes Detector", annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            else:
                break

        cap.release()
        cv2.destroyAllWindows()

        # Stop streaming
        pipeline.stop()

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
        Get the depth value of the specified pixel in centimeters
        """
        depth_in_meters = depth_frame.get_distance(x, y)
        depth_in_centimeters = depth_in_meters * 100
        return depth_in_centimeters

   

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
        center_x = (box[0] + box[2]) / 2
        center_y = (box[1] + box[3]) / 2
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


if __name__ == "__main__":            
    detector = Detector('best.pt')
    detector.run_segmentation(1)
    #detector.run_segmentation("shortenedRIO.mp4")