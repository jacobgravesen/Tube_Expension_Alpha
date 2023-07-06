from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QTextEdit
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QWidget, QSizePolicy, QSpacerItem
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtCore import Qt, QPoint

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

        # New code. 
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

    def mouseMoveEvent(self, event):
        x = event.x()
        y = event.y()

        if self.m_mouse_down:
            parent = self.parent()
            parent.move(parent.x() + x - self.m_old_pos.x(), parent.y() + y - self.m_old_pos.y())

    def mouseReleaseEvent(self, event):
        m_mouse_down = False

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

    def initUI(self):
        # Set window properties
        self.setWindowTitle('Tube Expansion Alpha')
        self.setGeometry(100, 100, 800, 600)  # Position and size

        # Define a central widget (required by QMainWindow)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Define a layout (widgets will be added to this layout)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Sets Custom Titlebar
        title_bar = CustomTitleBar(self)
        self.setMenuWidget(title_bar)  # Set the custom title bar

        # Add Start/Stop Controls
        self.start_button = QPushButton('Start', self)
        self.stop_button = QPushButton('Stop', self)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)

        # Add Status Information
        self.status_label = QLabel('Status: idle')
        self.layout.addWidget(self.status_label)

        # Add Camera Feed Display (placeholder)
        self.camera_label = QLabel('Camera feed goes here')
        self.layout.addWidget(self.camera_label)

        # Add System Parameters (placeholder)
        self.parameters_label = QLabel('Parameters go here')
        self.layout.addWidget(self.parameters_label)

        # Add Log Output
        self.log_output = QTextEdit()
        self.layout.addWidget(self.log_output)

        # Add Manual Control (placeholder)
        self.manual_control_label = QLabel('Manual controls go here')
        self.layout.addWidget(self.manual_control_label)

    def update_status(self, status):
        self.status_label.setText(f'Status: {status}')

    def log(self, message):
        self.log_output.append(message)

if __name__ == '__main__':
    app = QApplication([])


    # Apply dark theme
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

    mainWin = MainWindow()
    mainWin.show()

    app.exec()
