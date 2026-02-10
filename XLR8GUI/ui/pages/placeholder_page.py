from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt

class PlaceholderPage(QWidget):
    def __init__(self, name):
        super().__init__()

        label = QLabel(f"{name}\n(Under Construction)")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 18px; color: gray;")

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(label)
        layout.addStretch()

        self.setLayout(layout)
