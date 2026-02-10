from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox,
    QLineEdit, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator

import serial.tools.list_ports


class ConfigPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.controller.config_updated.connect(self.update_stored_config)
        self.controller.uart_status_updated.connect(self.update_uart_status)

        # =====================================================
        # MAIN LAYOUT
        # =====================================================
        layout = QVBoxLayout(self)

        # =====================================================
        # TITLE
        # =====================================================
        title = QLabel("CIPHER Configuration")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # =====================================================
        # MODE SELECTION
        # =====================================================
        layout.addWidget(QLabel("Mode of Operation"))
        self.mode_box = QComboBox()
        self.mode_box.addItems(["ECB", "CBC", "CFB", "OFB", "CTR"])
        self.mode_box.currentTextChanged.connect(self.mode_changed)
        layout.addWidget(self.mode_box)

        # =====================================================
        # OPERATION (ENC / DEC)
        # =====================================================
        self.encrypt_radio = QRadioButton("Encrypt")
        self.decrypt_radio = QRadioButton("Decrypt")
        self.encrypt_radio.setChecked(True)

        direction_group = QButtonGroup(self)
        direction_group.addButton(self.encrypt_radio)
        direction_group.addButton(self.decrypt_radio)

        op_layout = QHBoxLayout()
        op_layout.addWidget(QLabel("Operation:"))
        op_layout.addWidget(self.encrypt_radio)
        op_layout.addWidget(self.decrypt_radio)
        op_layout.addStretch()
        layout.addLayout(op_layout)

        # =====================================================
        # KEY SIZE
        # =====================================================
        layout.addWidget(QLabel("Key Size (bits)"))
        self.key_size_box = QComboBox()
        self.key_size_box.addItems(["128", "192", "256"])
        layout.addWidget(self.key_size_box)

        # =====================================================
        # KEY INPUT
        # =====================================================
        layout.addWidget(QLabel("Key (hex)"))
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Enter key in hex")

        hex_regex = QRegularExpression("^[0-9A-Fa-f]*$")
        self.key_input.setValidator(QRegularExpressionValidator(hex_regex))
        layout.addWidget(self.key_input)

        # =====================================================
        # IV / NONCE
        # =====================================================
        self.iv_input = QLineEdit()
        self.iv_input.setPlaceholderText("Enter IV / Counter in hex")
        layout.addWidget(self.iv_input)
        self.iv_input.setVisible(False)

        # =====================================================
        # STATUS / FEEDBACK
        # =====================================================
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # =====================================================
        # STORED CONFIG DISPLAY
        # =====================================================
        self.stored_mode = QLabel("Mode: None")
        self.stored_key_size = QLabel("Key Size: None")
        self.stored_key = QLabel("Key: None")
        self.stored_direction = QLabel("Operation: Encryption")
        self.stored_iv = QLabel("IV / Nonce: None")

        for lbl in (
            self.stored_mode, self.stored_key_size,
            self.stored_key, self.stored_direction, self.stored_iv
        ):
            lbl.setStyleSheet("font-family: monospace;")

        layout.addWidget(self.stored_mode)
        layout.addWidget(self.stored_key_size)
        layout.addWidget(self.stored_key)
        layout.addWidget(self.stored_direction)
        layout.addWidget(self.stored_iv)

        # =====================================================
        # CONFIG BUTTONS
        # =====================================================
        btn_row = QHBoxLayout()
        store_btn = QPushButton("Store Configuration")
        reset_btn = QPushButton("Reset FPGA")
        btn_row.addWidget(store_btn)
        btn_row.addWidget(reset_btn)
        layout.addLayout(btn_row)

        store_btn.clicked.connect(self.store)
        reset_btn.clicked.connect(self.controller.reset_fpga)

        # =====================================================
        # SEPARATOR SPACE
        # =====================================================
        layout.addStretch()

        # =====================================================
        # UART SECTION
        # =====================================================
        uart_title = QLabel("UART Configuration")
        uart_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(uart_title)

        # --- Port selection
        port_row = QHBoxLayout()
        self.port_combo = QComboBox()
        self.refresh_ports()
        refresh_btn = QPushButton("Refresh")
        port_row.addWidget(QLabel("COM Port:"))
        port_row.addWidget(self.port_combo)
        port_row.addWidget(refresh_btn)
        layout.addLayout(port_row)

        refresh_btn.clicked.connect(self.refresh_ports)

        # --- Baudrate
        baud_row = QHBoxLayout()
        self.baud_edit = QLineEdit("1000000")
        self.baud_edit.setReadOnly(True)
        baud_row.addWidget(QLabel("Baud Rate:"))
        baud_row.addWidget(self.baud_edit)
        layout.addLayout(baud_row)

        # --- UART status
        self.uart_status = QLabel("🔴 UART: Disconnected")
        layout.addWidget(self.uart_status)

        # --- UART buttons
        uart_btns = QHBoxLayout()
        self.connect_btn = QPushButton("Connect UART")
        self.disconnect_btn = QPushButton("Disconnect UART")
        self.disconnect_btn.setEnabled(False)

        uart_btns.addWidget(self.connect_btn)
        uart_btns.addWidget(self.disconnect_btn)
        layout.addLayout(uart_btns)

        self.connect_btn.clicked.connect(self.connect_uart)
        self.disconnect_btn.clicked.connect(self.disconnect_uart)

        # =====================================================
        # VALIDATION SIGNALS
        # =====================================================
        self.key_input.textChanged.connect(self.validate_key_length)
        self.iv_input.textChanged.connect(self.validate_iv_length)
        self.key_size_box.currentTextChanged.connect(self.validate_key_length)

    # =====================================================
    # MODE HANDLING
    # =====================================================
    def mode_changed(self, mode):
        self.iv_input.setVisible(mode != "ECB")
        self.validate_iv_length()

    # =====================================================
    # STORE CONFIG
    # =====================================================
    def store(self):
        if not self.key_input.text():
            self.show_error("Key is empty")
            return

        if "red" in self.key_input.styleSheet():
            self.show_error("Key length mismatch")
            return

        if self.iv_input.isVisible():
            if not self.iv_input.text():
                self.show_error("IV / Nonce is empty")
                return
            if "red" in self.iv_input.styleSheet():
                self.show_error("IV / Nonce must be 128 bits")
                return

        config = {
            "mode": self.mode_box.currentText(),
            "key_size": int(self.key_size_box.currentText()),
            "key": self.key_input.text(),
            "iv": self.iv_input.text() if self.iv_input.isVisible() else None,
            "direction": "enc" if self.encrypt_radio.isChecked() else "dec"
        }

        self.controller.set_config(config)
        self.show_success("Configuration stored")

    # =====================================================
    # VALIDATION
    # =====================================================
    def validate_key_length(self):
        req = int(self.key_size_box.currentText()) // 4
        self._validate_len(self.key_input, req)

    def validate_iv_length(self):
        if not self.iv_input.isVisible():
            self.iv_input.setStyleSheet("")
            return
        self._validate_len(self.iv_input, 32)

    def _validate_len(self, widget, req):
        if not widget.text():
            widget.setStyleSheet("")
        elif len(widget.text()) == req:
            widget.setStyleSheet("border: 2px solid green;")
        else:
            widget.setStyleSheet("border: 2px solid red;")

    # =====================================================
    # UART
    # =====================================================
    def refresh_ports(self):
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        if not ports:
            self.port_combo.addItem("No ports found")
            self.port_combo.setEnabled(False)
        else:
            self.port_combo.setEnabled(True)
            for p in ports:
                self.port_combo.addItem(p.device)

    def connect_uart(self):
        port = self.port_combo.currentText()
        self.controller.open_uart(port)

    def disconnect_uart(self):
        self.controller.close_uart()

    def update_uart_status(self, connected, port=None):
        if connected:
            self.uart_status.setText(f"🟢 UART: Connected ({port})")
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
        else:
            self.uart_status.setText("🔴 UART: Disconnected")
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(False)

    # =====================================================
    # FEEDBACK
    # =====================================================
    def show_error(self, msg):
        self.status_label.setText("❌ " + msg)
        self.status_label.setStyleSheet("color: red;")

    def show_success(self, msg):
        self.status_label.setText("✅ " + msg)
        self.status_label.setStyleSheet("color: green;")

    def update_stored_config(self, cfg):
        self.stored_mode.setText(f"Mode: {cfg['mode']}")
        self.stored_key_size.setText(f"Key Size: {cfg['key_size']} bits")
        self.stored_key.setText(f"Key: {cfg['key']}")
        self.stored_direction.setText(
            "Operation: Encryption" if cfg["direction"] == "enc" else "Operation: Decryption"
        )
        self.stored_iv.setText(
            f"IV / Nonce: {cfg['iv']}" if cfg["iv"] else "IV / Nonce: Not used"
        )
