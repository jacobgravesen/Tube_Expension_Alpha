from vision.Detector import Detector


class RobotInstructions:
    def __init__(self, detector):
        # Initialize an empty list to store the required points
        self.required_points = []
        # Initialize an empty list to store the completed points
        self.completed_points = []
        # Initialize the current point as None
        self.current_point = None
        self.is_locked = False  
        self.prev_length = 0
        self.same_length_counter = 0
        self.detector = detector


    def get_predicted_points(self):
        _, points_3d = self.detector.get_frame_and_coordinates()
        return points_3d

    def add_all_predicted_points(self, points):
        # Add new points to the list
        self.required_points.extend(points)
        
        # If there is no current point, set the first point as the current point
        if self.current_point is None and self.required_points:
            self.set_next_point()
                
    def set_next_point(self):
        if self.required_points:
            self.current_point = self.required_points[0]



    def get_next_point(self):
        # Get the next point from the list of required points
        if not self.is_locked and self.required_points:
            self.current_point = self.required_points[0]
        return self.current_point

    def mark_point_as_completed(self):
        # Remove the current point from the list of required points
        self.required_points.remove(self.current_point)
        # Add the current point to the list of completed points
        self.completed_points.append(self.current_point)
        # Reset the current point
        self.current_point = None

    def get_completed_points(self):
        # Return the list of completed points
        return self.completed_points

    def clear_points(self):
        # Clear the list of required and completed points
        self.required_points = []
        self.completed_points = []
        self.current_point = None

    def lock(self):
        self.is_locked = True

    