import csv
from vision.Detector import Detector
from sklearn.cluster import DBSCAN


class TargetCoordsHandler:
    def __init__(self):
        self.csv_file_path = 'robot_movement/required_points.csv'


    def write_predictions_to_csv(self, points_3d):
        print("Points")
        print(points_3d)

        # Cluster and sort the points
        sorted_points = self.cluster_and_sort_points(points_3d)
        #sorted_points = points_3d
        # Open the CSV file in write mode
        with open(self.csv_file_path, 'w', newline='') as file:
            writer = csv.writer(file)

            # Write the header
            writer.writerow(["X", "Y", "Z"])

            # Write the sorted points to the CSV file
            for point in sorted_points:
                if abs(point[2]) != 0:
                    writer.writerow([point[0], point[1], point[2]])
    
    def write_angle_to_csv(self, avg_angle):
        with open('robot_movement/plate_angle.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([avg_angle])

    def write_current_point_to_csv(self):
        print("write_current_point_to_csv called")

        # Open the required_points.csv file in read mode
        with open(self.csv_file_path, 'r') as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip the header
            points = list(reader)  # Get all rows

        print(f"Read {len(points)} points from {self.csv_file_path}")

        if points:
            # Get the first point and remove it from the list
            first_point = points.pop(0)

            print(f"Writing point {first_point} to current_point.csv")

            # Write the first point to the current_point.csv file
            with open('robot_movement/current_point.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["X", "Y", "Z"])  # Write the header
                writer.writerow(first_point)  # Write the first point

            print(f"Writing remaining {len(points)} points back to {self.csv_file_path}")

            # Write the remaining points back to the required_points.csv file
            with open(self.csv_file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["X", "Y", "Z"])  # Write the header
                writer.writerows(points)  # Write the remaining points

    def move_completed_point(self):
        completed_points_file_path = 'robot_movement/completed_points.csv'

        # Open the current_point.csv file in read mode
        with open('robot_movement/current_point.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip the header
            current_point = list(reader)  # Get all rows

        if current_point:
            # Get the first point and remove it from the list
            completed_point = current_point.pop(0)

            # Write the completed point to the completed_points.csv file
            with open(completed_points_file_path, 'a', newline='') as file:
                writer = csv.writer(file)
                if file.tell() == 0:  # Write the header if the file is empty
                    writer.writerow(["X", "Y", "Z"])
                writer.writerow(completed_point)  # Write the completed point

            # Clear the current_point.csv file
            with open('robot_movement/current_point.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["X", "Y", "Z"])  # Write the header

    def get_num_required_points(self):
        with open('robot_movement/required_points.csv', 'r') as f:
            return sum(1 for line in f)

    def read_current_point_from_csv(self):
        # Open the current_point.csv file in read mode
        with open('robot_movement/current_point.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip the header
            current_point = list(reader)  # Get all rows

        if current_point:
            # Get the first point and convert it to a list of floats
            current_point = list(map(float, current_point[0]))
            return current_point
        else:
            return None
        
    def cluster_and_sort_points(self, points_3d, eps=5, min_samples=1):
        # Cluster the points by Z value
        z_values = [[point[2]] for point in points_3d]
        db = DBSCAN(eps=eps, min_samples=min_samples).fit(z_values)
        clusters = {label: [] for label in set(db.labels_)}
        for point, label in zip(points_3d, db.labels_):
            clusters[label].append(point)

        # Calculate the average Z value for each cluster
        avg_z_values = {label: sum(point[2] for point in points) / len(points) for label, points in clusters.items()}

        # Sort the clusters based on the average Z values, in descending order
        sorted_clusters = sorted(clusters.items(), key=lambda item: avg_z_values[item[0]], reverse=True)

        # Sort the points in each cluster based on their Y values, from lowest to highest
        sorted_points = [sorted(points, key=lambda point: point[1]) for label, points in sorted_clusters]

        # Reverse every second cluster
        for i in range(1, len(sorted_points), 2):
            sorted_points[i] = sorted_points[i][::-1]

        # Flatten the list of sorted points
        return [point for points in sorted_points for point in points]
