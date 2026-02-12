from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit
)
from PySide6.QtCore import Qt, Slot, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator

class UartTestPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        # -----------------------------
        # Title
        # -----------------------------
        title = QLabel("UART Single Byte Test")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")

        # -----------------------------
        # UART status
        # -----------------------------
        self.status_label = QLabel("UART Port: Not connected")
        self.status_label.setStyleSheet("color: red;")
        self.status_label.setAlignment(Qt.AlignLeft)

        # Connect signal from controller
        self.controller.uart_status_updated.connect(self.on_uart_status_update)

        # -----------------------------
        # Input for single byte
        # -----------------------------
        self.byte_input = QLineEdit()
        self.byte_input.setPlaceholderText("Enter 1 byte (hex, e.g., 0A)")
        self.byte_input.setMaxLength(2)  # max 2 hex chars

        hex_regex = QRegularExpression("^[0-9A-Fa-f]{0,2}$")
        hex_validator = QRegularExpressionValidator(hex_regex)
        self.byte_input.setValidator(hex_validator)

        # Send button
        self.send_btn = QPushButton("Send Byte")
        self.send_btn.clicked.connect(self.send_byte)

        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Byte to send:"))
        input_layout.addWidget(self.byte_input)
        input_layout.addWidget(self.send_btn)

        # -----------------------------
        # Output box (readonly)
        # -----------------------------
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setPlaceholderText("Received bytes will appear here...")

        # -----------------------------
        # Layout
        # -----------------------------
        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.status_label)
        layout.addLayout(input_layout)
        layout.addWidget(self.output_box)

        self.setLayout(layout)

        # -----------------------------
        # Connect controller signal for incoming bytes
        # -----------------------------
        self.controller.uart_test_page_received.connect(self.receive_byte)

    # -----------------------------
    # Slot: update UART status
    # -----------------------------
    @Slot(bool, str)
    def on_uart_status_update(self, status, port):
        if status:
            self.status_label.setText(f"UART Port: {port} (Open)")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText("UART Port: Not connected")
            self.status_label.setStyleSheet("color: red;")

    # -----------------------------
    # Send the byte to FPGA
    # -----------------------------
    @Slot()
    def send_byte(self):
        hex_text = self.byte_input.text().strip()
        if len(hex_text) == 0:
            self.output_box.append("❌ Enter a hex byte to send.")
            return

        # Convert hex string to byte
        try:
            byte_value = bytes.fromhex(hex_text)
        except ValueError:
            self.output_box.append("❌ Invalid hex value.")
            return

        #success = self.controller.send_bytes(byte_value)# this should be something like : self.controller.fpga_operation(op="image", img_inputpath="", img_outputpath="") and the function will do the the work of sending the data to the FPGA. 
        success = self.controller.fpga_operation(op="test", test_byte_tx = byte_value)
        if success:
            self.output_box.append(f"➡ Sent: {byte_value.hex().upper()}")
        else:
            self.output_box.append("❌ UART not open. Cannot send.")

    # -----------------------------
    # Receive byte from FPGA
    # -----------------------------
    @Slot(bytes)
    def receive_byte(self, data):
        self.output_box.append(f"⬅ Received: {data.hex().upper()}")
