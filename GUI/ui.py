from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QTextEdit, QLineEdit
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QWidget, QSizePolicy, QSpacerItem
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGridLayout
from PyQt5.QtGui import QImage, QPainter

from .CustomTitleBar import CustomTitleBar
from robot_movement.MoveRobot import MoveRobot
from robot_movement.RobotInstructions import RobotInstructions
from utils.utils import load_transformation_matrix
import numpy as np
import cv2



# Setting up the app color theme and other settings:
def setup_application():
    app = QApplication([])
    app.setStyle('Fusion')

    dark_palette = QPalette()

    # Base colors
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))

    # Button colors
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))

    # Highlight colors
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))

    app.setPalette(dark_palette)

    return app



class MainWindow(QMainWindow):
    def __init__(self, robot_instructions, target_coords_handler, detector):
        super().__init__()

        # This removes the standard Windows title bar. (Not Pretty)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.robot_instructions = robot_instructions
        self.target_coords_handler = target_coords_handler
        self.detector = detector

        self.should_exit = False  # Add this line

        self.required_points = []
        self.current_point = (-10.93, 60.895 , 47.45)

        self.camera_to_robot_transformation_matrix = load_transformation_matrix('vision/camera_to_robot.csv')

        self.move_robot = MoveRobot(target_coords_handler, 'robot_movement/sim_robot_to_real_robot.csv')

        self.initUI()


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:  # Check if 'q' key is pressed
            self.should_exit = True  # Set the flag to True
            # Set the WA_DeleteOnClose attribute
            self.setAttribute(Qt.WA_DeleteOnClose)
            self.close()  # Close the application

    def update_camera_feed(self):
          # Call the process_frame method and get the annotated_frame
        _, _, annotated_frame = self.detector.process_frame(self.detector.pcg)
          # Convert the annotated_frame from BGR to RGB
        frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)

         # Convert the frame to QImage
        height, width, channel = frame.shape
        bytesPerLine = 3 * width
        qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)

        # Update the QGraphicsScene with the new QPixmap
        self.camera_scene.clear()  # Clear the previous frame
        self.camera_scene.addPixmap(QPixmap.fromImage(qImg))


    def initUI(self):
        self.setWindowTitle('Tube Expansion Alpha')
        self.setGeometry(100, 100, 800, 600)

        # Create and set the layout first
        self.grid_layout = QGridLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.grid_layout)
        self.setCentralWidget(self.central_widget)

        # Add custom title bar
        self.initCustomTitleBar() 

        # Now, it's safe to call the other initialization methods
        self.initCameraFeedDisplay()
        self.initControlButtons()
        self.initStatusInformation()

        # Adjust the row stretch
        self.grid_layout.setRowStretch(0, 80)  # camera feed row
        self.grid_layout.setRowStretch(1, 20)  # all other elements row
        self.initCurrentPointDisplay()

        self.points_display = QTextEdit(self)
        self.points_display.setReadOnly(True)  # Make the QTextEdit read-only   
        self.points_display.setStyleSheet("color: white;")  # Set the text color to white

        


    def initCentralWidget(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

    def initCustomTitleBar(self):
        self.title_bar = CustomTitleBar(self)
        self.setMenuWidget(self.title_bar)  # Set the custom title bar


    def initControlButtons(self):
        # Create two QVBoxLayouts
        control_layout_left = QVBoxLayout()
        control_layout_right = QVBoxLayout()

        # Add 'Add CSV' button to the right layout
        self.add_csv_button = QPushButton('Add CSV')
        self.add_csv_button.clicked.connect(self.on_add_csv_button_clicked)
        control_layout_right.addWidget(self.add_csv_button)

        # Add 'Move to All Required Points' button to the right layout
        self.move_to_all_points_button = QPushButton('Move to All Required Points')
        self.move_to_all_points_button.clicked.connect(self.on_move_to_all_points_button_clicked)
        control_layout_right.addWidget(self.move_to_all_points_button)

        self.move_to_first_point_button = QPushButton('Move to First Point')
        self.move_to_first_point_button.clicked.connect(self.on_move_to_first_point_button_clicked)
        control_layout_right.addWidget(self.move_to_first_point_button)

         # Add 'Home' button to the right layout
        self.home_button = QPushButton('Home')
        self.home_button.clicked.connect(self.on_home_button_clicked)
        control_layout_right.addWidget(self.home_button)



        # Create a QHBoxLayout
        control_layout = QHBoxLayout()

        # Add the QVBoxLayouts to the QHBoxLayout
        control_layout.addLayout(control_layout_left)
        control_layout.addLayout(control_layout_right)

        # Create a QWidget and set the QHBoxLayout as its layout
        control_widget = QWidget()
        control_widget.setLayout(control_layout)

        # Add the QWidget to the grid layout
        self.grid_layout.addWidget(control_widget, 1, 0)

    def initStatusInformation(self):
        self.status_label = QLabel('Status: idle')
        self.grid_layout.addWidget(self.status_label, 1, 1)

    
    def initCameraFeedDisplay(self):
        # Create a QGraphicsView for displaying the camera feed
        self.camera_view = QGraphicsView(self)

        # Create a QGraphicsScene for holding the QPixmap
        self.camera_scene = QGraphicsScene(self)
        self.camera_view.setScene(self.camera_scene)

        # Create a timer for updating the camera feed
        self.camera_timer = QTimer()
        self.camera_timer.timeout.connect(self.update_camera_feed)
        self.camera_timer.start(100)  # Update every 100 ms

        self.grid_layout.addWidget(self.camera_view, 0, 0, 1, 6)  # Replace self.camera_label with self.camera_view


    def update_status(self, status):
        self.status_label.setText(f'Status: {status}')

    def log(self, message):
        self.log_output.append(message)

    def closeEvent(self, event): # Handling properly closing webcam when closing application.
        pass

    def initCurrentPointDisplay(self):
        # Create QLabel for displaying the current point
        self.current_point_label = QLabel(self)
        self.grid_layout.addWidget(self.current_point_label, 3, 0, 1, 7)  # Span the label across all columns

    def update_current_point(self):
        # Check if there are any points left in the list
        if self.required_points:
            # Get the first point from the list
            next_point = self.required_points.pop(0)
            
            # Update the Current Point Variable
            self.current_point = next_point
            
            # Update the text of the label displaying the current point
            self.current_point_label.setText(f'Current Point: {self.current_point}')

            # Update the points display
            self.update_points_display()
        else:
            print('No more points in the list')

    def on_add_points_button_clicked(self):
        # Use the get_predicted_points method of the RobotInstructions class to get the points
        points = self.robot_instructions.get_predicted_points()

        # Apply the transformation to each point
        transformed_points = []
        for point in points:
            transformed_point = np.dot(self.camera_to_robot_transformation_matrix, np.append(point, 1))[:-1]
            transformed_points.append(transformed_point)

        # Call the add_all_predicted_points method with the transformed points
        self.robot_instructions.add_all_predicted_points(transformed_points)

        # Update the points list and the points display
        self.required_points = transformed_points
        self.update_points_display()    

    def update_points_display(self):
        # Start the text with the current point, if it's not None
        text = f"<b>Current Point:</b> X: {self.current_point[0]:.2f}, Y: {self.current_point[1]:.2f}, Z: {self.current_point[2]:.2f}<br>" if self.current_point is not None else ""

        # Add the required points to the text
        text += f"<b>Required Points:</b> [{len(self.required_points)}]<br>"
        for i, point in enumerate(self.required_points, start=1):
            text += f"<b>Point {i}:</b> X: {point[0]:.2f}, Y: {point[1]:.2f}, Z: {point[2]:.2f}<br>"

        # Set the text of the points display
        self.points_display.setHtml(text)


    def on_add_csv_button_clicked(self):
        # Get the 3D points
        _, points_3d = self.robot_instructions.detector.get_frame_and_coordinates()

        # If points were detected, write them to the CSV file
        if points_3d is not None:
            self.target_coords_handler.write_predictions_to_csv(points_3d)
        
        angle = self.robot_instructions.detector.get_angle()
        
        if angle is not None:
            self.target_coords_handler.write_angle_to_csv(angle)

    def on_move_to_all_points_button_clicked(self):
        self.move_robot.move_to_all_required_points()

    def on_move_to_first_point_button_clicked(self):
        self.move_robot.move_to_first_required_point()

    def on_home_button_clicked(self):
        self.move_robot.return_to_base()

if __name__ == '__main__':
    app = setup_application()

    mainWin = MainWindow()
    mainWin.show()

    app.exec()