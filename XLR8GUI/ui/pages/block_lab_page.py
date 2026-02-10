from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QGroupBox,QScrollArea
)
from PySide6.QtCore import Qt


class BlockLabPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        # round tracking
        self.current_block_index = 0
        self.total_expected_blocks = 0

        self.controller.uart_blocklab_page_received.connect(self.handle_uart_block)

        # -----------------------------
        # Title
        # -----------------------------
        title = QLabel("Block Cipher Lab")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")

        # -----------------------------
        # Configuration display
        # -----------------------------
        self.config_label = QLabel("Mode: None | Operation: Encryption | Key Size: None | Key: None ")
        self.config_label.setStyleSheet("font-family: monospace;")
        self.controller.config_updated.connect(self.on_config_update)

        # -----------------------------
        # Block input
        # -----------------------------
        block_layout = QHBoxLayout()
        block_layout.addWidget(QLabel("Enter block (128 bits):"))
        self.block_input = QLineEdit()
        self.block_input.setPlaceholderText("32 hex characters")
        self.block_input.setMaxLength(32)
        self.block_input.setStyleSheet("font-family: monospace;")
        block_layout.addWidget(self.block_input)

        # -----------------------------
        # Control buttons
        # -----------------------------
        start_btn = QPushButton("Start Encryption")
        reset_btn = QPushButton("Reset FPGA")
        sw_btn = QPushButton("Start Software Encryption")

        start_btn.clicked.connect(self.start)
        reset_btn.clicked.connect(self.reset)
        sw_btn.clicked.connect(self.start_software)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(start_btn)
        btn_layout.addWidget(sw_btn)
        btn_layout.addWidget(reset_btn)

        # -----------------------------
        # FPGA Round outputs
        # -----------------------------
        self.round_boxes = []
        self.round_labels = []

        fpga_group = QGroupBox("FPGA Rounds Output")
        self.rounds_layout = QVBoxLayout()
        fpga_group.setLayout(self.rounds_layout)

        # FPGA final
        final_layout = QHBoxLayout()
        final_layout.addWidget(QLabel("FPGA Final Result:"))
        self.final_box = QLineEdit()
        self.final_box.setReadOnly(True)
        self.final_box.setMaxLength(32)
        self.final_box.setStyleSheet("font-family: monospace;")
        final_layout.addWidget(self.final_box)

        # -----------------------------
        # Software round outputs (NEW)
        # -----------------------------
        self.sw_round_boxes = []
        self.sw_round_labels = []

        sw_group = QGroupBox("Software Rounds Output")
        self.sw_rounds_layout = QVBoxLayout()
        sw_group.setLayout(self.sw_rounds_layout)

        sw_final_layout = QHBoxLayout()
        sw_final_layout.addWidget(QLabel("Software Final Result:"))
        self.sw_final_box = QLineEdit()
        self.sw_final_box.setReadOnly(True)
        self.sw_final_box.setMaxLength(32)
        self.sw_final_box.setStyleSheet("font-family: monospace;")
        sw_final_layout.addWidget(self.sw_final_box)

        # -----------------------------
        # Comparison label (NEW)
        # -----------------------------
        self.compare_label = QLabel("No comparison yet")
        self.compare_label.setStyleSheet("padding: 6px; font-weight: bold;")

        # -----------------------------
        # Status
        # -----------------------------
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: green; padding: 4px;")

        # -----------------------------
        # Assemble layout
        # -----------------------------
        # -----------------------------
        # Inner content widget
        # -----------------------------
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        content_layout.addWidget(title)
        content_layout.addWidget(self.config_label)
        content_layout.addLayout(block_layout)
        content_layout.addLayout(btn_layout)

        content_layout.addWidget(fpga_group)
        content_layout.addLayout(final_layout)

        content_layout.addWidget(sw_group)
        content_layout.addLayout(sw_final_layout)

        content_layout.addWidget(self.compare_label)
        content_layout.addWidget(self.status_label)
        content_layout.addStretch()

        # -----------------------------
        # Scroll area
        # -----------------------------
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content_widget)

        # -----------------------------
        # Main layout
        # -----------------------------
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)

    # -----------------------------
    # Round visibility logic
    # -----------------------------
    def update_round_visibility(self):
        key_size = self.controller.config.get("key_size")

        if key_size == 128:
            total_rounds = 11
        elif key_size == 192:
            total_rounds = 13
        elif key_size == 256:
            total_rounds = 15
        else:
            total_rounds = 0

        self.total_expected_blocks = total_rounds

        # -------- FPGA boxes --------
        while self.rounds_layout.count():
            item = self.rounds_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.round_boxes.clear()
        self.round_labels.clear()

        # -------- SW boxes --------
        while self.sw_rounds_layout.count():
            item = self.sw_rounds_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.sw_round_boxes.clear()
        self.sw_round_labels.clear()

        # rebuild both sets
        for i in range(total_rounds):
            label_text = "Initial Round:" if i == 0 else f"Round {i}:"

            # FPGA
            fpga_row = QHBoxLayout()
            fpga_label = QLabel(label_text)
            fpga_box = QLineEdit()
            fpga_box.setReadOnly(True)
            fpga_box.setMaxLength(32)
            fpga_box.setStyleSheet("font-family: monospace;")
            fpga_row.addWidget(fpga_label)
            fpga_row.addWidget(fpga_box)
            self.rounds_layout.addLayout(fpga_row)
            self.round_boxes.append(fpga_box)

            # Software
            sw_row = QHBoxLayout()
            sw_label = QLabel(label_text)
            sw_box = QLineEdit()
            sw_box.setReadOnly(True)
            sw_box.setMaxLength(32)
            sw_box.setStyleSheet("font-family: monospace;")
            sw_row.addWidget(sw_label)
            sw_row.addWidget(sw_box)
            self.sw_rounds_layout.addLayout(sw_row)
            self.sw_round_boxes.append(sw_box)

    # -----------------------------
    # UART handler (UNCHANGED)
    # -----------------------------
    def handle_uart_block(self, block: bytes):
        hex_text = block.hex().upper()

        if self.current_block_index < len(self.round_boxes):
            self.round_boxes[self.current_block_index].setText(hex_text)
        else:
            self.final_box.setText(hex_text)
            self.status_label.setText("✅ FPGA Encryption complete")

        self.current_block_index += 1

    # -----------------------------
    # FPGA start (UNCHANGED)
    # -----------------------------
    def start(self):
        block = self.block_input.text()
        cfg = self.controller.config

        if len(block) != 32:
            self.status_label.setText("❌ Block must be 128 bits (32 hex chars)")
            self.status_label.setStyleSheet("color: red; padding: 4px;")
            return

        elif cfg["key"] is None:
            self.status_label.setText("❌ Must configure Key.")
            self.status_label.setStyleSheet("color: red; padding: 4px;")
            return

        self.status_label.setText("✅ Starting FPGA encryption...")
        self.status_label.setStyleSheet("color: green; padding: 4px;")

        self.current_block_index = 0
        self.update_round_visibility()

        for box in self.round_boxes:
            box.clear()
        self.final_box.clear()

        self.controller.fpga_operation(op="block_lab", block_lab=block)

    # -----------------------------
    # Software start (NEW)
    # -----------------------------
    def start_software(self):
        block_hex = self.block_input.text()
        cfg = self.controller.config

        if len(block_hex) != 32:
            self.status_label.setText("❌ Block must be 128 bits (32 hex chars)")
            self.status_label.setStyleSheet("color: red; padding: 4px;")
            return

        if cfg["key"] is None:
            self.status_label.setText("❌ Must configure Key.")
            self.status_label.setStyleSheet("color: red; padding: 4px;")
            return

        self.status_label.setText("Running software encryption...")
        self.status_label.setStyleSheet("color: blue; padding: 4px;")

        # Clear software boxes
        for box in self.sw_round_boxes:
            box.clear()
        self.sw_final_box.clear()

        # -----------------------------
        # CALL CONTROLLER SOFTWARE OP
        # -----------------------------
        result = self.controller.software_operation(
            op="block_lab",
            block_lab=block_hex
        )

        if not result:
            self.compare_label.setText("❌ Software operation failed")
            self.compare_label.setStyleSheet("color: red; font-weight: bold;")
            return

        sw_rounds = result.get("rounds", [])
        sw_final = result.get("final", "")

        # Fill UI
        for i, val in enumerate(sw_rounds):
            if i < len(self.sw_round_boxes):
                self.sw_round_boxes[i].setText(val.upper())

        self.sw_final_box.setText(sw_final.upper())

        # -----------------------------
        # Compare with FPGA result
        # -----------------------------
        fpga_final = self.final_box.text()

        if not fpga_final:
            self.compare_label.setText("⚠ FPGA result not available")
            return

        if fpga_final.upper() == sw_final.upper():
            self.compare_label.setText("✅ Results match")
            self.compare_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.compare_label.setText("❌ Results DO NOT match")
            self.compare_label.setStyleSheet("color: red; font-weight: bold;")

    # -----------------------------
    # Reset
    # -----------------------------
    def reset(self):
        self.status_label.setText("Resetting FPGA...")
        self.status_label.setStyleSheet("color: orange; padding: 4px;")
        self.block_input.clear()
        self.final_box.clear()
        self.sw_final_box.clear()
        self.compare_label.setText("No comparison yet")

        for box in self.round_boxes:
            box.clear()
        for box in self.sw_round_boxes:
            box.clear()

    # -----------------------------
    # Config update
    # -----------------------------
    def on_config_update(self, config):
        if config['direction'] == 'enc':
            op = "Encryption"
        else:
            op = "Decryption"

        self.config_label.setText(
            f"Mode: {config['mode']} | Operation: {op} | "
            f"Key Size: {config['key_size']} | Key: {config['key']}"
        )

        self.update_round_visibility()

        for box in self.round_boxes:
            box.clear()
        for box in self.sw_round_boxes:
            box.clear()

        self.final_box.clear()
        self.sw_final_box.clear()
        self.compare_label.setText("No comparison yet")

        self.status_label.setText("✅ Config updated")
        self.status_label.setStyleSheet("color: green; padding: 4px;")
