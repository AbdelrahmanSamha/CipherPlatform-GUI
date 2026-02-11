from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit,
    QLineEdit, QRadioButton, QButtonGroup,
    QFileDialog, QGroupBox
)
from PySide6.QtCore import Slot


class Sha256Page(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        # =========================================================
        # Title
        # =========================================================
        title = QLabel("SHA-256 Hash")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")

        # =========================================================
        # Status
        # =========================================================
        self.status_label = QLabel("Idle")
        self.status_label.setStyleSheet("color: gray; padding: 4px;")

        # Listen for FPGA hash result
        self.controller.uart_sha_page_received.connect(
            self.on_hash_received
        )

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
        # INPUT DATA TYPE
        # =========================================================
        self.hex_type_radio = QRadioButton("Hex Input")
        self.ascii_type_radio = QRadioButton("ASCII Input")
        self.ascii_type_radio.setChecked(True)

        self.data_type_group = QButtonGroup(self)
        self.data_type_group.addButton(self.hex_type_radio)
        self.data_type_group.addButton(self.ascii_type_radio)

        data_type_row = QHBoxLayout()
        data_type_row.addWidget(QLabel("Input Type:"))
        data_type_row.addWidget(self.hex_type_radio)
        data_type_row.addWidget(self.ascii_type_radio)
        data_type_row.addStretch()

        # =========================================================
        # OUTPUT DATA TYPE
        # =========================================================
        self.hex_out_radio = QRadioButton("Hex Output")
        self.ascii_out_radio = QRadioButton("ASCII Output")
        self.hex_out_radio.setChecked(True)

        self.output_type_group = QButtonGroup(self)
        self.output_type_group.addButton(self.hex_out_radio)
        self.output_type_group.addButton(self.ascii_out_radio)

        output_type_row = QHBoxLayout()
        output_type_row.addWidget(QLabel("Output Type:"))
        output_type_row.addWidget(self.hex_out_radio)
        output_type_row.addWidget(self.ascii_out_radio)
        output_type_row.addStretch()

        # =========================================================
        # TEXT MODE widgets
        # =========================================================
        self.text_group = QGroupBox("Text Hashing")

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            "Enter text to hash"
        )

        text_layout = QVBoxLayout()
        text_layout.addWidget(QLabel("Input"))
        text_layout.addWidget(self.text_input)

        self.text_group.setLayout(text_layout)

        # =========================================================
        # FILE MODE widgets
        # =========================================================
        self.file_group = QGroupBox("File Hashing")
        self.file_group.setVisible(False)

        self.input_path = QLineEdit()
        self.input_path.setReadOnly(True)

        browse_in_btn = QPushButton("Browse Input File")
        browse_in_btn.clicked.connect(self.browse_input_file)

        file_layout = QVBoxLayout()

        in_row = QHBoxLayout()
        in_row.addWidget(self.input_path)
        in_row.addWidget(browse_in_btn)

        file_layout.addWidget(QLabel("Input File"))
        file_layout.addLayout(in_row)

        self.file_group.setLayout(file_layout)

        # =========================================================
        # RESULTS (FIXED ON SCREEN)
        # =========================================================
        results_group = QGroupBox("Results")

        # FPGA output
        self.fpga_hash_output = QLineEdit()
        self.fpga_hash_output.setReadOnly(True)
        self.fpga_hash_output.setPlaceholderText(
            "FPGA hash result"
        )

        # Software output
        self.sw_hash_output = QLineEdit()
        self.sw_hash_output.setReadOnly(True)
        self.sw_hash_output.setPlaceholderText(
            "Software hash result"
        )

        # Comparison label
        self.compare_label = QLabel("")
        self.compare_label.setStyleSheet("font-weight: bold;")

        results_layout = QVBoxLayout()
        results_layout.addWidget(QLabel("FPGA SHA-256 Result"))
        results_layout.addWidget(self.fpga_hash_output)

        results_layout.addWidget(QLabel("Software SHA-256 Result"))
        results_layout.addWidget(self.sw_hash_output)

        results_layout.addWidget(self.compare_label)

        results_group.setLayout(results_layout)

        # =========================================================
        # Control buttons
        # =========================================================
        start_fpga_btn = QPushButton("Start FPGA Hash")
        start_sw_btn = QPushButton("Start Software Hash")

        start_fpga_btn.clicked.connect(self.start_hash_fpga)
        start_sw_btn.clicked.connect(self.start_hash_software)

        btn_row = QHBoxLayout()
        btn_row.addWidget(start_fpga_btn)
        btn_row.addWidget(start_sw_btn)

        # =========================================================
        # Main layout
        # =========================================================
        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.status_label)

        layout.addLayout(mode_row)
        layout.addLayout(data_type_row)
        layout.addLayout(output_type_row)

        layout.addWidget(self.text_group)
        layout.addWidget(self.file_group)

        layout.addWidget(results_group)

        layout.addLayout(btn_row)
        layout.addStretch()

        self.setLayout(layout)

    # =============================================================
    # UI logic
    # =============================================================
    def update_input_mode(self):
        text_mode = self.text_mode_radio.isChecked()
        self.text_group.setVisible(text_mode)
        self.file_group.setVisible(not text_mode)

    # =============================================================
    # File dialog
    # =============================================================
    def browse_input_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Input File")
        if path:
            self.input_path.setText(path)

    # =============================================================
    # FPGA HASH
    # =============================================================
    def start_hash_fpga(self):
        self.compare_label.setText("")
        self.fpga_hash_output.clear()

        if self.text_mode_radio.isChecked():
            data = self.text_input.toPlainText()
            in_path = None

            if not data:
                self.status_label.setText("❌ No input text provided")
                self.status_label.setStyleSheet("color: red;")
                return

            self.status_label.setText("🔄 FPGA hashing text...")
            self.status_label.setStyleSheet("color: blue;")

        else:
            data = None
            in_path = self.input_path.text()

            if not in_path:
                self.status_label.setText("❌ Input file not selected")
                self.status_label.setStyleSheet("color: red;")
                return

            self.status_label.setText("🔄 FPGA hashing file...")
            self.status_label.setStyleSheet("color: blue;")

        is_hex = self.hex_type_radio.isChecked()
        out_hex = self.hex_out_radio.isChecked()

        self.controller.fpga_operation(
            op="sha256",
            sha_text=data,
            sha_in_path=in_path,
            sha_is_hex=is_hex,
        )
        self.controller.sha_outhex = out_hex

    # =============================================================
    # SOFTWARE HASH
    # =============================================================
    def start_hash_software(self):
        self.compare_label.setText("")
        self.sw_hash_output.clear()

        if self.text_mode_radio.isChecked():
            data = self.text_input.toPlainText()
            in_path = None

            if not data:
                self.status_label.setText("❌ No input text provided")
                self.status_label.setStyleSheet("color: red;")
                return

        else:
            data = None
            in_path = self.input_path.text()

            if not in_path:
                self.status_label.setText("❌ Input file not selected")
                self.status_label.setStyleSheet("color: red;")
                return

        is_hex = self.hex_type_radio.isChecked()
        out_hex = self.hex_out_radio.isChecked()

        self.status_label.setText("🔄 Software hashing...")
        self.status_label.setStyleSheet("color: blue;")

        result = self.controller.software_operation(
            op="sha256",
            sha_text=data,
            sha_in_path=in_path,
            sha_is_hex=is_hex,
            sha_out_hex=out_hex
        )

        # Choose output based on UI selection
        if out_hex:
            self.sw_hash_output.setText(result["hash_hex"])
        else:
            self.sw_hash_output.setText(result["hash_out"])

        self.compare_results()

        self.status_label.setText("✅ Software hash complete")
        self.status_label.setStyleSheet("color: green;")

    # =============================================================
    # Receive FPGA hash result
    # =============================================================
    @Slot(bytes)
    def on_hash_received(self, data: bytes):
        if self.ascii_out_radio.isChecked():
            try:
                text = data.decode("utf-8", errors="replace")
            except:
                text = str(data)
        else:
            text = data.hex().upper()

        self.fpga_hash_output.setText(text)

        self.compare_results()

        self.status_label.setText("✅ FPGA hash complete")
        self.status_label.setStyleSheet("color: green;")

    # =============================================================
    # Compare results
    # =============================================================
    def compare_results(self):
        fpga = self.fpga_hash_output.text()
        sw = self.sw_hash_output.text()

        if not fpga or not sw:
            return

        if fpga == sw:
            self.compare_label.setText("✅ Results match")
            self.compare_label.setStyleSheet(
                "color: green; font-weight: bold;"
            )
        else:
            self.compare_label.setText("❌ Results DO NOT match")
            self.compare_label.setStyleSheet(
                "color: red; font-weight: bold;"
            )
