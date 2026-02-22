from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit,
    QLineEdit, QRadioButton, QButtonGroup,
    QFileDialog, QProgressBar, QGroupBox,
    QScrollArea
)
from PySide6.QtCore import Slot
import os
import time


class StreamPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.only_compare_file = None
        # Metrics tracking
        self.fpga_done = False
        self.software_done = False
        self.fpga_time_ms = 0
        self.software_time_ms = 0
        self.data_size = 0

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
        self.controller.operation_progress.connect(self.update_progress)
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
        # COMPARISON SECTION
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
        self.record_metrics_btn = QPushButton("📊 Record Metrics")
        self.record_metrics_btn.setEnabled(False)
        cancel_btn = QPushButton("Cancel")

        start_fpga_btn.clicked.connect(self.start_fpga_stream)
        start_software_btn.clicked.connect(self.start_software_stream)
        self.record_metrics_btn.clicked.connect(self.record_metrics)
        cancel_btn.clicked.connect(self.cancel_stream)

        btn_row = QHBoxLayout()
        btn_row.addWidget(start_fpga_btn)
        btn_row.addWidget(start_software_btn)
        btn_row.addWidget(self.record_metrics_btn)
        btn_row.addWidget(cancel_btn)

        # ─────────────────────────────────────────────────────
        # NEW: Add FPGA Progress Section (after FPGA output box)
        # ─────────────────────────────────────────────────────
        
        fpga_progress_group = QGroupBox("FPGA Operation Progress")
        fpga_progress_layout = QVBoxLayout()
        
        # Progress bar
        self.fpga_progress_bar = QProgressBar()
        self.fpga_progress_bar.setRange(0, 100)
        self.fpga_progress_bar.setValue(0)
        self.fpga_progress_bar.setTextVisible(True)
        self.fpga_progress_bar.setFormat("%p%")  # Shows percentage
        
        # Progress label
        self.fpga_progress_label = QLabel("Ready")
        self.fpga_progress_label.setStyleSheet("padding: 5px;")
        
        fpga_progress_layout.addWidget(self.fpga_progress_bar)
        fpga_progress_layout.addWidget(self.fpga_progress_label)
        fpga_progress_group.setLayout(fpga_progress_layout)


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
        main_layout.addWidget(fpga_progress_group)
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
    # DATA SIZE CALCULATION
    # =============================================================
    def _calculate_data_size(self):
        """Calculate the input data size in bytes"""
        if self.text_mode_radio.isChecked():
            data = self.text_input.toPlainText()
            if self.hex_type_radio.isChecked():
                # Hex input - each pair of hex chars = 1 byte
                hex_cleaned = data.replace(" ", "").replace("\n", "").replace("\r", "")
                return len(hex_cleaned) // 2
            else:
                # ASCII input
                return len(data.encode('utf-8'))
        else:
            # File input
            in_path = self.input_path.text()
            if in_path and os.path.exists(in_path):
                return os.path.getsize(in_path)
        return 0

    # =============================================================
    # COMPARISON LOGIC
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
        # Check if both are binary data messages
        # -------------------------
        fpga_is_binary_msg = (fpga_text.startswith("[") and "Binary encrypted data" in fpga_text) or self.only_compare_file == True
        software_is_binary_msg = (software_text.startswith("[") and "Binary encrypted data" in software_text) or self.only_compare_file == True
        
        both_are_binary_msgs = fpga_is_binary_msg and software_is_binary_msg
        
        # -------------------------
        # Compare GUI text (only if NOT both binary messages)
        # -------------------------
        if both_are_binary_msgs:
            print(f"\n[GUI TEXT COMPARISON]")
            print("ℹ️ Both outputs show binary encrypted data messages")
            print("   Skipping GUI comparison - will compare files instead")
            results.append("ℹ️ Binary encrypted data - comparing files only")
        elif fpga_text and software_text:
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
        # Compare files (BINARY comparison)
        # -------------------------
        fpga_file_exists = os.path.exists(fpga_file_path)
        software_file_exists = os.path.exists(software_file_path)
        
        print(f"\n[FILE COMPARISON]")
        print(f"FPGA file: {fpga_file_path}")
        print(f"FPGA file exists: {fpga_file_exists}")
        print(f"Software file: {software_file_path}")
        print(f"Software file exists: {software_file_exists}")
        
        if fpga_file_exists and software_file_exists:
            try:
                # Read as BINARY (works for both encrypted and text files)
                with open(fpga_file_path, 'rb') as f:
                    fpga_file_content = f.read()
                
                with open(software_file_path, 'rb') as f:
                    software_file_content = f.read()
                
                print(f"FPGA file size: {len(fpga_file_content)} bytes")
                print(f"Software file size: {len(software_file_content)} bytes")
                
                if fpga_file_content == software_file_content:
                    print("✅ File outputs MATCH")
                    results.append("✅ File outputs MATCH")
                else:
                    print("❌ File outputs DO NOT MATCH")
                    results.append("❌ File outputs DO NOT MATCH")
                    all_match = False
                    
                    # Show size mismatch if different
                    if len(fpga_file_content) != len(software_file_content):
                        size_msg = f"   Size mismatch: FPGA={len(fpga_file_content)} bytes vs Software={len(software_file_content)} bytes"
                        print(size_msg)
                        results.append(size_msg)
                    
                    # Find first difference
                    min_len = min(len(fpga_file_content), len(software_file_content))
                    for i in range(min_len):
                        if fpga_file_content[i] != software_file_content[i]:
                            diff_msg = f"   First difference at byte {i}: FPGA=0x{fpga_file_content[i]:02X} vs Software=0x{software_file_content[i]:02X}"
                            print(diff_msg)
                            results.append(f"   First diff at byte {i}")
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
            self.comparison_result.setText(" ALL OUTPUTS MATCH!\n\n" + result_text)
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
        # NEW: Reset progress
        self.fpga_progress_bar.setValue(0)
        self.fpga_progress_label.setText("Starting...")
        self.fpga_progress_label.setStyleSheet("color: blue; padding: 5px;")        


        # Calculate and store data size
        self.data_size = self._calculate_data_size()
        
        if self.data_size == 0:
            self.status_label.setText("❌ No input data")
            self.status_label.setStyleSheet("color: red;")
            return
        
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
        
        fpga_out_path, _ = self._get_output_paths()

        # Start timing
        self.fpga_start_time = time.perf_counter()

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
        
        # Calculate and store data size
        self.data_size = self._calculate_data_size()
        
        if self.data_size == 0:
            self.status_label.setText("❌ No input data")
            self.status_label.setStyleSheet("color: red;")
            return
        
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

        # Start timing
        start_time = time.perf_counter()

        # Call controller software operation
        result = self.controller.software_operation(
            op="stream",
            stream_text=data,
            stream_in_path=in_path,
            stream_out_path=software_out_path,
            stream_is_hex=is_hex,
            stream_out_hex=output_hex
        )

        # End timing
        end_time = time.perf_counter()
        self.software_time_ms = (end_time - start_time) * 1000

        # Handle result
        if result:
            self.status_label.setText("✅ Software processing complete")
            self.status_label.setStyleSheet("color: green;")
            
            # Display result in software output box
            if "output" in result:
                self.software_output.setPlainText(result["output"])
            
            # Mark software as done
            self.software_done = True
            self._update_record_button()
        else:
            self.status_label.setText("❌ Software processing failed")
            self.status_label.setStyleSheet("color: red;")

    # =============================================================
    # Metrics button update
    # =============================================================
    def _update_record_button(self):
        """Update the record metrics button state"""
        if self.fpga_done and self.software_done:
            self.record_metrics_btn.setEnabled(True)
            self.record_metrics_btn.setStyleSheet(
                "background-color: #4CAF50; color: white; font-weight: bold;"
            )
        else:
            self.record_metrics_btn.setEnabled(False)
            self.record_metrics_btn.setStyleSheet("")

    # =============================================================
    # Record metrics
    # =============================================================
    def record_metrics(self):
        """Record metrics to metrics page"""
        if not (self.fpga_done and self.software_done):
            return
        
        # Get key size from config
        key_size = self.controller.config.get("key_size", 128)
        
        # Record metric via controller
        self.controller.record_metric({
            "operation": "stream",
            "data_size": self.data_size,
            "mode": self.controller.config["mode"],
            "key_size": key_size,
            "direction": self.controller.config["direction"],
            "fpga_time_ms": self.fpga_time_ms,
            "software_time_ms": self.software_time_ms,
        })
        
        # Show feedback
        self.status_label.setText("✅ Metrics recorded successfully!")
        self.status_label.setStyleSheet("color: green; padding: 4px;")
        
        # Reset for next run
        self.fpga_done = False
        self.software_done = False
        self._update_record_button()

    # =============================================================
    # Cancel
    # =============================================================
    def cancel_stream(self):
        """Cancel streaming operations"""
        self.status_label.setText("⛔ Streaming cancelled")
        self.status_label.setStyleSheet("color: orange;")
        
        # Reset metrics state
        self.fpga_done = False
        self.software_done = False
        self._update_record_button()

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

    @Slot(bytes)
    def on_stream_data_received(self, data: bytes):
        """Handle incoming FPGA stream data"""
        
        if self.output_hex_radio.isChecked():
            # User wants HEX output
            text = data.hex()
        else:
            # User wants ASCII output
            if self.controller.config["direction"] == "enc":
                # ENCRYPTING - binary data, can't show as ASCII
                text = f"[Check tmp/fpga_stream_output for full output.\n Binary encrypted data  - {len(data)} bytes]"
                #text = f"[Binary encrypted data saved to file - {len(data)} bytes]\nCheck tmp/fpga_stream_output for full output"
            else:
                # DECRYPTING - plaintext, CAN show as ASCII
                try:
                    text = data.decode("utf-8", errors="replace")
                except:
                    text = str(data)

        # Add truncation notice if data is at 1000 byte limit
        if len(data) >= 1000 :
            self.only_compare_file = True
            text += "\n\n... (Output truncated for display. Full output saved to tmp/fpga_stream_output)"

        # Display in FPGA output box
        self.fpga_output.setPlainText(text)
        
        # Record FPGA time
        self.fpga_time_ms = (time.perf_counter() - self.fpga_start_time) * 1000
        self.fpga_done = True
        self._update_record_button()
        
        # Update status
        self.status_label.setText("✅ FPGA streaming complete")
        self.status_label.setStyleSheet("color: green;")
    # ─────────────────────────────────────────────────────
    # NEW: Progress update handler
    # ─────────────────────────────────────────────────────
    @Slot(int, int, int)
    def update_progress(self, bytes_received, bytes_total, percentage):
        '''Update progress bar and label'''
        
        # Update progress bar
        self.fpga_progress_bar.setValue(percentage)
        
        # Format bytes nicely
        if bytes_total < 1024:
            label_text = f"{bytes_received} / {bytes_total} bytes ({percentage}%)"
        elif bytes_total < 1024 * 1024:
            recv_kb = bytes_received / 1024
            total_kb = bytes_total / 1024
            label_text = f"{recv_kb:.1f} / {total_kb:.1f} KB ({percentage}%)"
        else:
            recv_mb = bytes_received / (1024 * 1024)
            total_mb = bytes_total / (1024 * 1024)
            label_text = f"{recv_mb:.2f} / {total_mb:.2f} MB ({percentage}%)"
        
        self.fpga_progress_label.setText(label_text)
        
        # Change color based on progress
        if percentage == 100:
            self.fpga_progress_label.setStyleSheet("color: green; font-weight: bold; padding: 5px;")
        else:
            self.fpga_progress_label.setStyleSheet("color: blue; padding: 5px;")
