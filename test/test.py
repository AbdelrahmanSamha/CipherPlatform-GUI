# main.py
# ============================================================
# FPGA Cryptographic Platform - GUI Skeleton
# Single-file, readable, extensible
# ============================================================

from PySide6.QtWidgets import (
    QApplication, QWidget,
    QPushButton, QLabel, QTextEdit,
    QVBoxLayout, QHBoxLayout,
    QStackedWidget, QGroupBox
)
from PySide6.QtCore import Qt
import time


class CryptoGUI(QWidget):
    def __init__(self):
        super().__init__()

        # -----------------------------
        # Window setup
        # -----------------------------
        self.setWindowTitle("FPGA Cryptographic Platform")
        self.resize(1000, 600)

        # -----------------------------
        # Application state (placeholders)
        # -----------------------------
        self.fpga_connected = False
        self.active_key = None

        # -----------------------------
        # Main layout (sidebar + pages)
        # -----------------------------
        main_layout = QHBoxLayout(self)

        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)

        self.pages = QStackedWidget()
        main_layout.addWidget(self.pages, stretch=1)

        # Add pages to stacked widget
        self.pages.addWidget(self.create_block_lab_page())   # index 0
        self.pages.addWidget(self.create_full_block_page())  # index 1
        self.pages.addWidget(self.create_streaming_page())   # index 2

    # ============================================================
    # Sidebar (Navigation)
    # ============================================================
    def create_sidebar(self):
        box = QGroupBox("Navigation")
        layout = QVBoxLayout()

        btn_block_lab = QPushButton("Block Cipher Lab")
        btn_full_block = QPushButton("Full Block Result")
        btn_streaming = QPushButton("Streaming Cipher")

        btn_block_lab.clicked.connect(lambda: self.pages.setCurrentIndex(0))
        btn_full_block.clicked.connect(lambda: self.pages.setCurrentIndex(1))
        btn_streaming.clicked.connect(lambda: self.pages.setCurrentIndex(2))

        layout.addWidget(btn_block_lab)
        layout.addWidget(btn_full_block)
        layout.addWidget(btn_streaming)
        layout.addStretch()

        box.setLayout(layout)
        box.setFixedWidth(200)
        return box

    # ============================================================
    # Page 1: Block Cipher Lab (step / pause per block or round)
    # ============================================================
    def create_block_lab_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("Block Cipher Lab (Step-by-Step)")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self.block_input = QTextEdit()
        self.block_input.setPlaceholderText("Enter plaintext block (hex)")
        layout.addWidget(self.block_input)

        self.block_output = QTextEdit()
        self.block_output.setReadOnly(True)
        self.block_output.setPlaceholderText("Intermediate / round output")
        layout.addWidget(self.block_output)

        btn_step = QPushButton("Next Block / Round")
        btn_step.clicked.connect(self.block_lab_step)
        layout.addWidget(btn_step)

        self.block_status = QLabel("Status: Idle")
        layout.addWidget(self.block_status)

        layout.addStretch()
        return page

    def block_lab_step(self):
        """
        PLACEHOLDER:
        - Send one block / round command to FPGA
        - FPGA pauses internally
        - Receive intermediate AES state
        """
        start_time = time.time()

        # TODO: FPGA UART send/receive here
        time.sleep(0.1)  # simulate hardware delay
        received_state = "DEADBEEF (placeholder)"

        elapsed = time.time() - start_time

        self.block_output.append(received_state)
        self.block_status.setText(f"Last step time: {elapsed:.3f}s")

    # ============================================================
    # Page 2: Full Block Result (one-shot encryption/decryption)
    # ============================================================
    def create_full_block_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("Full Block Encryption / Decryption")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self.full_input = QTextEdit()
        self.full_input.setPlaceholderText("Enter plaintext block (hex)")
        layout.addWidget(self.full_input)

        btn_encrypt = QPushButton("Encrypt Full Block")
        btn_encrypt.clicked.connect(self.full_block_encrypt)
        layout.addWidget(btn_encrypt)

        self.full_output = QTextEdit()
        self.full_output.setReadOnly(True)
        self.full_output.setPlaceholderText("Ciphertext output")
        layout.addWidget(self.full_output)

        self.full_status = QLabel("Status: Idle")
        layout.addWidget(self.full_status)

        layout.addStretch()
        return page

    def full_block_encrypt(self):
        """
        PLACEHOLDER:
        - Send entire block to FPGA
        - Receive final ciphertext
        - Measure latency
        """
        start_time = time.time()

        # TODO: FPGA full-block encryption
        time.sleep(0.2)  # simulate hardware delay
        ciphertext = "CAFEBABE (placeholder)"

        elapsed = time.time() - start_time

        self.full_output.setText(ciphertext)
        self.full_status.setText(f"Encryption time: {elapsed:.3f}s")

    # ============================================================
    # Page 3: Streaming Cipher
    # ============================================================
    def create_streaming_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("Streaming Cipher Mode")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        btn_start = QPushButton("Start Streaming")
        btn_stop = QPushButton("Stop Streaming")

        btn_start.clicked.connect(self.start_streaming)
        btn_stop.clicked.connect(self.stop_streaming)

        layout.addWidget(btn_start)
        layout.addWidget(btn_stop)

        self.stream_log = QTextEdit()
        self.stream_log.setReadOnly(True)
        self.stream_log.setPlaceholderText("Streaming log")
        layout.addWidget(self.stream_log)

        self.stream_status = QLabel("Status: Stopped")
        layout.addWidget(self.stream_status)

        layout.addStretch()
        return page

    def start_streaming(self):
        """
        PLACEHOLDER:
        - Start continuous data transfer
        - Measure throughput
        """
        self.stream_status.setText("Status: Streaming...")
        self.stream_log.append("Streaming started")

        # TODO: FPGA stream start

    def stop_streaming(self):
        self.stream_status.setText("Status: Stopped")
        self.stream_log.append("Streaming stopped")

        # TODO: FPGA stream stop


# ============================================================
# Application entry point
# ============================================================
if __name__ == "__main__":
    app = QApplication([])
    window = CryptoGUI()
    window.show()
    app.exec()
