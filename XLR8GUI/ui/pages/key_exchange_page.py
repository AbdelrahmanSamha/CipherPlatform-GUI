from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit,
    QGroupBox, QTextEdit, QCheckBox, QApplication
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
        
        # Timing
        self.fpga_start_time = 0
        self.fpga_total_time = 0
        self.software_total_time = 0
        self.alice_public_time = 0
        self.bob_public_time = 0
        self.alice_shared_time = 0
        self.bob_shared_time = 0

        # Connect signals
        self.controller.uart_rng_page_received.connect(self.handle_rng)
        self.controller.uart_keyexchange_page_received.connect(self.handle_fpga_result)

        # -----------------------------
        # Layout Setup
        # -----------------------------
        main_layout = QVBoxLayout(self)

        # Title
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

        alice_layout.addWidget(QLabel("Private Key:"))
        priv_alice_layout = QHBoxLayout()
        self.alice_priv_box = self._readonly_box()
        self.alice_priv_copy_btn = QPushButton("📋")
        self.alice_priv_copy_btn.setMaximumWidth(40)
        self.alice_priv_copy_btn.clicked.connect(lambda: self._copy_to_clipboard(self.alice_priv_box.text()))
        priv_alice_layout.addWidget(self.alice_priv_box)
        priv_alice_layout.addWidget(self.alice_priv_copy_btn)
        alice_layout.addLayout(priv_alice_layout)

        alice_layout.addWidget(QLabel("Public Key:"))
        pub_alice_layout = QHBoxLayout()
        self.alice_pub_box = self._readonly_box()
        self.alice_pub_copy_btn = QPushButton("📋")
        self.alice_pub_copy_btn.setMaximumWidth(40)
        self.alice_pub_copy_btn.clicked.connect(lambda: self._copy_to_clipboard(self.alice_pub_box.text()))
        pub_alice_layout.addWidget(self.alice_pub_box)
        pub_alice_layout.addWidget(self.alice_pub_copy_btn)
        alice_layout.addLayout(pub_alice_layout)

        alice_layout.addWidget(QLabel("Shared Secret:"))
        shared_alice_layout = QHBoxLayout()
        self.alice_shared_box = self._readonly_box()
        self.alice_shared_copy_btn = QPushButton("📋")
        self.alice_shared_copy_btn.setMaximumWidth(40)
        self.alice_shared_copy_btn.clicked.connect(lambda: self._copy_to_clipboard(self.alice_shared_box.text()))
        shared_alice_layout.addWidget(self.alice_shared_box)
        shared_alice_layout.addWidget(self.alice_shared_copy_btn)
        alice_layout.addLayout(shared_alice_layout)

        alice_layout.addWidget(QLabel("FPGA Time (ms):"))
        self.alice_time_box = self._readonly_box()
        alice_layout.addWidget(self.alice_time_box)

        alice_group.setLayout(alice_layout)
        panels_layout.addWidget(alice_group)

        # -----------------------------
        # Middle Section (Log + Exchange Visual)
        # -----------------------------
        middle_layout = QVBoxLayout()

        # Base point label
        base_label = QLabel("Base Point (u): 09")
        base_label.setAlignment(Qt.AlignCenter)
        base_label.setStyleSheet("font-weight: bold; font-family: monospace; padding: 5px;")
        middle_layout.addWidget(base_label)

        # Exchange visual
        exchange_visual_layout = QVBoxLayout()
        
        self.arrow_label = QLabel("⟷")
        self.arrow_label.setAlignment(Qt.AlignCenter)
        self.arrow_label.setStyleSheet("font-size: 48px; color: #CCCCCC;")
        
        self.exchange_status = QLabel("Ready to start exchange")
        self.exchange_status.setAlignment(Qt.AlignCenter)
        self.exchange_status.setWordWrap(True)
        self.exchange_status.setStyleSheet("padding: 10px; color: gray;")
        
        exchange_visual_layout.addWidget(self.arrow_label)
        exchange_visual_layout.addWidget(self.exchange_status)
        
        middle_layout.addLayout(exchange_visual_layout)

        # Log box
        log_label = QLabel("Exchange Log:")
        log_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        middle_layout.addWidget(log_label)
        
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("font-family: monospace; background-color: #F5F5F5;")
        middle_layout.addWidget(self.log_box)

        panels_layout.addLayout(middle_layout)

        # -----------------------------
        # Bob Panel (Software)
        # -----------------------------
        bob_group = QGroupBox("Bob (Software)")
        bob_layout = QVBoxLayout()

        bob_layout.addWidget(QLabel("Private Key:"))
        priv_bob_layout = QHBoxLayout()
        self.bob_priv_box = self._readonly_box()
        self.bob_priv_copy_btn = QPushButton("📋")
        self.bob_priv_copy_btn.setMaximumWidth(40)
        self.bob_priv_copy_btn.clicked.connect(lambda: self._copy_to_clipboard(self.bob_priv_box.text()))
        priv_bob_layout.addWidget(self.bob_priv_box)
        priv_bob_layout.addWidget(self.bob_priv_copy_btn)
        bob_layout.addLayout(priv_bob_layout)

        bob_layout.addWidget(QLabel("Public Key:"))
        pub_bob_layout = QHBoxLayout()
        self.bob_pub_box = self._readonly_box()
        self.bob_pub_copy_btn = QPushButton("📋")
        self.bob_pub_copy_btn.setMaximumWidth(40)
        self.bob_pub_copy_btn.clicked.connect(lambda: self._copy_to_clipboard(self.bob_pub_box.text()))
        pub_bob_layout.addWidget(self.bob_pub_box)
        pub_bob_layout.addWidget(self.bob_pub_copy_btn)
        bob_layout.addLayout(pub_bob_layout)

        bob_layout.addWidget(QLabel("Shared Secret:"))
        shared_bob_layout = QHBoxLayout()
        self.bob_shared_box = self._readonly_box()
        self.bob_shared_copy_btn = QPushButton("📋")
        self.bob_shared_copy_btn.setMaximumWidth(40)
        self.bob_shared_copy_btn.clicked.connect(lambda: self._copy_to_clipboard(self.bob_shared_box.text()))
        shared_bob_layout.addWidget(self.bob_shared_box)
        shared_bob_layout.addWidget(self.bob_shared_copy_btn)
        bob_layout.addLayout(shared_bob_layout)

        bob_layout.addWidget(QLabel("Software Time (ms):"))
        self.bob_time_box = self._readonly_box()
        bob_layout.addWidget(self.bob_time_box)

        bob_group.setLayout(bob_layout)
        panels_layout.addWidget(bob_group)

        main_layout.addLayout(panels_layout)

        # -----------------------------
        # Controls
        # -----------------------------
        controls_layout = QHBoxLayout()

        # Show private keys checkbox
        self.show_private_checkbox = QCheckBox("Show Private Keys")
        self.show_private_checkbox.stateChanged.connect(self.toggle_private_keys)
        controls_layout.addWidget(self.show_private_checkbox)

        controls_layout.addStretch()

        # Start button
        self.start_btn = QPushButton("Start Secure Key Exchange")
        self.start_btn.clicked.connect(self.start_exchange)
        self.start_btn.setStyleSheet("padding: 10px; font-weight: bold;")
        controls_layout.addWidget(self.start_btn)

        # Reset button
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset_state)
        controls_layout.addWidget(self.reset_btn)

        # Record metrics button
        self.record_metrics_btn = QPushButton("📊 Record Metrics")
        self.record_metrics_btn.setEnabled(False)
        self.record_metrics_btn.clicked.connect(self.record_metrics)
        controls_layout.addWidget(self.record_metrics_btn)

        main_layout.addLayout(controls_layout)

        # Status label
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("padding: 5px; color: green;")
        main_layout.addWidget(self.status_label)

    # -----------------------------
    # Helpers
    # -----------------------------
    def _readonly_box(self):
        box = QLineEdit()
        box.setReadOnly(True)
        box.setStyleSheet("font-family: monospace;")
        box.setPlaceholderText("[Not generated]")
        return box

    def _copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        if text and not text.startswith("["):
            QApplication.clipboard().setText(text)
            self.status_label.setText("✅ Copied to clipboard!")
            self.status_label.setStyleSheet("color: green; padding: 5px;")

    def log(self, text):
        """Add message to log"""
        self.log_box.append(text)

    def toggle_private_keys(self, state):
        """Show or hide private keys"""
        if state == Qt.Checked:
            # Show actual keys
            if self.alice_private:
                self.alice_priv_box.setText(self.alice_private.hex().upper())
            if self.bob_private:
                self.bob_priv_box.setText(self.bob_private.hex().upper())
        else:
            # Hide with lock icon
            if self.alice_private:
                self.alice_priv_box.setText("[🔒 Hidden]")
            if self.bob_private:
                self.bob_priv_box.setText("[🔒 Hidden]")

    # -----------------------------
    # Start Process
    # -----------------------------
    def start_exchange(self):
        """Start the key exchange process"""
        try:
            self.reset_state()
            
            # Disable button during operation
            self.start_btn.setEnabled(False)
            self.start_btn.setText("Operation in progress...")
            self.start_btn.setStyleSheet("padding: 10px; font-weight: bold; background-color: #CCCCCC;")
            
            self.exchange_status.setText("Generating private keys...")
            self.exchange_status.setStyleSheet("padding: 10px; color: blue;")
            self.arrow_label.setStyleSheet("font-size: 48px; color: #CCCCCC;")
            
            self.log("[1] 🔑 Generating private keys on FPGA...")
            self.status_label.setText("Status: Generating keys...")
            self.status_label.setStyleSheet("color: blue; padding: 5px;")
            
            self.current_step = 1
            self.controller.fpga_operation(op="rng")
            
        except Exception as e:
            self.log(f"❌ Error starting exchange: {e}")
            self.start_btn.setEnabled(True)
            self.start_btn.setText("Start Secure Key Exchange")
            self.status_label.setText(f"Status: Error - {e}")
            self.status_label.setStyleSheet("color: red; padding: 5px;")

    def reset_state(self):
        """Reset all state and UI"""
        self.log_box.clear()
        
        # Clear boxes
        self.alice_priv_box.clear()
        self.alice_pub_box.clear()
        self.alice_shared_box.clear()
        self.bob_priv_box.clear()
        self.bob_pub_box.clear()
        self.bob_shared_box.clear()
        self.alice_time_box.clear()
        self.bob_time_box.clear()
        
        # Reset styles
        self.alice_priv_box.setStyleSheet("font-family: monospace;")
        self.alice_pub_box.setStyleSheet("font-family: monospace;")
        self.alice_shared_box.setStyleSheet("font-family: monospace;")
        self.bob_priv_box.setStyleSheet("font-family: monospace;")
        self.bob_pub_box.setStyleSheet("font-family: monospace;")
        self.bob_shared_box.setStyleSheet("font-family: monospace;")
        
        # Reset placeholders
        self.alice_priv_box.setPlaceholderText("[Not generated]")
        self.alice_pub_box.setPlaceholderText("[Not generated]")
        self.alice_shared_box.setPlaceholderText("[Not computed]")
        self.bob_priv_box.setPlaceholderText("[Not generated]")
        self.bob_pub_box.setPlaceholderText("[Not generated]")
        self.bob_shared_box.setPlaceholderText("[Not computed]")

        # Reset state
        self.current_step = 0
        self.alice_private = None
        self.bob_private = None
        self.alice_public = None
        self.bob_public = None
        self.alice_shared = None
        self.bob_shared = None
        
        # Reset timing
        self.fpga_total_time = 0
        self.software_total_time = 0
        
        # Reset visual
        self.exchange_status.setText("Ready to start exchange")
        self.exchange_status.setStyleSheet("padding: 10px; color: gray;")
        self.arrow_label.setStyleSheet("font-size: 48px; color: #CCCCCC;")
        
        # Re-enable buttons
        self.start_btn.setEnabled(True)
        self.start_btn.setText("Start Secure Key Exchange")
        self.start_btn.setStyleSheet("padding: 10px; font-weight: bold;")
        self.record_metrics_btn.setEnabled(False)
        self.record_metrics_btn.setStyleSheet("")
        
        # Reset status
        self.status_label.setText("Status: Ready")
        self.status_label.setStyleSheet("color: green; padding: 5px;")

    # -----------------------------
    # RNG Handler
    # -----------------------------
    def handle_rng(self, key1: bytes, key2: bytes):
        """Handle RNG result (private keys)"""
        try:
            if self.current_step != 1:
                return

            self.alice_private = key1 
            self.bob_private = key2

            # Display based on checkbox state
            if self.show_private_checkbox.isChecked():
                self.alice_priv_box.setText(key1.hex().upper())
                self.bob_priv_box.setText(key2.hex().upper())
            else:
                self.alice_priv_box.setText("[🔒 Hidden]")
                self.bob_priv_box.setText("[🔒 Hidden]")

            self.log("[2] 📤 Computing Alice's public key on FPGA...")
            self.exchange_status.setText("Computing Alice's public key...")
            self.status_label.setText("Status: Computing Alice's public key...")
            
            self.current_step = 2
            self.fpga_start_time = time.perf_counter()


            reversed_key1 = bytes(reversed(key1))

            self.controller.fpga_operation(
                op="keyexchange",
                kx_private=reversed_key1,
                kx_public=b"\x00"*31 + b"\x09"
            )
            
        except Exception as e:
            self.log(f"❌ Error handling RNG: {e}")
            self.start_btn.setEnabled(True)
            self.start_btn.setText("Start Secure Key Exchange")

    # -----------------------------
    # FPGA Result Handler
    # -----------------------------
    def handle_fpga_result(self, result: bytes):
        """Handle FPGA key exchange result"""
        #result is returned in big endian, we convert it to little endian here. 
        result = bytes(reversed(result))
        try:
            if self.current_step == 2:
                # Alice public key received
                
                self.alice_public = result
                self.alice_pub_box.setText(result.hex().upper())

                self.alice_public_time = (time.perf_counter() - self.fpga_start_time) * 1000
                self.alice_time_box.setText(f"{self.alice_public_time:.2f}")

                self.log("[3] 📤 Computing Bob's public key in Software...")
                self.exchange_status.setText("Computing Bob's public key...")
                self.status_label.setText("Status: Computing Bob's public key...")
                
                self.current_step = 3

                sw_start = time.perf_counter()

                result = self.controller.software_operation(
                    op="keyexchange",
                    kx_private=self.bob_private,
                    kx_public=b"\x09" + b"\x00"*31
                )

                self.bob_public_time = (time.perf_counter() - sw_start) * 1000
                self.bob_time_box.setText(f"{self.bob_public_time:.2f}")

                self.bob_public = result
                self.bob_pub_box.setText(result.hex().upper())

                self.log("[4] 🔄 Exchanging public keys...")
                self.exchange_status.setText("Exchanging public keys...\nAlice ⇄ Bob")
                self.exchange_status.setStyleSheet("padding: 10px; color: green; font-weight: bold;")
                self.arrow_label.setStyleSheet("font-size: 48px; color: #4CAF50;")
                
                self.log("[5] 🔐 Computing Alice's shared secret on FPGA...")
                self.status_label.setText("Status: Computing shared secrets...")
                
                self.current_step = 4
                self.fpga_start_time = time.perf_counter()

                reveresed_alice_private = bytes(reversed(self.alice_private))
                reveresed_bob_public = bytes(reversed(self.bob_public))
                self.controller.fpga_operation(
                    op="keyexchange",
                    kx_private=reveresed_alice_private,
                    kx_public=reveresed_bob_public
                )

            elif self.current_step == 4:
                # Alice shared secret received
                self.alice_shared = result
                self.alice_shared_box.setText(result.hex().upper())

                self.alice_shared_time = (time.perf_counter() - self.fpga_start_time) * 1000
                self.alice_time_box.setText(f"{self.alice_public_time + self.alice_shared_time:.2f}")

                self.log("[6] 🔐 Computing Bob's shared secret in Software...")
                self.current_step = 5

                sw_start = time.perf_counter()

                result = self.controller.software_operation(
                    op="keyexchange",
                    kx_private=self.bob_private,
                    kx_public=self.alice_public
                )

                self.bob_shared_time = (time.perf_counter() - sw_start) * 1000
                self.bob_time_box.setText(f"{self.bob_public_time + self.bob_shared_time:.2f}")

                self.bob_shared = result
                self.bob_shared_box.setText(result.hex().upper())

                self.verify()
                
        except Exception as e:
            self.log(f"❌ Error handling FPGA result: {e}")
            self.start_btn.setEnabled(True)
            self.start_btn.setText("Start Secure Key Exchange")
            self.status_label.setText(f"Status: Error - {e}")
            self.status_label.setStyleSheet("color: red; padding: 5px;")

    # -----------------------------
    # Verification
    # -----------------------------
    def verify(self):
        """Verify that shared secrets match"""
        try:
            self.log("[7] ✓ Verifying shared secrets...")

            if self.alice_shared == self.bob_shared:
                # SUCCESS!
                self.log("✅ SUCCESS! Secure Channel Established")
                self.log(f"   Shared Secret: {self.alice_shared.hex().upper()}")
                
                # Visual feedback - green background
                self.alice_shared_box.setStyleSheet("background-color: #90EE90; font-family: monospace; font-weight: bold;")
                self.bob_shared_box.setStyleSheet("background-color: #90EE90; font-family: monospace; font-weight: bold;")
                
                # Update exchange visual
                self.exchange_status.setText("✅ Secure Channel Established!\nShared secrets MATCH")
                self.exchange_status.setStyleSheet("padding: 10px; color: green; font-weight: bold;")
                self.arrow_label.setText("✓")
                self.arrow_label.setStyleSheet("font-size: 64px; color: #4CAF50;")
                
                # Status
                self.status_label.setText("✅ Status: Secure channel established!")
                self.status_label.setStyleSheet("color: green; font-weight: bold; padding: 5px;")
                
                # Calculate total times
                self.fpga_total_time = self.alice_public_time + self.alice_shared_time
                self.software_total_time = self.bob_public_time + self.bob_shared_time
                
                # Enable metrics button
                self.record_metrics_btn.setEnabled(True)
                self.record_metrics_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
                
            else:
                # MISMATCH!
                self.log("❌ ERROR! Shared Secret Mismatch")
                self.log(f"   Alice: {self.alice_shared.hex().upper()}")
                self.log(f"   Bob:   {self.bob_shared.hex().upper()}")
                
                # Visual feedback - red background
                self.alice_shared_box.setStyleSheet("background-color: #FFB6C1; font-family: monospace;")
                self.bob_shared_box.setStyleSheet("background-color: #FFB6C1; font-family: monospace;")
                
                # Update exchange visual
                self.exchange_status.setText("❌ Secrets DO NOT MATCH!\nExchange FAILED")
                self.exchange_status.setStyleSheet("padding: 10px; color: red; font-weight: bold;")
                self.arrow_label.setText("✗")
                self.arrow_label.setStyleSheet("font-size: 64px; color: #FF5252;")
                
                # Status
                self.status_label.setText("❌ Status: Exchange failed - secrets mismatch")
                self.status_label.setStyleSheet("color: red; font-weight: bold; padding: 5px;")

            # Re-enable start button
            self.start_btn.setEnabled(True)
            self.start_btn.setText("Start Secure Key Exchange")
            self.start_btn.setStyleSheet("padding: 10px; font-weight: bold;")
            
        except Exception as e:
            self.log(f"❌ Error during verification: {e}")
            self.status_label.setText(f"Status: Verification error - {e}")
            self.status_label.setStyleSheet("color: red; padding: 5px;")

    # -----------------------------
    # Metrics Recording
    # -----------------------------
    def record_metrics(self):
        """Record metrics to metrics page"""
        if not (self.alice_shared and self.bob_shared):
            return
        
        try:
            # Record metric via controller
            self.controller.record_metric({
                "operation": "keyexchange",
                "data_size": 32,  # 32-byte keys
                "mode": "Curve25519",
                "key_size": 256,
                "direction": "exchange",
                "fpga_time_ms": self.fpga_total_time,
                "software_time_ms": self.software_total_time,
            })
            
            self.log("📊 Metrics recorded to dashboard!")
            self.status_label.setText("✅ Status: Metrics recorded!")
            self.status_label.setStyleSheet("color: green; padding: 5px;")
            
            # Reset metrics button
            self.record_metrics_btn.setEnabled(False)
            self.record_metrics_btn.setStyleSheet("")
            
        except Exception as e:
            self.log(f"❌ Error recording metrics: {e}")