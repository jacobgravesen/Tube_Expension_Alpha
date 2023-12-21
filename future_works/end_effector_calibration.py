import os
import cv2
import numpy as np
import csv

def read_intrinsic_parameters_from_csv(file_path):
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        mtx = np.array([next(reader) for _ in range(3)], dtype=np.float32)
        _ = next(reader)  # Skip title row for distortion coefficients
        dist = np.array(next(reader), dtype=np.float32)
    return mtx, dist

import numpy as np
import cv2
import os

def save_camera_pose(image, rvec, tvec, filename):
    """
    Saves the image, rotation vector, and translation vector to the disk.
    """
    # Saving the image
    cv2.imwrite(f'successful_calibrations/{filename}.png', image)

    # Saving the rotation and translation vectors
    np.save(f'successful_calibrations/{filename}_rvec.npy', rvec)
    np.save(f'successful_calibrations/{filename}_tvec.npy', tvec)

def get_camera_pose(image, chessboard_size, square_size, mtx, dist):
    """
    Given an image, chessboard size, and square size, finds the camera pose.
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Find the chessboard corners
    success, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

    if not success:
        return False, None, None

    # Refine the corner positions
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

    # 3D points in the real world space
    obj_pts = np.zeros((np.prod(chessboard_size), 3), np.float32)
    obj_pts[:, :2] = np.indices(chessboard_size).T.reshape(-1, 2)
    obj_pts *= square_size

    # Solve for pose
    _, rvec, tvec = cv2.solvePnP(obj_pts, corners, mtx, dist)

    return True, rvec, tvec

def main():
    chessboard_size = (6, 9)
    square_size = 0.025  # In meters

    # Create directory to store successful calibrations
    os.makedirs("successful_calibrations", exist_ok=True)
    
    # Load camera intrinsic parameters from CSV file
    mtx, dist = read_intrinsic_parameters_from_csv('path/to/your/intrinsics.csv')
    
    image_folder = 'path/to/your/image/folder'
    image_files = [f for f in os.listdir(image_folder) if f.endswith('.jpg') or f.endswith('.png')]
    image_files.sort()

    for idx, image_file in enumerate(image_files):
        full_path = os.path.join(image_folder, image_file)
        image = cv2.imread(full_path)
        
        success, rvec, tvec = get_camera_pose(image, chessboard_size, square_size, mtx, dist)
        
        if success:
            print(f"Successfully found pose for {image_file}.")
            unique_filename = f"calibration_{idx}_{image_file[:-4]}"
            save_camera_pose(image, rvec, tvec, unique_filename)

if __name__ == "__main__":
    main()
