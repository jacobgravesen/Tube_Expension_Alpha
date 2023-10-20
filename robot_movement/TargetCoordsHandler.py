import csv
from vision.Detector import Detector

class TargetCoordsHandler:
    def __init__(self):
        self.csv_file_path = 'robot_movement/required_points.csv'


    def write_predictions_to_csv(self, points_3d):
        # Open the CSV file in write mode
        with open(self.csv_file_path, 'w', newline='') as file:
            writer = csv.writer(file)

            # Write the header
            writer.writerow(["X", "Y", "Z"])

            # Write the coordinates to the CSV file
            for point in points_3d:
                writer.writerow([point[0], point[1], point[2]])

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