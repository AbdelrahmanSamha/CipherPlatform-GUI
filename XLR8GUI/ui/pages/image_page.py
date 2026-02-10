from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Slot
from PIL import Image
import os


class ImagePage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        # -----------------------------
        # Prepare tmp directory
        # -----------------------------
        self.tmp_dir = "tmp"
        os.makedirs(self.tmp_dir, exist_ok=True)

        self.input_path = os.path.join(self.tmp_dir, "input.bmp")
        self.output_path = os.path.join(self.tmp_dir, "output.bmp")

        # -----------------------------
        # Title
        # -----------------------------
        title = QLabel("Image Cipher Page")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")

        # -----------------------------
        # Status
        # -----------------------------
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: green; padding: 4px;")

        # -----------------------------
        # Image previews
        # -----------------------------
        self.input_preview = QLabel("Input Image Preview")
        self.input_preview.setStyleSheet("border: 1px solid black;")
        self.input_preview.setFixedSize(256, 256)
        self.input_preview.setScaledContents(True)

        self.output_preview = QLabel("Output Image Preview")
        self.output_preview.setStyleSheet("border: 1px solid black;")
        self.output_preview.setFixedSize(256, 256)
        self.output_preview.setScaledContents(True)

        preview_layout = QHBoxLayout()
        preview_layout.addWidget(self.input_preview)
        preview_layout.addWidget(self.output_preview)

        # -----------------------------
        # Buttons
        # -----------------------------
        self.load_btn = QPushButton("Load Image")
        self.load_btn.clicked.connect(self.load_image)

        self.start_btn = QPushButton("Start Cipher")
        self.start_btn.clicked.connect(self.start_cipher)

        self.swap_btn = QPushButton("Swap I/O")
        self.swap_btn.clicked.connect(self.swap_io)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.load_btn)
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.swap_btn)

        # -----------------------------
        # Layout
        # -----------------------------
        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.status_label)
        layout.addLayout(preview_layout)
        layout.addLayout(btn_layout)
        layout.addStretch()
        self.setLayout(layout)

    # -----------------------------
    # Load input image
    # -----------------------------
    @Slot()
    def load_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.bmp *.jpg *.jpeg)"
        )
        if not path:
            return

        try:
            # Open and convert
            img = Image.open(path).convert("RGB")

            # Resize to fixed size (256x256)
            img = img.resize((256, 256))

            # Save to tmp/input.bmp
            img.save(self.input_path, format="BMP")

            # Update preview
            pixmap = QPixmap(self.input_path)
            self.input_preview.setPixmap(pixmap)

            self.status_label.setText("Loaded and prepared input.bmp")
            self.status_label.setStyleSheet("color: green; padding: 4px;")

        except Exception as e:
            self.status_label.setText(f"❌ Failed to load image: {e}")
            self.status_label.setStyleSheet("color: red; padding: 4px;")

    # -----------------------------
    # Start Cipher (encrypt/decrypt)
    # -----------------------------
    @Slot()
    def start_cipher(self):
        if not os.path.exists(self.input_path):
            self.status_label.setText("❌ No input image loaded")
            self.status_label.setStyleSheet("color: red; padding: 4px;")
            return

        self.status_label.setText("Sending image to FPGA...")
        self.status_label.setStyleSheet("color: blue; padding: 4px;")

        # Call controller
        self.controller.fpga_operation(
            op="image",
            stream_in_path=self.input_path,
            stream_out_path=self.output_path,
            stream_is_hex=False
        )

    # -----------------------------
    # Swap input/output paths
    # -----------------------------
    @Slot()
    def swap_io(self):
        if not os.path.exists(self.output_path):
            self.status_label.setText("❌ No output to swap")
            self.status_label.setStyleSheet("color: red; padding: 4px;")
            return

        # Output becomes new input
        self.input_path = self.output_path

        pixmap = QPixmap(self.input_path)
        self.input_preview.setPixmap(pixmap)

        self.status_label.setText("Swapped: output.bmp is now input")
        self.status_label.setStyleSheet("color: green; padding: 4px;")

    # -----------------------------
    # Receive processed image
    # -----------------------------
    @Slot()
    def refresh_output_preview(self):
        """
        Call this after backend writes output.bmp
        """
        if os.path.exists(self.output_path):
            pixmap = QPixmap(self.output_path)
            self.output_preview.setPixmap(pixmap)
            self.status_label.setText("Received processed image")
            self.status_label.setStyleSheet("color: green; padding: 4px;")
