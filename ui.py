from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QTextEdit
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QWidget, QSizePolicy, QSpacerItem
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtCore import Qt, QPoint
from vision import VisionSystem
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGridLayout



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

class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Background, QColor(53, 53, 53))
        self.setPalette(palette)

        self.m_mouse_down = False
        self.m_old_pos = None

        self.initUI()

    def initUI(self):
        self.setAutoFillBackground(True)
        self.setFixedHeight(32)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel('Tube Expansion Alpha')
        self.title_label.setStyleSheet("QLabel { color : white; }")

        btn_size = 32

        # Cross Button
        self.btn_close = QPushButton('')
        self.btn_close.clicked.connect(self.btn_close_clicked)
        self.btn_close.setFixedSize(btn_size, btn_size)
        self.btn_close.setIcon(QIcon('Icons\cross_icon.png')) 

        # Minimize Button
        self.btn_min = QPushButton('')
        self.btn_min.clicked.connect(self.btn_min_clicked)
        self.btn_min.setFixedSize(btn_size, btn_size)
        self.btn_min.setIcon(QIcon('Icons\minimize_icon.png'))  

        # Maximize/Restore Button
        self.btn_max = QPushButton('')
        self.btn_max.clicked.connect(self.btn_max_clicked)
        self.btn_max.setFixedSize(btn_size, btn_size)
        self.btn_max.setIcon(QIcon('Icons\Maximize_icon.png')) 

        self.max_icon = QIcon('Icons\Maximize_icon.png')
        self.restore_icon = QIcon('Icons\Restore_down_icon.png') 
        self.btn_max.setIcon(self.max_icon)

        layout.addWidget(self.title_label)
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout.addWidget(self.btn_min)
        layout.addWidget(self.btn_max)
        layout.addWidget(self.btn_close)

    def btn_max_clicked(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.btn_max.setIcon(self.max_icon)  # Set icon to maximize
        else:
            self.parent().showMaximized()
            self.btn_max.setIcon(self.restore_icon)  # Set icon to restore

    def mousePressEvent(self, event):
        self.m_old_pos = event.pos()
        self.m_mouse_down = event.button() == Qt.LeftButton

        # When mouse is pressed, record whether the window is maximized
        self.m_was_maximized = self.parent().isMaximized()
        if self.m_was_maximized:
            # Store global mouse position when the user starts dragging the window
            self.m_global_mouse_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        x = event.x()
        y = event.y()

        if self.m_mouse_down:
            parent = self.parent()
            if self.m_was_maximized:
                # When the window is maximized and the user starts dragging, we should 'restore down' the window
                # and calculate the new position of the window.
                parent.showNormal()
                self.btn_max.setIcon(self.max_icon)  # Set icon to maximize
                # Calculate ratio of mouse position in relation to window size
                ratio = self.m_old_pos.x()/self.width()
                # Calculate new x position for the window and ensure it's an integer
                # Now, instead of aligning the mouse to the old position in the title bar,
                # we align it to the center of the window
                new_x = int(event.globalPos().x() - self.width() / 2)
                new_y = int(event.globalPos().y() - self.m_old_pos.y())
                parent.move(new_x, new_y)
            else:
                parent.move(parent.x() + x - self.m_old_pos.x(), parent.y() + y - self.m_old_pos.y())

    def mouseReleaseEvent(self, event):
        self.m_mouse_down = False

        # If the mouse is released at the top of the screen, maximize the window
        if event.globalPos().y() == 0:
            self.parent().showMaximized()
            self.btn_max.setIcon(self.restore_icon)  # Set icon to restore

    def btn_close_clicked(self):
        self.parent().close()

    def btn_min_clicked(self):
        self.parent().showMinimized()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # This removes the standard Windows title bar. (Not Pretty)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.initUI()

        # Create instance of vision system
        self.vision_system = VisionSystem()
    
    def update_camera_feed(self):
        # Get the current frame from the vision system as a QImage
        frame = self.vision_system.get_current_frame()       

        # Update the QGraphicsScene with the new QPixmap
        self.camera_scene.clear()  # Clear the previous frame
        self.camera_scene.addPixmap(QPixmap.fromImage(frame))

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
        self.initSystemParameters()
        self.initLogOutput()
        self.initManualControl()

        # Adjust the row stretch
        self.grid_layout.setRowStretch(0, 80)  # camera feed row
        self.grid_layout.setRowStretch(1, 20)  # all other elements row


    def initCentralWidget(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

    def initCustomTitleBar(self):
        self.title_bar = CustomTitleBar(self)
        self.setMenuWidget(self.title_bar)  # Set the custom title bar


    def initControlButtons(self):
        control_layout = QVBoxLayout()

        self.start_button = QPushButton('Start')
        self.stop_button = QPushButton('Stop')
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)

        control_widget = QWidget()
        control_widget.setLayout(control_layout)
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

    def initSystemParameters(self):
        self.parameters_label = QLabel('Parameters go here')
        self.grid_layout.addWidget(self.parameters_label, 1, 2)

    def initLogOutput(self):
        self.log_output = QTextEdit()
        self.grid_layout.addWidget(self.log_output, 1, 3)

    def initManualControl(self):
        self.manual_control_label = QLabel('Manual controls go here')
        self.grid_layout.addWidget(self.manual_control_label, 1, 4)


    def update_status(self, status):
        self.status_label.setText(f'Status: {status}')

    def log(self, message):
        self.log_output.append(message)

    def closeEvent(self, event): # Handling properly closing webcam when closing application.
        self.vision_system.capture.release()

if __name__ == '__main__':
    app = setup_application()

    mainWin = MainWindow()
    mainWin.show()

    app.exec()