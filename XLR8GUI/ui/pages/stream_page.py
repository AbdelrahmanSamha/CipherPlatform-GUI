from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit,
    QLineEdit, QRadioButton, QButtonGroup,
    QFileDialog, QProgressBar, QGroupBox,
    QScrollArea
)
from PySide6.QtCore import Slot
import os


class StreamPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        # Create main widget and layout for scroll area
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

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
        # Listen for new data over UART
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
        self.hex_type_radio = QRadioButton("Hex Input")
        self.ascii_type_radio = QRadioButton("ASCII Input")
        self.hex_type_radio.setChecked(True)

        self.data_type_group = QButtonGroup(self)
        self.data_type_group.addButton(self.hex_type_radio)
        self.data_type_group.addButton(self.ascii_type_radio)

        data_type_row = QHBoxLayout()
        data_type_row.addWidget(QLabel("Input Type:"))
        data_type_row.addWidget(self.hex_type_radio)
        data_type_row.addWidget(self.ascii_type_radio)
        data_type_row.addStretch()

        # =========================================================
        # OUTPUT FORMAT SELECTION
        # =========================================================
        self.output_hex_radio = QRadioButton("Hex Output")
        self.output_ascii_radio = QRadioButton("ASCII Output")
        self.output_hex_radio.setChecked(True)

        self.output_format_group = QButtonGroup(self)
        self.output_format_group.addButton(self.output_hex_radio)
        self.output_format_group.addButton(self.output_ascii_radio)

        output_format_row = QHBoxLayout()
        output_format_row.addWidget(QLabel("Output Type:"))
        output_format_row.addWidget(self.output_hex_radio)
        output_format_row.addWidget(self.output_ascii_radio)
        output_format_row.addStretch()

        # =========================================================
        # TEXT MODE widgets (INPUT ONLY)
        # =========================================================
        self.text_group = QGroupBox("Text Input")

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            "Enter plaintext / ciphertext here"
        )
        self.text_input.setMaximumHeight(150)  # Limit height

        text_layout = QVBoxLayout()
        text_layout.addWidget(QLabel("Input Text"))
        text_layout.addWidget(self.text_input)

        self.text_group.setLayout(text_layout)

        # =========================================================
        # FILE MODE widgets (INPUT ONLY)
        # =========================================================
        self.file_group = QGroupBox("File Input")
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
        # DUAL OUTPUT BOXES
        # =========================================================
        outputs_container = QHBoxLayout()

        # FPGA Output Box
        fpga_output_group = QGroupBox("FPGA Output")
        self.fpga_output = QTextEdit()
        self.fpga_output.setReadOnly(True)
        self.fpga_output.setPlaceholderText("FPGA output will appear here")
        self.fpga_output.setMaximumHeight(200)  # Limit height
        
        fpga_layout = QVBoxLayout()
        fpga_layout.addWidget(self.fpga_output)
        fpga_output_group.setLayout(fpga_layout)

        # Software Output Box
        software_output_group = QGroupBox("Software Output")
        self.software_output = QTextEdit()
        self.software_output.setReadOnly(True)
        self.software_output.setPlaceholderText("Software output will appear here")
        self.software_output.setMaximumHeight(200)  # Limit height
        
        software_layout = QVBoxLayout()
        software_layout.addWidget(self.software_output)
        software_output_group.setLayout(software_layout)

        outputs_container.addWidget(fpga_output_group)
        outputs_container.addWidget(software_output_group)

        # =========================================================
        # COMPARISON SECTION (NEW)
        # =========================================================
        comparison_group = QGroupBox("Output Comparison")
        
        self.compare_label = QLabel("Run both operations, then click Compare")
        self.compare_label.setStyleSheet("padding: 6px;")
        
        compare_btn = QPushButton("Compare Outputs")
        compare_btn.clicked.connect(self.compare_outputs)
        
        self.comparison_result = QLabel("")
        self.comparison_result.setStyleSheet("font-weight: bold; padding: 6px;")
        self.comparison_result.setWordWrap(True)
        
        comparison_layout = QVBoxLayout()
        comparison_layout.addWidget(self.compare_label)
        comparison_layout.addWidget(compare_btn)
        comparison_layout.addWidget(self.comparison_result)
        
        comparison_group.setLayout(comparison_layout)

        # =========================================================
        # Progress / control
        # =========================================================
        self.progress = QProgressBar()
        self.progress.setValue(0)

        start_fpga_btn = QPushButton("Start FPGA Streaming")
        start_software_btn = QPushButton("Start Software Cipher")
        cancel_btn = QPushButton("Cancel")

        start_fpga_btn.clicked.connect(self.start_fpga_stream)
        start_software_btn.clicked.connect(self.start_software_stream)
        cancel_btn.clicked.connect(self.cancel_stream)

        btn_row = QHBoxLayout()
        btn_row.addWidget(start_fpga_btn)
        btn_row.addWidget(start_software_btn)
        btn_row.addWidget(cancel_btn)

        # =========================================================
        # Add all to main layout
        # =========================================================
        main_layout.addWidget(title)
        main_layout.addWidget(self.config_label)
        main_layout.addWidget(self.status_label)

        main_layout.addLayout(mode_row)
        main_layout.addLayout(data_type_row)
        main_layout.addLayout(output_format_row)
        
        main_layout.addWidget(self.text_group)
        main_layout.addWidget(self.file_group)

        main_layout.addLayout(outputs_container)
        main_layout.addWidget(comparison_group)

        main_layout.addWidget(self.progress)
        main_layout.addLayout(btn_row)

        main_layout.addStretch()

        # =========================================================
        # Create scroll area and set main widget
        # =========================================================
        scroll = QScrollArea()
        scroll.setWidget(main_widget)
        scroll.setWidgetResizable(True)
        
        # Set scroll area as the main layout
        page_layout = QVBoxLayout(self)
        page_layout.addWidget(scroll)
        page_layout.setContentsMargins(0, 0, 0, 0)

        # =========================================================
        # Create tmp directory
        # =========================================================
        self._ensure_tmp_directory()

    # =============================================================
    # Directory setup
    # =============================================================
    def _ensure_tmp_directory(self):
        """Create tmp directory if it doesn't exist"""
        tmp_dir = os.path.join(os.getcwd(), "tmp")
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
            print(f"✅ Created tmp directory: {tmp_dir}")

    def _get_output_paths(self):
        """Get output file paths in tmp directory"""
        tmp_dir = os.path.join(os.getcwd(), "tmp")
        fpga_path = os.path.join(tmp_dir, "fpga_stream_output")
        software_path = os.path.join(tmp_dir, "software_stream_output")
        return fpga_path, software_path

    # =============================================================
    # UI logic
    # =============================================================
    def update_input_mode(self):
        """Show / hide widgets based on input mode"""
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

    # =============================================================
    # COMPARISON LOGIC (NEW)
    # =============================================================
    def compare_outputs(self):
        """Compare FPGA and Software outputs (both GUI text and files)"""
        print("\n" + "="*60)
        print("COMPARING OUTPUTS")
        print("="*60)
        
        # Get GUI text outputs
        fpga_text = self.fpga_output.toPlainText().strip()
        software_text = self.software_output.toPlainText().strip()
        
        # Get file paths
        fpga_file_path, software_file_path = self._get_output_paths()
        
        results = []
        all_match = True
        
        # -------------------------
        # Compare GUI text
        # -------------------------
        if fpga_text and software_text:
            print(f"\n[GUI TEXT COMPARISON]")
            print(f"FPGA length: {len(fpga_text)}")
            print(f"Software length: {len(software_text)}")
            
            if fpga_text == software_text:
                print("✅ GUI outputs MATCH")
                results.append("✅ GUI outputs MATCH")
            else:
                print("❌ GUI outputs DO NOT MATCH")
                results.append("❌ GUI outputs DO NOT MATCH")
                all_match = False
                
                # Find first difference
                for i, (c1, c2) in enumerate(zip(fpga_text, software_text)):
                    if c1 != c2:
                        print(f"   First difference at position {i}: FPGA='{c1}' vs Software='{c2}'")
                        results.append(f"   First diff at pos {i}: FPGA='{c1}' vs Software='{c2}'")
                        break
        elif fpga_text or software_text:
            print("⚠️ Only one GUI output present")
            results.append("⚠️ Only one GUI output available")
            all_match = False
        else:
            print("⚠️ No GUI outputs to compare")
            results.append("⚠️ No GUI outputs to compare")
        
        # -------------------------
        # Compare files
        # -------------------------
        fpga_file_exists = os.path.exists(fpga_file_path)
        software_file_exists = os.path.exists(software_file_path)
        
        print(f"\n[FILE COMPARISON]")
        print(f"FPGA file exists: {fpga_file_exists}")
        print(f"Software file exists: {software_file_exists}")
        
        if fpga_file_exists and software_file_exists:
            try:
                with open(fpga_file_path, 'r') as f:
                    fpga_file_content = f.read()
                
                with open(software_file_path, 'r') as f:
                    software_file_content = f.read()
                
                print(f"FPGA file size: {len(fpga_file_content)} chars")
                print(f"Software file size: {len(software_file_content)} chars")
                
                if fpga_file_content == software_file_content:
                    print("✅ File outputs MATCH")
                    results.append("✅ File outputs MATCH")
                else:
                    print("❌ File outputs DO NOT MATCH")
                    results.append("❌ File outputs DO NOT MATCH")
                    all_match = False
                    
                    # Find first difference
                    for i, (c1, c2) in enumerate(zip(fpga_file_content, software_file_content)):
                        if c1 != c2:
                            print(f"   First difference at position {i}: FPGA='{c1}' vs Software='{c2}'")
                            results.append(f"   First diff at pos {i}")
                            break
                            
            except Exception as e:
                print(f"❌ Error reading files: {e}")
                results.append(f"❌ Error reading files: {e}")
                all_match = False
        elif fpga_file_exists or software_file_exists:
            print("⚠️ Only one output file exists")
            results.append("⚠️ Only one output file exists")
            all_match = False
        else:
            print("⚠️ No output files to compare")
            results.append("⚠️ No output files to compare")
        
        # -------------------------
        # Display results
        # -------------------------
        print("\n" + "="*60)
        print("COMPARISON COMPLETE")
        print("="*60 + "\n")
        
        result_text = "\n".join(results)
        
        if all_match and results:
            self.comparison_result.setText("🎉 ALL OUTPUTS MATCH!\n" + result_text)
            self.comparison_result.setStyleSheet("color: green; font-weight: bold; padding: 6px;")
        else:
            self.comparison_result.setText(result_text)
            self.comparison_result.setStyleSheet("color: red; font-weight: bold; padding: 6px;")

    # =============================================================
    # Streaming control - FPGA
    # =============================================================
    def start_fpga_stream(self):
        """Start FPGA streaming operation"""
        
        # Clear FPGA output and comparison
        self.fpga_output.clear()
        self.comparison_result.clear()
        
        # Get input data
        if self.text_mode_radio.isChecked():
            data = self.text_input.toPlainText()
            in_path = None
            
            if not data:
                self.status_label.setText("❌ No input text provided")
                self.status_label.setStyleSheet("color: red;")
                return

            self.status_label.setText("🔄 FPGA streaming text...")
            self.status_label.setStyleSheet("color: blue;")
        else:
            data = None
            in_path = self.input_path.text()

            if not in_path:
                self.status_label.setText("❌ Input file not selected")
                self.status_label.setStyleSheet("color: red;")
                return

            self.status_label.setText("🔄 FPGA streaming file...")
            self.status_label.setStyleSheet("color: blue;")

        # Get input format
        is_hex = self.hex_type_radio.isChecked()
        
        # Get output format
        output_hex = self.output_hex_radio.isChecked()
        
        # Get output path
        if  self.text_mode_radio.isChecked():
            fpga_out_path = None
        else : 
            fpga_out_path, _ = self._get_output_paths()

        # Call controller
        self.controller.fpga_operation(
            op="stream",
            stream_text=data,
            stream_in_path=in_path,
            stream_out_path=fpga_out_path,
            stream_is_hex=is_hex,
            stream_out_hex=output_hex
        )

    # =============================================================
    # Streaming control - SOFTWARE
    # =============================================================
    def start_software_stream(self):
        """Start software cipher operation"""
        
        # Clear software output and comparison
        self.software_output.clear()
        self.comparison_result.clear()
        
        # Get input data
        if self.text_mode_radio.isChecked():
            data = self.text_input.toPlainText()
            in_path = None
            
            if not data:
                self.status_label.setText("❌ No input text provided")
                self.status_label.setStyleSheet("color: red;")
                return

            self.status_label.setText("🔄 Software processing text...")
            self.status_label.setStyleSheet("color: blue;")
        else:
            data = None
            in_path = self.input_path.text()

            if not in_path:
                self.status_label.setText("❌ Input file not selected")
                self.status_label.setStyleSheet("color: red;")
                return

            self.status_label.setText("🔄 Software processing file...")
            self.status_label.setStyleSheet("color: blue;")

        # Get input format
        is_hex = self.hex_type_radio.isChecked()
        
        # Get output format
        output_hex = self.output_hex_radio.isChecked()
        
        # Get output path
        _, software_out_path = self._get_output_paths()

        # Call controller software operation
        result = self.controller.software_operation(
            op="stream",
            stream_text=data,
            stream_in_path=in_path,
            stream_out_path=software_out_path,
            stream_is_hex=is_hex,
            stream_out_hex=output_hex
        )

        # Handle result
        if result:
            self.status_label.setText("✅ Software processing complete")
            self.status_label.setStyleSheet("color: green;")
            
            # Display result in software output box
            if "output" in result:
                self.software_output.setPlainText(result["output"])
        else:
            self.status_label.setText("❌ Software processing failed")
            self.status_label.setStyleSheet("color: red;")

    # =============================================================
    # Cancel
    # =============================================================
    def cancel_stream(self):
        """Cancel streaming operations"""
        self.status_label.setText("⛔ Streaming cancelled")
        self.status_label.setStyleSheet("color: orange;")

        # Placeholder for actual cancellation logic
        # self.controller.cancel_stream()

    # =============================================================
    # Configuration update
    # =============================================================
    def on_config_update(self, config):
        """Update config display when configuration changes"""
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

    # =============================================================
    # UART data received (FPGA output)
    # =============================================================
    @Slot(bytes)
    def on_stream_data_received(self, data: bytes):
        """Handle incoming FPGA stream data"""
        if self.output_hex_radio.isChecked():
            text = data.hex()
        else:
            try:
                text = data.decode("utf-8", errors="replace")
            except:
                text = str(data)

        # Display in FPGA output box
        self.fpga_output.setPlainText(text)