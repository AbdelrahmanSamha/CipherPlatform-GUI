from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Signal

class Sidebar(QWidget):
    page_selected = Signal(str)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        config_btn = QPushButton("Configuration")
        block_btn = QPushButton("Block Lab Cipher")
        stream_btn = QPushButton("Stream Cipher")
        rng_btn = QPushButton("RNG")
        image_btn = QPushButton("Image Cipher")
        metrics_btn = QPushButton("Metrics")
        test_btn = QPushButton("Test")

        config_btn.clicked.connect(lambda: self.page_selected.emit("config"))
        block_btn.clicked.connect(lambda: self.page_selected.emit("block"))
        stream_btn.clicked.connect(lambda: self.page_selected.emit("stream"))
        rng_btn.clicked.connect(lambda: self.page_selected.emit("rng"))
        metrics_btn.clicked.connect(lambda: self.page_selected.emit("metrics"))
        image_btn.clicked.connect(lambda: self.page_selected.emit("image"))
        test_btn.clicked.connect(lambda: self.page_selected.emit("test"))

        layout.addWidget(config_btn)
        layout.addWidget(block_btn)
        layout.addWidget(stream_btn)
        layout.addWidget(rng_btn)
        layout.addWidget(image_btn)
        layout.addWidget(metrics_btn)
        layout.addWidget(test_btn)
        layout.addStretch()

        self.setLayout(layout)
