from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtCore import Qt

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
        self.btn_close.setIcon(QIcon('GUI/Icons/cross_icon.png')) 

        # Minimize Button
        self.btn_min = QPushButton('')
        self.btn_min.clicked.connect(self.btn_min_clicked)
        self.btn_min.setFixedSize(btn_size, btn_size)
        self.btn_min.setIcon(QIcon('GUI/Icons/minimize_icon.png'))  

        # Maximize/Restore Button
        self.btn_max = QPushButton('')
        self.btn_max.clicked.connect(self.btn_max_clicked)
        self.btn_max.setFixedSize(btn_size, btn_size)
        self.btn_max.setIcon(QIcon('GUI/Icons/Maximize_icon.png')) 

        self.max_icon = QIcon('GUI/Icons/Maximize_icon.png')
        self.restore_icon = QIcon('GUI/Icons/Restore_down_icon.png') 
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