import supervision as sv
import numpy as np
from ultralytics import YOLO
import cv2

VIDEO_PATH = "shortenedRIO.mp4"
model = YOLO("yolov8s-seg.pt")

video_info = sv.VideoInfo.from_video_path(VIDEO_PATH)

def process_frame(frame: np.ndarray, _) -> np.ndarray:
    results = model(frame, imgsz=1280)[0]
    
    detections = sv.Detections.from_yolov8(results)

    box_annotator = sv.BoxAnnotator(thickness=0, text_thickness=0, text_scale=0)

    labels = ["" for _ in detections]
    frame = box_annotator.annotate(scene=frame, detections=detections, labels=labels)

    return frame

sv.process_video(source_path=VIDEO_PATH, target_path=f"result.mp4", callback=process_frame)
