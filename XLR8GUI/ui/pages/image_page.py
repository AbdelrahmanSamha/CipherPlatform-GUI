from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QGroupBox, QScrollArea,QProgressBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Slot
from PIL import Image
import os
import time


class ImagePage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        # Metrics tracking
        self.fpga_done = False
        self.software_done = False
        self.fpga_time_ms = 0
        self.software_time_ms = 0
        self.data_size = 0  # Will be set when image is loaded

        
        
        self.controller.uart_image_page_received.connect(self.on_fpga_complete)# Note: You need to add this signal emission in your read_loop when image operation completes
        self.controller.operation_progress.connect(self.update_progress)

        # -----------------------------
        # Prepare img_tmp directory
        # -----------------------------
        self.tmp_dir = "img_tmp"
        os.makedirs(self.tmp_dir, exist_ok=True)

        self.input_path = os.path.join(self.tmp_dir, "input.bmp")
        self.fpga_output_path = os.path.join(self.tmp_dir, "fpga_img_output.bmp")
        self.sw_output_path = os.path.join(self.tmp_dir, "sw_img_output.bmp")

        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # Main content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

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
        # Input Image Section
        # -----------------------------
        input_group = QGroupBox("Input Image")
        input_layout = QVBoxLayout()

        self.input_preview = QLabel("No image loaded")
        self.input_preview.setStyleSheet("border: 1px solid black; background-color: #f0f0f0;")
        self.input_preview.setFixedSize(256, 256)
        self.input_preview.setScaledContents(True)
        self.input_preview.setAlignment(Qt.AlignCenter)

        self.load_btn = QPushButton("Load Image")
        self.load_btn.clicked.connect(self.load_image)

        input_layout.addWidget(self.input_preview)
        input_layout.addWidget(self.load_btn)
        input_group.setLayout(input_layout)

        # -----------------------------
        # Output Images Section (side by side)
        # -----------------------------
        outputs_layout = QHBoxLayout()

        # FPGA Output
        fpga_group = QGroupBox("FPGA Output")
        fpga_layout = QVBoxLayout()

        self.fpga_output_preview = QLabel("No output yet")
        self.fpga_output_preview.setStyleSheet("border: 1px solid black; background-color: #f0f0f0;")
        self.fpga_output_preview.setFixedSize(256, 256)
        self.fpga_output_preview.setScaledContents(True)
        self.fpga_output_preview.setAlignment(Qt.AlignCenter)

        self.fpga_cipher_btn = QPushButton("Start FPGA Cipher")
        self.fpga_cipher_btn.clicked.connect(self.start_fpga_cipher)

        fpga_layout.addWidget(self.fpga_output_preview)
        fpga_layout.addWidget(self.fpga_cipher_btn)
        fpga_group.setLayout(fpga_layout)

        # Software Output
        sw_group = QGroupBox("Software Output")
        sw_layout = QVBoxLayout()

        self.sw_output_preview = QLabel("No output yet")
        self.sw_output_preview.setStyleSheet("border: 1px solid black; background-color: #f0f0f0;")
        self.sw_output_preview.setFixedSize(256, 256)
        self.sw_output_preview.setScaledContents(True)
        self.sw_output_preview.setAlignment(Qt.AlignCenter)

        self.sw_cipher_btn = QPushButton("Start Software Cipher")
        self.sw_cipher_btn.clicked.connect(self.start_software_cipher)

        sw_layout.addWidget(self.sw_output_preview)
        sw_layout.addWidget(self.sw_cipher_btn)
        sw_group.setLayout(sw_layout)

        outputs_layout.addWidget(fpga_group)
        outputs_layout.addWidget(sw_group)

        # -----------------------------
        # Comparison Section
        # -----------------------------
        comparison_group = QGroupBox("Output Comparison")
        comparison_layout = QVBoxLayout()

        self.compare_label = QLabel("Run both operations, then click Compare")
        self.compare_label.setStyleSheet("padding: 6px;")

        compare_btn = QPushButton("Compare Outputs")
        compare_btn.clicked.connect(self.compare_outputs)

        self.comparison_result = QLabel("")
        self.comparison_result.setStyleSheet("font-weight: bold; padding: 6px;")
        self.comparison_result.setWordWrap(True)

        comparison_layout.addWidget(self.compare_label)
        comparison_layout.addWidget(compare_btn)
        comparison_layout.addWidget(self.comparison_result)
        comparison_group.setLayout(comparison_layout)

        # -----------------------------
        # Control Buttons
        # -----------------------------
        control_layout = QHBoxLayout()

        self.swap_btn = QPushButton("Swap I/O (Use Output as Input)")
        self.swap_btn.clicked.connect(self.swap_io)

        self.record_metrics_btn = QPushButton("📊 Record Metrics")
        self.record_metrics_btn.setEnabled(False)
        self.record_metrics_btn.clicked.connect(self.record_metrics)

        control_layout.addWidget(self.swap_btn)
        control_layout.addWidget(self.record_metrics_btn)

        # ─────────────────────────────────────────────────────
        # NEW: Add Progress Section (after FPGA output group)
        # ─────────────────────────────────────────────────────
        
        progress_group = QGroupBox("FPGA Operation Progress")
        progress_layout = QVBoxLayout()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        
        # Progress label
        self.progress_label = QLabel("Ready")
        self.progress_label.setStyleSheet("padding: 5px;")
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        progress_group.setLayout(progress_layout)


        # -----------------------------
        # Assemble layout
        # -----------------------------
        content_layout.addWidget(title)
        content_layout.addWidget(self.status_label)
        content_layout.addWidget(input_group)
        content_layout.addLayout(outputs_layout)
        content_layout.addWidget(progress_group)
        content_layout.addWidget(comparison_group)
        content_layout.addLayout(control_layout)
        content_layout.addStretch()

        # Set scroll area
        scroll.setWidget(content_widget)

        # Main page layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
        main_layout.setContentsMargins(0, 0, 0, 0)



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

            # Save to img_tmp/input.bmp
            img.save(self.input_path, format="BMP")

            # Calculate data size (BMP file size - 54 byte header)
            file_size = os.path.getsize(self.input_path)
            self.data_size = file_size - 54  # Pixel data only

            # Update preview
            pixmap = QPixmap(self.input_path)
            self.input_preview.setPixmap(pixmap)

            self.status_label.setText(f"✅ Loaded image ({self.data_size} bytes pixel data)")
            self.status_label.setStyleSheet("color: green; padding: 4px;")

        except Exception as e:
            self.status_label.setText(f"❌ Failed to load image: {e}")
            self.status_label.setStyleSheet("color: red; padding: 4px;")

    # -----------------------------
    # Start FPGA Cipher
    # -----------------------------
    @Slot()
    def start_fpga_cipher(self):
        if not os.path.exists(self.input_path):
            self.status_label.setText("❌ No input image loaded")
            self.status_label.setStyleSheet("color: red; padding: 4px;")
            return
        # Reset progress
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting...")
        self.progress_label.setStyleSheet("color: blue; padding: 5px;")
        self.update_progress(0,0,0)
        self.status_label.setText("🔄 Sending image to FPGA...")
        self.status_label.setStyleSheet("color: blue; padding: 4px;")

        # Clear FPGA output preview
        self.fpga_output_preview.clear()
        self.fpga_output_preview.setText("Processing...")
        self.comparison_result.clear()

        # Start timing
        self.fpga_start_time = time.perf_counter()

        # Call controller
        self.controller.fpga_operation(
            op="image",
            stream_in_path=self.input_path,
            stream_out_path=self.fpga_output_path,
            stream_is_hex=False
        )

    # -----------------------------
    # FPGA Operation Complete (called by signal from read_loop)
    # -----------------------------
    @Slot()
    def on_fpga_complete(self):
        """
        Called when FPGA image operation completes
        This should be connected to a signal from controller
        """
        # End timing
        self.fpga_time_ms = (time.perf_counter() - self.fpga_start_time) * 1000

        # Update preview
        if os.path.exists(self.fpga_output_path):
            pixmap = QPixmap(self.fpga_output_path)
            self.fpga_output_preview.setPixmap(pixmap)
            self.status_label.setText("✅ FPGA cipher complete")
            self.status_label.setStyleSheet("color: green; padding: 4px;")
        else:
            self.status_label.setText("❌ FPGA output file not found")
            self.status_label.setStyleSheet("color: red; padding: 4px;")

        # Mark FPGA as done
        self.fpga_done = True
        self._update_record_button()

    # -----------------------------
    # Start Software Cipher
    # -----------------------------
    @Slot()
    def start_software_cipher(self):
        if not os.path.exists(self.input_path):
            self.status_label.setText("❌ No input image loaded")
            self.status_label.setStyleSheet("color: red; padding: 4px;")
            return

        self.status_label.setText("🔄 Processing image in software...")
        self.status_label.setStyleSheet("color: blue; padding: 4px;")

        # Clear software output preview
        self.sw_output_preview.clear()
        self.sw_output_preview.setText("Processing...")
        self.comparison_result.clear()

        # Start timing
        start_time = time.perf_counter()

        # Call controller software operation
        result = self.controller.software_operation(
            op="image",
            stream_in_path=self.input_path,
            stream_out_path=self.sw_output_path,
            stream_is_hex=False
        )

        # End timing
        end_time = time.perf_counter()
        self.software_time_ms = (end_time - start_time) * 1000

        # Handle result
        if result and os.path.exists(self.sw_output_path):
            pixmap = QPixmap(self.sw_output_path)
            self.sw_output_preview.setPixmap(pixmap)
            self.status_label.setText("✅ Software cipher complete")
            self.status_label.setStyleSheet("color: green; padding: 4px;")

            # Mark software as done
            self.software_done = True
            self._update_record_button()
        else:
            self.status_label.setText("❌ Software cipher failed")
            self.status_label.setStyleSheet("color: red; padding: 4px;")

    # -----------------------------
    # Compare Outputs
    # -----------------------------
    @Slot()
    def compare_outputs(self):
        """Compare FPGA and Software outputs"""
        print("\n" + "="*60)
        print("COMPARING IMAGE OUTPUTS")
        print("="*60)

        fpga_exists = os.path.exists(self.fpga_output_path)
        sw_exists = os.path.exists(self.sw_output_path)

        if not fpga_exists and not sw_exists:
            self.comparison_result.setText("⚠️ No outputs to compare. Run both operations first.")
            self.comparison_result.setStyleSheet("color: orange; font-weight: bold;")
            return
        elif not fpga_exists:
            self.comparison_result.setText("⚠️ FPGA output not available")
            self.comparison_result.setStyleSheet("color: orange; font-weight: bold;")
            return
        elif not sw_exists:
            self.comparison_result.setText("⚠️ Software output not available")
            self.comparison_result.setStyleSheet("color: orange; font-weight: bold;")
            return

        try:
            # Read both files as binary
            with open(self.fpga_output_path, 'rb') as f:
                fpga_data = f.read()

            with open(self.sw_output_path, 'rb') as f:
                sw_data = f.read()

            print(f"FPGA output size: {len(fpga_data)} bytes")
            print(f"Software output size: {len(sw_data)} bytes")

            # Compare
            if fpga_data == sw_data:
                print("✅ Outputs MATCH")
                self.comparison_result.setText("🎉 OUTPUTS MATCH PERFECTLY!\nFPGA and Software produced identical images.")
                self.comparison_result.setStyleSheet("color: green; font-weight: bold;")
            else:
                print("❌ Outputs DO NOT MATCH")
                
                # Find first difference
                min_len = min(len(fpga_data), len(sw_data))
                first_diff = -1
                for i in range(min_len):
                    if fpga_data[i] != sw_data[i]:
                        first_diff = i
                        break

                if first_diff >= 0:
                    result_text = f"❌ OUTPUTS DO NOT MATCH\nFirst difference at byte {first_diff}"
                    print(f"First difference at byte {first_diff}")
                else:
                    result_text = f"❌ OUTPUTS DO NOT MATCH\nFiles have different lengths"

                self.comparison_result.setText(result_text)
                self.comparison_result.setStyleSheet("color: red; font-weight: bold;")

        except Exception as e:
            print(f"❌ Error comparing files: {e}")
            self.comparison_result.setText(f"❌ Error comparing files: {e}")
            self.comparison_result.setStyleSheet("color: red; font-weight: bold;")

        print("="*60 + "\n")

    # -----------------------------
    # Swap I/O
    # -----------------------------
    @Slot()
    def swap_io(self):
        """Use the most recent output as the new input"""
        # Check which output is more recent or exists
        fpga_exists = os.path.exists(self.fpga_output_path)
        sw_exists = os.path.exists(self.sw_output_path)

        if not fpga_exists and not sw_exists:
            self.status_label.setText("❌ No output to swap")
            self.status_label.setStyleSheet("color: red; padding: 4px;")
            return

        # Use FPGA output if it exists, otherwise software output
        if fpga_exists:
            source = self.fpga_output_path
            source_label = "FPGA"
        else:
            source = self.sw_output_path
            source_label = "Software"

        try:
            # Copy output to input
            import shutil
            shutil.copy(source, self.input_path)

            # Update input preview
            pixmap = QPixmap(self.input_path)
            self.input_preview.setPixmap(pixmap)

            # Recalculate data size
            file_size = os.path.getsize(self.input_path)
            self.data_size = file_size - 54

            self.status_label.setText(f"✅ Swapped: {source_label} output is now input")
            self.status_label.setStyleSheet("color: green; padding: 4px;")

        except Exception as e:
            self.status_label.setText(f"❌ Swap failed: {e}")
            self.status_label.setStyleSheet("color: red; padding: 4px;")

    # -----------------------------
    # Metrics button update
    # -----------------------------
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

    # -----------------------------
    # Record metrics
    # -----------------------------
    def record_metrics(self):
        """Record metrics to metrics page"""
        if not (self.fpga_done and self.software_done):
            return

        # Get key size from config
        key_size = self.controller.config.get("key_size", 128)

        # Record metric via controller
        self.controller.record_metric({
            "operation": "image",
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

   # NEW: Progress handler (same as stream page)
    @Slot(int, int, int)
    def update_progress(self, bytes_received, bytes_total, percentage):
        self.progress_bar.setValue(percentage)
        
        # Format bytes
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
        
        self.progress_label.setText(label_text)
        
        # Color based on progress
        if percentage == 100:
            self.progress_label.setStyleSheet("color: green; font-weight: bold; padding: 5px;")
        else:
            self.progress_label.setStyleSheet("color: blue; padding: 5px;")
