from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit,
    QLineEdit, QRadioButton, QButtonGroup,
    QFileDialog, QProgressBar, QGroupBox
)
from PySide6.QtCore import Slot


class StreamPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        # =========================================================
        # Title
        # =========================================================
        title = QLabel("Streaming Cipher")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")

        # =========================================================
        # Configuration display (top)
        # =========================================================
        self.config_label = QLabel(
            "Mode: None | Operation: None | Key Size: None | Key: None"
        )
        self.config_label.setStyleSheet(
            "font-family: monospace; padding: 6px;"
        )

        self.status_label = QLabel("Idle")
        self.status_label.setStyleSheet("color: gray; padding: 4px;")

        # Listen for config updates
        self.controller.config_updated.connect(self.on_config_update)
        #listen for new data over UART
        self.controller.uart_stream_page_received.connect(self.on_stream_data_received)
        # =========================================================
        # Input mode selection
        # =========================================================
        self.text_mode_radio = QRadioButton("Text Input")
        self.file_mode_radio = QRadioButton("File Input")
        self.text_mode_radio.setChecked(True)

        self.input_mode_group = QButtonGroup(self)
        self.input_mode_group.addButton(self.text_mode_radio)
        self.input_mode_group.addButton(self.file_mode_radio)

        self.text_mode_radio.toggled.connect(self.update_input_mode)

        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Input Mode:"))
        mode_row.addWidget(self.text_mode_radio)
        mode_row.addWidget(self.file_mode_radio)
        mode_row.addStretch()

        # =========================================================
        # HEX OR ASCII INPUT 
        # =========================================================
        self.hex_type_radio = QRadioButton("Hex Inpurt")
        self.ascii_type_radio=QRadioButton("ASCII input")
        self.hex_type_radio.setChecked(True)

        self.data_type_group = QButtonGroup(self)
        self.data_type_group.addButton(self.hex_type_radio)
        self.data_type_group.addButton(self.ascii_type_radio)

        data_type_row = QHBoxLayout()
        data_type_row.addWidget(QLabel("Data Type:"))
        data_type_row.addWidget(self.hex_type_radio)
        data_type_row.addWidget(self.ascii_type_radio)
        data_type_row.addStretch()

        # =========================================================
        # TEXT MODE widgets
        # =========================================================
        self.text_group = QGroupBox("Text Streaming")

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            "Enter plaintext / ciphertext here (hex)"
        )

        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setPlaceholderText(
            "Output will appear here (limited size)"
        )

        text_layout = QVBoxLayout()
        text_layout.addWidget(QLabel("Input"))
        text_layout.addWidget(self.text_input)
        text_layout.addWidget(QLabel("Output"))
        text_layout.addWidget(self.text_output)

        self.text_group.setLayout(text_layout)

        # =========================================================
        # FILE MODE widgets
        # =========================================================
        self.file_group = QGroupBox("File Streaming")
        self.file_group.setVisible(False)

        self.input_path = QLineEdit()
        self.input_path.setReadOnly(True)

        self.output_path = QLineEdit()
        self.output_path.setReadOnly(True)

        browse_in_btn = QPushButton("Browse Input File")
        browse_out_btn = QPushButton("Browse Output File")

        browse_in_btn.clicked.connect(self.browse_input_file)
        browse_out_btn.clicked.connect(self.browse_output_file)

        file_layout = QVBoxLayout()

        in_row = QHBoxLayout()
        in_row.addWidget(self.input_path)
        in_row.addWidget(browse_in_btn)

        out_row = QHBoxLayout()
        out_row.addWidget(self.output_path)
        out_row.addWidget(browse_out_btn)

        file_layout.addWidget(QLabel("Input File"))
        file_layout.addLayout(in_row)
        file_layout.addWidget(QLabel("Output File"))
        file_layout.addLayout(out_row)

        self.file_group.setLayout(file_layout)

        # =========================================================
        # Progress / control
        # =========================================================
        self.progress = QProgressBar()
        self.progress.setValue(0)

        start_btn = QPushButton("Start Streaming")
        cancel_btn = QPushButton("Cancel")

        start_btn.clicked.connect(self.start_stream)
        cancel_btn.clicked.connect(self.cancel_stream)

        btn_row = QHBoxLayout()
        btn_row.addWidget(start_btn)
        btn_row.addWidget(cancel_btn)

        # =========================================================
        # Main layout
        # =========================================================
        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.config_label)
        layout.addWidget(self.status_label)

        layout.addLayout(mode_row)
        layout.addLayout(data_type_row)
        layout.addWidget(self.text_group)
        layout.addWidget(self.file_group)

        layout.addWidget(self.progress)
        layout.addLayout(btn_row)

        layout.addStretch()
        self.setLayout(layout)

    # =============================================================
    # UI logic
    # =============================================================
    def update_input_mode(self):
        """
        Show / hide widgets based on input mode
        """
        text_mode = self.text_mode_radio.isChecked()
        self.text_group.setVisible(text_mode)
        self.file_group.setVisible(not text_mode)

    # =============================================================
    # File dialogs
    # =============================================================
    def browse_input_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Input File")
        if path:
            self.input_path.setText(path)

    def browse_output_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Select Output File")
        if path:
            self.output_path.setText(path)

    # =============================================================
    # Streaming control
    # =============================================================
    def start_stream(self):
        if self.text_mode_radio.isChecked():
            data = self.text_input.toPlainText()
            in_path = None
            out_path = None
            if not data:
                self.status_label.setText("❌ No input text provided")
                self.status_label.setStyleSheet("color: red;")
                return

            self.status_label.setText("🔄 Streaming text...")
            self.status_label.setStyleSheet("color: blue;")



        else:
            data = None
            in_path = self.input_path.text()
            out_path = self.output_path.text()

            if not in_path or not out_path:
                self.status_label.setText("❌ Input/output file not selected")
                self.status_label.setStyleSheet("color: red;")
                return

            self.status_label.setText("🔄 Streaming file...")
            self.status_label.setStyleSheet("color: blue;")

        if self.hex_type_radio.isChecked(): 
            is_hex = True
        else: 
            is_hex = False


        
        self.controller.fpga_operation(op="stream", stream_text=data, stream_in_path=in_path, stream_out_path=out_path, stream_is_hex=is_hex)

    def cancel_stream(self):
        self.status_label.setText("⛔ Streaming cancelled")
        self.status_label.setStyleSheet("color: orange;")

        # Placeholder
        # self.controller.cancel_stream()

    # =============================================================
    # Configuration update
    # =============================================================
    def on_config_update(self, config):
        if config["direction"] == "enc":
            op = "Encryption"
        else:
            op = "Decryption"

        self.config_label.setText(
            f"Mode: {config['mode']} | "
            f"Operation: {op} | "
            f"Key Size: {config['key_size']} | "
            f"Key: {config['key']}"
        )

        self.status_label.setText("✅ Config updated")
        self.status_label.setStyleSheet("color: green;")


    @Slot(bytes)
    def on_stream_data_received(self, data: bytes):
        if self.hex_type_radio.isChecked():
            text = data.hex()
        else:
            try:
                text = data.decode("utf-8", errors="replace")
            except:
                text = str(data)

        self.text_output.setPlainText(text)