from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QGroupBox
)
from PySide6.QtCore import Slot


class RNGPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        # =========================================================
        # Title
        # =========================================================
        title = QLabel("True Random Number Generator")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")

        subtitle = QLabel("Generate numbers for key and IV/Nonce")
        subtitle.setStyleSheet("color: gray;")

        # =========================================================
        # Configuration display
        # =========================================================
        self.config_label = QLabel(
            "Mode: None | Key Size: None | Operation: None"
        )
        self.config_label.setStyleSheet(
            "font-family: monospace; padding: 6px;"
        )

        self.controller.config_updated.connect(self.on_config_update)
        self.controller.uart_rng_page_received.connect(self.handle_rng_data)

        # =========================================================
        # Generate button
        # =========================================================
        generate_btn = QPushButton("Generate")
        generate_btn.clicked.connect(self.generate)

        note = QLabel(
            "ℹ️ The generated Key matches the Key Size set in Configurations"
        )
        note.setStyleSheet("color: gray; font-size: 11px;")

        # =========================================================
        # Output fields
        # =========================================================
        self.key_output = QLineEdit()
        self.key_output.setReadOnly(True)
        self.key_output.setPlaceholderText("Generated Key (hex)")

        # IV / Nonce (optional)
        self.iv_output = QLineEdit()
        self.iv_output.setReadOnly(True)
        self.iv_output.setPlaceholderText("Generated IV / Nonce (hex)")

        self.iv_group = QGroupBox("IV / Nonce")
        iv_layout = QVBoxLayout()
        iv_layout.addWidget(self.iv_output)
        self.iv_group.setLayout(iv_layout)

        # Hidden by default (ECB)
        self.iv_group.setVisible(False)

        # =========================================================
        # Apply button
        # =========================================================
        apply_btn = QPushButton("Use Generated Values as Configuration")
        apply_btn.clicked.connect(self.apply_generated)

        self.status_label = QLabel("Idle")
        self.status_label.setStyleSheet("color: gray; padding: 4px;")

        # =========================================================
        # Layout
        # =========================================================
        layout = QVBoxLayout()

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.config_label)

        layout.addSpacing(10)
        layout.addWidget(generate_btn)
        layout.addWidget(note)

        layout.addSpacing(10)
        layout.addWidget(QLabel("Generated Key"))
        layout.addWidget(self.key_output)
        layout.addWidget(self.iv_group)

        layout.addSpacing(10)
        layout.addWidget(apply_btn)
        layout.addWidget(self.status_label)

        layout.addStretch()
        self.setLayout(layout)

    # =============================================================
    # Configuration updates
    # =============================================================
    def on_config_update(self, config):
        if config["direction"] == "enc":
            op = "Encryption"
        else:
            op = "Decryption"

        self.config_label.setText(
            f"Mode: {config['mode']} | "
            f"Operation: {op} | "
            f"Key Size: {config['key_size']}"
        )

        # Show / hide IV depending on mode
        if config["mode"] == "ECB":
            self.iv_group.setVisible(False)
        else:
            self.iv_group.setVisible(True)

        self.status_label.setText("✅ Config updated")
        self.status_label.setStyleSheet("color: green;")

    # =============================================================
    # Generate RNG values
    # =============================================================
    def generate(self):
        self.status_label.setText("🎲 Generating random values...")
        self.status_label.setStyleSheet("color: blue;")

        # Placeholder – real values come from FPGA
        # Later:
        # key, iv = self.controller.generate_rng()

        #key = "dead389127648273abcdefadad12beaf"      # dummy
        #iv =  "dead389127648273abcdefadad12beaf"      # dummy

        #self.key_output.setText(key)

        #if self.iv_group.isVisible():
        #    self.iv_output.setText(iv)

        #self.status_label.setText("✅ Random values generated")
        #self.status_label.setStyleSheet("color: green;")
        self.controller.fpga_operation(op="rng")

    # =============================================================
    # Apply generated values
    # =============================================================
    def apply_generated(self):
        key = self.key_output.text()

        if not key:
            self.status_label.setText("❌ No generated key to apply")
            self.status_label.setStyleSheet("color: red;")
            return

        iv = None
        if self.iv_group.isVisible():
            iv = self.iv_output.text()
        cnfg = self.controller.config 
        cnfg["key"] = key
        cnfg["iv"]  = iv
        self.controller.set_config(cnfg)

        self.status_label.setText("✅ Generated values applied to configuration")
        self.status_label.setStyleSheet("color: green;")


    @Slot(bytes, bytes)
    def handle_rng_data(self, key: bytes, iv: bytes):
        key_hex = key.hex().upper()
        iv_hex  = iv.hex().upper()

        self.key_output.setText(key_hex)
        if self.iv_group.isVisible():
            self.iv_output.setText(iv_hex)