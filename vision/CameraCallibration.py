import cv2
import numpy as np
import csv
import os

class CameraCalibrator:
    def __init__(self, board_shape=(7, 6), square_size=3.59):
        self.board_shape = board_shape
        self.square_size = square_size
        self.obj_points = []  # 3D points in real-world space
        self.img_points = []  # 2D points in image plane
        self.image_shape = None  # Initialize to None

        # Prepare the object points
        self.objp = np.zeros((board_shape[1] * board_shape[0], 3), np.float32)
        self.objp[:, :2] = np.mgrid[0:board_shape[0], 0:board_shape[1]].T.reshape(-1, 2) * square_size

        self.mtx = None  # Camera matrix
        self.dist = None  # Distortion coefficient
    def add_image(self, image, image_file):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, self.board_shape, None)
        if ret:
            self.obj_points.append(self.objp)
            self.img_points.append(corners)
            if self.image_shape is None:
                self.image_shape = gray.shape[::-1]
            return True, image_file
        else:
            return False, image_file


    def calibrate(self):
        if self.image_shape is None:  # No images have been added
            print("No images added for calibration.")
            return False

        print("Starting calibration...")
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(self.obj_points, self.img_points, self.image_shape, None, None)
        print("Calibration finished.")

        
        if ret:
            self.mtx = mtx
            self.dist = dist
            return True
        else:
            print("Calibration failed.")
            return False

    def save_intrinsic_parameters(self, filename='intrinsic_parameters.csv'):
        if self.mtx is None or self.dist is None:
            print("No intrinsic parameters to save. Perform calibration first.")
            return False

        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            
            writer.writerow(['Camera Matrix'])
            for row in self.mtx:
                writer.writerow(row)
            
            writer.writerow(['Distortion Coefficients'])
            for row in self.dist:
                writer.writerow(row)

        print(f"Intrinsic parameters saved to {filename}.")
        return True

def compute_reprojection_error(obj_points, img_points, rvecs, tvecs, mtx, dist):
    """
    Compute the total reprojection error for the calibrated camera.
    
    Parameters:
    - obj_points: The object points used in calibration
    - img_points: The image points used in calibration
    - rvecs: The rotation vectors obtained from calibration
    - tvecs: The translation vectors obtained from calibration
    - mtx: The camera matrix
    - dist: The distortion coefficients
    
    Returns:
    - mean_error: The mean re-projection error
    """
    total_error = 0
    for i in range(len(obj_points)):
        imgpoints2, _ = cv2.projectPoints(obj_points[i], rvecs[i], tvecs[i], mtx, dist)
        error = cv2.norm(img_points[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
        total_error += error
    
    mean_error = total_error / len(obj_points)
    return mean_error

def visualize_points(image, original_points, reprojected_points):
    for orig, reproj in zip(original_points, reprojected_points):
        cv2.circle(image, tuple(orig.ravel().astype(int)), 5, (0, 255, 0), -1)  # Original points in green
        cv2.circle(image, tuple(reproj.ravel().astype(int)), 5, (0, 0, 255), -1)  # Reprojected points in red

    cv2.imshow('Comparison', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def visualize_all_points(image_folder, processed_image_files, obj_points, img_points, mtx, dist):
    min_length = min(len(obj_points), len(img_points), len(processed_image_files))
    for i in range(min_length):
        image_path = os.path.join(image_folder, processed_image_files[i])
        image = cv2.imread(image_path)

        if image is None:
            print(f"Couldn't read {image_files[i]}. Skipping...")
            continue

        ret, rvec, tvec = cv2.solvePnP(obj_points[i], img_points[i], mtx, dist)
        if not ret:
            print(f"Failed to solve PnP for {image_files[i]}. Skipping...")
            continue

        reprojected_points, _ = cv2.projectPoints(obj_points[i], rvec, tvec, mtx, dist)
        visualize_points(image, img_points[i], reprojected_points)




if __name__ == "__main__":
    calibrator = CameraCalibrator((6,9), 2.3) # width x height

    # Specify the folder containing the images for calibration
    image_folder = r'C:\Users\grave\Desktop\Tube_Expension_Alpha\CallibrationImages'
    
    # List all files in the specified folder
    image_files = [f for f in os.listdir(image_folder) if f.endswith('.jpg') or f.endswith('.png')]

    # Sort the image files to ensure consistent ordering
    image_files.sort()

    processed_image_files = []

    total_images = len(image_files)
    processed_images = 0

    for image_file in image_files:
        full_path = os.path.join(image_folder, image_file)
        image = cv2.imread(full_path)
        
        success, processed_image = calibrator.add_image(image, image_file)
        
        if success:
            print(f"Added {image_file} for calibration.")
            processed_image_files.append(processed_image)
        else:
            print(f"Failed to add {image_file} for calibration.")
        
        processed_images += 1
        print(f"Processed {processed_images}/{total_images} images.")

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        calibrator.obj_points, calibrator.img_points, calibrator.image_shape, None, None
    )

    if ret:
        print("Calibration successful.")
        
        calibrator.mtx = mtx
        calibrator.dist = dist

        # Compute reprojection error
        mean_error = compute_reprojection_error(
            calibrator.obj_points, calibrator.img_points, rvecs, tvecs, calibrator.mtx, calibrator.dist
        )
        print(f"Mean Reprojection Error: {mean_error}")

        
        visualize_all_points(image_folder, processed_image_files, calibrator.obj_points, calibrator.img_points, calibrator.mtx, calibrator.dist)


        print("Camera Matrix:", calibrator.mtx)
        print("Distortion Coefficients:", calibrator.dist)
        calibrator.save_intrinsic_parameters()
    else:
        print("Calibration failed.")
