from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, Signal

class SplashScreen(QWidget):
    # Signal emitted when user wants to continue
    start_requested = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("XLR8")
        self.resize(500, 300)

        # Big title
        title = QLabel("XLR8")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 48px; font-weight: bold;")

        subtitle = QLabel("FPGA Crypto Acceleration Platform")
        subtitle.setAlignment(Qt.AlignCenter)

        hint = QLabel("Press Enter to continue")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet("color: gray;")

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()
        layout.addWidget(hint)

        self.setLayout(layout)

    # Capture keyboard event
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.start_requested.emit()
            self.close()

    # Optional: clicking also continues
    def mousePressEvent(self, event):
        self.start_requested.emit()
        self.close()
