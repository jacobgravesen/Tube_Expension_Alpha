import cv2
import numpy as np
import csv

class PointCloudGenerator:
    def __init__(self, intrinsic_csv='intrinsic_parameters.csv'):
        self.mtx = None  # Camera Matrix
        self.dist = None  # Distortion Coefficients
        self.read_intrinsic_parameters(intrinsic_csv)
        
    def read_intrinsic_parameters(self, filename):
        try:
            with open(filename, 'r') as file:
                csv_reader = csv.reader(file)
                mode = None
                mtx_rows = []
                dist_rows = []
                
                for row in csv_reader:
                    if row[0] == 'Camera Matrix':
                        mode = 'mtx'
                        continue
                    elif row[0] == 'Distortion Coefficients':
                        mode = 'dist'
                        continue
                    
                    if mode == 'mtx':
                        mtx_rows.append([float(x) for x in row])
                    elif mode == 'dist':
                        dist_rows.append([float(x) for x in row])
            
            self.mtx = np.array(mtx_rows)
            self.dist = np.array(dist_rows)
            
            return True
        except Exception as e:
            print(f"Failed to read intrinsic parameters: {e}")
            return False
    
    def convert_2d_to_3d(self, points_2d, depth_values):
        points_3d = []
        
        for (x, y), depth in zip(points_2d, depth_values):
            X = (x - self.mtx[0, 2]) * depth / self.mtx[0, 0]
            Y = (y - self.mtx[1, 2]) * depth / self.mtx[1, 1]
            Z = depth
            
            points_3d.append((X, Y, Z))
        
        return np.array(points_3d)

if __name__ == "__main__":
    pcg = PointCloudGenerator()
    
    # Example 2D points and their corresponding depth values
    points_2d = [(100, 100), (200, 200), (300, 300)]
    depth_values = [1000, 1200, 1100]  # Depth in mm or any other unit
    
    points_3d = pcg.convert_2d_to_3d(points_2d, depth_values)
    print(f"3D Points: {points_3d}")
