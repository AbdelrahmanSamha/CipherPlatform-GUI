import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QTextEdit, QVBoxLayout, QHBoxLayout, QGridLayout
)

class LayoutDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Layout Control Demo")
        self.resize(500, 350)

        # Widgets
        self.encrypt_btn = QPushButton("Encrypt")
        self.reset_btn = QPushButton("Reset")
        self.status = QLabel("Idle")
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        # Signals
        self.encrypt_btn.clicked.connect(self.encrypt)
        self.reset_btn.clicked.connect(self.reset)

        # --- Top button row ---
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.encrypt_btn)
        top_layout.addWidget(self.reset_btn)
        top_layout.addStretch()  # push buttons left

        # --- Status bar ---
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        status_layout.addWidget(self.status)
        status_layout.addStretch()

        # --- Main layout ---
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(status_layout)
        main_layout.addWidget(self.output)

        self.setLayout(main_layout)

    def encrypt(self):
        self.status.setText("Encrypting...")
        self.output.append("Encrypt command sent")

    def reset(self):
        self.status.setText("Idle")
        self.output.append("Reset issued")

app = QApplication(sys.argv)
window = LayoutDemo()
window.show()
sys.exit(app.exec())
