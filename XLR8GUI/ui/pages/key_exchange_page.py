from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit,
    QGroupBox, QTextEdit, QScrollArea
)
from PySide6.QtCore import Qt
import time


class KeyExchangePage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        # Internal state
        self.current_step = 0
        self.alice_private = None
        self.bob_private = None
        self.alice_public = None
        self.bob_public = None
        self.alice_shared = None
        self.bob_shared = None

        # Connect signals
        self.controller.uart_rng_page_received.connect(self.handle_rng)
        self.controller.uart_keyexchange_page_received.connect(self.handle_fpga_result)

        # -----------------------------
        # Layout Setup
        # -----------------------------
        main_layout = QVBoxLayout(self)

        title = QLabel("Curve25519 Key Exchange Lab")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        main_layout.addWidget(title)

        # Panels layout
        panels_layout = QHBoxLayout()

        # -----------------------------
        # Alice Panel (FPGA)
        # -----------------------------
        alice_group = QGroupBox("Alice (FPGA)")
        alice_layout = QVBoxLayout()

        self.alice_priv_box = self._readonly_box()
        self.alice_pub_box = self._readonly_box()
        self.alice_shared_box = self._readonly_box()
        self.alice_time_box = self._readonly_box()

        alice_layout.addWidget(QLabel("Private Key:"))
        alice_layout.addWidget(self.alice_priv_box)
        alice_layout.addWidget(QLabel("Public Key:"))
        alice_layout.addWidget(self.alice_pub_box)
        alice_layout.addWidget(QLabel("Shared Secret:"))
        alice_layout.addWidget(self.alice_shared_box)
        alice_layout.addWidget(QLabel("FPGA Time (ms):"))
        alice_layout.addWidget(self.alice_time_box)

        alice_group.setLayout(alice_layout)
        panels_layout.addWidget(alice_group)

        # -----------------------------
        # Middle Log Panel
        # -----------------------------
        middle_layout = QVBoxLayout()

        base_label = QLabel("Base Point (u): 09")
        base_label.setAlignment(Qt.AlignCenter)
        base_label.setStyleSheet("font-weight: bold; font-family: monospace;")

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("font-family: monospace;")

        middle_layout.addWidget(base_label)
        middle_layout.addWidget(self.log_box)

        panels_layout.addLayout(middle_layout)

        # -----------------------------
        # Bob Panel (Software)
        # -----------------------------
        bob_group = QGroupBox("Bob (Software)")
        bob_layout = QVBoxLayout()

        self.bob_priv_box = self._readonly_box()
        self.bob_pub_box = self._readonly_box()
        self.bob_shared_box = self._readonly_box()
        self.bob_time_box = self._readonly_box()

        bob_layout.addWidget(QLabel("Private Key:"))
        bob_layout.addWidget(self.bob_priv_box)
        bob_layout.addWidget(QLabel("Public Key:"))
        bob_layout.addWidget(self.bob_pub_box)
        bob_layout.addWidget(QLabel("Shared Secret:"))
        bob_layout.addWidget(self.bob_shared_box)
        bob_layout.addWidget(QLabel("Software Time (ms):"))
        bob_layout.addWidget(self.bob_time_box)

        bob_group.setLayout(bob_layout)
        panels_layout.addWidget(bob_group)

        main_layout.addLayout(panels_layout)

        # -----------------------------
        # Controls
        # -----------------------------
        self.start_btn = QPushButton("Start Secure Key Exchange")
        self.start_btn.clicked.connect(self.start_exchange)

        main_layout.addWidget(self.start_btn)

    # -----------------------------
    # Helpers
    # -----------------------------
    def _readonly_box(self):
        box = QLineEdit()
        box.setReadOnly(True)
        box.setStyleSheet("font-family: monospace;")
        return box

    def log(self, text):
        self.log_box.append(text)

    # -----------------------------
    # Start Process
    # -----------------------------
    def start_exchange(self):
        self.reset_state()
        self.log("[1] Generating private keys on FPGA...")
        self.current_step = 1

        self.controller.fpga_operation(op="rng")

    def reset_state(self):
        self.log_box.clear()
        self.alice_priv_box.clear()
        self.alice_pub_box.clear()
        self.alice_shared_box.clear()
        self.bob_priv_box.clear()
        self.bob_pub_box.clear()
        self.bob_shared_box.clear()
        self.alice_time_box.clear()
        self.bob_time_box.clear()

        self.current_step = 0

    # -----------------------------
    # RNG Handler
    # -----------------------------
    def handle_rng(self, key1: bytes, key2: bytes):
        if self.current_step != 1:
            return

        self.alice_private = key1
        self.bob_private = key2

        self.alice_priv_box.setText(key1.hex().upper())
        self.bob_priv_box.setText(key2.hex().upper())

        self.log("[2] Computing Alice public key on FPGA...")
        self.current_step = 2

        self.fpga_start_time = time.perf_counter()

        self.controller.fpga_operation(
            op="keyexchange_scalar",
            scalar=key1,
            u_coordinate=b"\x09" + b"\x00"*31
        )

    # -----------------------------
    # FPGA Result Handler
    # -----------------------------
    def handle_fpga_result(self, result: bytes):
        if self.current_step == 2:
            # Alice public received
            self.alice_public = result
            self.alice_pub_box.setText(result.hex().upper())

            elapsed = (time.perf_counter() - self.fpga_start_time) * 1000
            self.alice_time_box.setText(f"{elapsed:.2f}")

            self.log("[3] Computing Bob public key in Software...")
            self.current_step = 3

            sw_start = time.perf_counter()

            result = self.controller.software_operation(
                op="keyexchange_scalar",
                scalar=self.bob_private,
                u_coordinate=b"\x09" + b"\x00"*31
            )

            sw_elapsed = (time.perf_counter() - sw_start) * 1000
            self.bob_time_box.setText(f"{sw_elapsed:.2f}")

            self.bob_public = result
            self.bob_pub_box.setText(result.hex().upper())

            self.log("[4] Exchanging public keys...")
            self.log("[5] Computing shared secret on FPGA...")
            self.current_step = 4

            self.fpga_start_time = time.perf_counter()

            self.controller.fpga_operation(
                op="keyexchange_scalar",
                scalar=self.alice_private,
                u_coordinate=self.bob_public
            )

        elif self.current_step == 4:
            # Alice shared received
            self.alice_shared = result
            self.alice_shared_box.setText(result.hex().upper())

            elapsed = (time.perf_counter() - self.fpga_start_time) * 1000
            self.alice_time_box.setText(f"{elapsed:.2f}")

            self.log("[6] Computing shared secret in Software...")
            self.current_step = 5

            sw_start = time.perf_counter()

            result = self.controller.software_operation(
                op="keyexchange_scalar",
                scalar=self.bob_private,
                u_coordinate=self.alice_public
            )

            sw_elapsed = (time.perf_counter() - sw_start) * 1000
            self.bob_time_box.setText(f"{sw_elapsed:.2f}")

            self.bob_shared = result
            self.bob_shared_box.setText(result.hex().upper())

            self.verify()

    # -----------------------------
    # Verification
    # -----------------------------
    def verify(self):
        self.log("[7] Verifying shared secrets...")

        if self.alice_shared == self.bob_shared:
            self.log("✅ Secure Channel Established")
        else:
            self.log("❌ Shared Secret Mismatch")