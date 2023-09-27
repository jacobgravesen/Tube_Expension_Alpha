import cv2
import torch
from ultralytics import YOLO
from time import time
#import numpy as np
import cupy as np

class Detector:
    def __init__(self, model_path):

        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("Using Device: ", self.device)

        self.model = self.load_model(model_path)

    def load_model(self, model_path):
        model = YOLO(model_path)
        model.fuse()
        return model

    def predict(self, frame):
        return self.model(frame)

    def run_segmentation(self, video_path):
        cap = cv2.VideoCapture(video_path)
        while cap.isOpened():
            start_time = time()
            success, frame = cap.read()
            if success:
                
                # Use the track method instead of predict
                results = self.model.track(frame, persist=True)
                # mask_centers = self.calculate_mask_centers(results)
                box_centers = self.calculate_box_centers(results)
                annotated_frame = results[0].plot(boxes=False)
                
                # Check if any objects were detected and their IDs are available
                if results[0].boxes is not None and results[0].boxes.id is not None:
                    # Draw each mask center as a small green dot and display the tracking ID
                    for (center_x, center_y), track_id in zip(box_centers, results[0].boxes.id):
                        if center_x is not None and center_y is not None:
                            cv2.circle(annotated_frame, (center_x, center_y), radius=2, color=(255, 255, 0), thickness=-1)
                            cv2.putText(annotated_frame, f'{int(track_id)}', (center_x, center_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                fps = self.calculate_fps(start_time)
                cv2.putText(annotated_frame, f'FPS: {int(fps)}', (20,70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2)
                cv2.imshow("Holes Detector", annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            else:
                break
        cap.release()
        cv2.destroyAllWindows()

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
        for result in results:
            # Check if boxes were detected
            if result.boxes is not None:
                for box in result.boxes.xyxy:  # Use xyxy attribute for boxes
                    center_x, center_y = self.calculate_box_center(box)
                    box_centers.append((center_x, center_y))
        return box_centers
            
detector = Detector('best.pt')
detector.run_segmentation('shortenedRIO.mp4')