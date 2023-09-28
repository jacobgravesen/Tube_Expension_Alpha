import supervision as sv
import numpy as np
from ultralytics import YOLO
import cv2


"""
VIDEO_PATH = "shortenedRIO.mp4"
model = YOLO("yolov8s-seg.pt")

video_info = sv.VideoInfo.from_video_path(VIDEO_PATH)

def process_frame(frame: np.ndarray, _) -> np.ndarray:
    results = model(frame, imgsz=1280)[0]
    q
    detections = sv.Detections.from_yolov8(results)

    box_annotator = sv.BoxAnnotator(thickness=0, text_thickness=0, text_scale=0)

    labels = ["" for _ in detections]
    frame = box_annotator.annotate(scene=frame, detections=detections, labels=labels)

    return frame

sv.process_video(source_path=VIDEO_PATH, target_path=f"result.mp4", callback=process_frame)
"""

from Detector import Detector
from PointCloudGenerator import PointCloudGenerator

# Instantiate the Detector class with the model path
detector = Detector('best.pt')


# Instantiate the PointCloudGenerator class with the intrinsic parameters file
pcg = PointCloudGenerator('intrinsic_parameters.csv')

# Run the segmentation on the webcam feed
detector.run_segmentation(2, pcg)  

# Get the 2D points and their corresponding depth values
points_2d = detector.calculate_box_centers(detector.results)
depth_values = [detector.get_depth(x, y, detector.depth_frame) for x, y in points_2d]

# Convert the 2D points to 3D
points_3d = pcg.convert_2d_to_3d(points_2d, depth_values)

# Now points_3d contains the 3D coordinates of the detected objects' centers