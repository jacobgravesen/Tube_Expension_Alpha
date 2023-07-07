import cv2
from PyQt5.QtGui import QImage
import numpy as np

class VisionSystem:
    def __init__(self):
        self.capture = cv2.VideoCapture(0)  # 0 is the index of the default webcam

    def get_current_frame(self):
        ret, frame = self.capture.read()

        if ret:
            # Convert the frame to format understandable by QImage (RGB888)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            bytesPerLine = 3 * width
            return QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
        else:
            # In case of error, return a default QImage
            return QImage()

