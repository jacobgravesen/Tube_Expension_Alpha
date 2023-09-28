import cv2
import os
import datetime

# Specify the index of the webcam you want to use
camera_index = 2

# Specify the folder to save the images
image_folder = 'CallibrationImages'

# Create a VideoCapture object
cap = cv2.VideoCapture(camera_index)

# Check if the camera was opened successfully
if not cap.isOpened():
    print(f"Cannot open camera {camera_index}")
else:
    # Capture a single frame
    ret, frame = cap.read()

    # Check if the frame was captured successfully
    if not ret:
        print("Can't receive frame. Exiting ...")
    else:
        # Generate a unique filename based on the current date and time
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}.png"

        # Save the frame to a file
        cv2.imwrite(os.path.join(image_folder, filename), frame)

        print(f"Image saved to {filename}")

    # Release the VideoCapture object
    cap.release()