from ui.main_window import MainWindow
from PySide6.QtCore import QObject, Signal
from backend.fpga import FPGA
from backend.data_processing import DataProcessing
from backend.software_engine import SoftwareEngine 
import serial
import threading


class AppController(QObject):
    """
    This class connects:
    GUI  <->  FPGA / backend logic

    The GUI never talks to UART directly.
    """
    config_updated = Signal(dict)
    uart_status_updated = Signal(bool, str)     # all pages
    uart_blocklab_page_received = Signal(bytes)   
    uart_test_page_received = Signal(bytes)
    uart_stream_page_received = Signal(bytes)
    uart_rng_page_received = Signal(bytes, bytes)
    uart_image_page_received = Signal(bytes)
    uart_sha_page_received = Signal(bytes)
    def __init__(self):
        super().__init__()

        self.config = {
            "mode": None,
            "key_size": None,
            "key": None,
            "iv": None, 
            "direction": "enc"
        }

        self.main_window = None
        self.serial = None
        self.read_thread = None
        self.running = False
        self.current_page = None
        self.last_page = None   # track last page to flush buffer on page change

        # specific things for streampage
        self.stream_buffer = b''
        self.stream_expected_len = 0
        self.stream_output_path = None

        # for image header 
        self.image_header = None

        #for SHA 
        self.sha_outhex = None
        self.sha_expected_len = None

        # persistent UART buffer
        self.serial_buffer = b''
        self.start_reading_event = threading.Event()
        self.data_processing = DataProcessing(self.config)


        self.fpga = FPGA(controller=self)
        self.software_engine = SoftwareEngine(controller=self)
        
    def show_main_window(self):
        self.main_window = MainWindow(controller=self)
        self.main_window.show()
    
    def set_config(self, config):
        self.config.update(config) 
        self.config_updated.emit(config)

    def fpga_operation(self, op=None,test_byte_tx= None, block_lab=None, stream_text=None, stream_in_path=None, stream_out_path=None, stream_is_hex=None,
                       sha_text=None, sha_in_path=None, sha_is_hex=None): 
        if not op :
            print("failed FPGA operation, no op is selected") 
            return  
        print("NEW OPERATIOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOON")
        self.start_reading_event.clear()
        # Flush the buffer when starting a new operation
        print(f"newop,before flush buffer value : {self.serial_buffer.hex()}")
        if self.serial:
            self.serial.reset_input_buffer()
            print(f"some condition idk what it does--: {self.serial_buffer.hex()}")
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
            # dummy read to drain CP2102 FIFO
            while self.serial.in_waiting:
                dummy = self.serial.read(self.serial.in_waiting)
                print(f"drained data: {dummy.hex()}")
            
        
        self.serial_buffer = b''
        self.stream_buffer = b''
        self.stream_expected_len = 0
        self.stream_output_path = None
        print(f"newop, current buffer value after flush: {self.serial_buffer.hex()}")
        
        if op == "block_lab": 
            self.current_page = "block_lab" 
            self.fpga.block_lab_operation(block_lab)
            

        elif op == "stream": 
            self.current_page = "stream" 
            self.fpga.stream_operation(
                text_data=stream_text,
                input_path=stream_in_path,
                output_path=stream_out_path,
                is_hex=stream_is_hex
            )
            
        elif op == "image":
            self.current_page = "image"
            self.fpga.image_operation(
                input_path=stream_in_path,
                output_path=stream_out_path
            )

        elif op =="rng": 
            self.current_page = "rng"
            self.fpga.rng_operation(mode=self.config["mode"], key_size=self.config["key_size"])
            
        elif op =="sha256": 
            self.current_page = "sha"
            self.fpga.sha_operation(text=sha_text, in_path=sha_in_path, is_hex=sha_is_hex)
        elif op == "test": 
            self.fpga.test_byte(test_byte_tx = test_byte_tx)
            self.current_page = "test"
        print("setting the read thread. ")
        self.start_reading_event.set()
        return True

    ####################################################################
    def software_operation(self, op=None, block_lab=None, sha_text=None, sha_in_path=None, sha_is_hex=None, sha_out_hex=None):
        """
        Perform software-side operations.

        Returns:
            dict with results depending on operation
        """

        if not op:
            print("❌ No software operation specified")
            return None

        # -------------------------
        # BLOCK LAB
        # -------------------------
        if op == "block_lab":
            return self.software_engine.block_lab_operation(block_lab)

        # -------------------------
        # SHA256
        # -------------------------
        elif op =="sha256": 
            return self.software_engine.hash_sha256(sha_text, sha_in_path, sha_is_hex, sha_out_hex)
        # -------------------------
        # UNKNOWN OP
        # -------------------------
        print(f"❌ Unknown software operation: {op}")
        return None

        
    # -----------------------------
    # UART handling
    # -----------------------------
    def open_uart(self, port):
        try:
            self.serial = serial.Serial(
                port=port,
                baudrate=921600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )

            self.running = True
            self.read_thread = threading.Thread(
                target=self.read_loop,
                daemon=True
            )
            self.read_thread.start()

            self.uart_status_updated.emit(True, port)

        except serial.SerialException:
            self.serial = None
            self.uart_status_updated.emit(False, None)

    def close_uart(self):
        self.running = False
        if self.serial:
            try:
                self.serial.close()
            except:
                pass
            self.serial = None

        self.uart_status_updated.emit(False, None)

    # -----------------------------
    # Send data
    # -----------------------------
    def send_bytes(self, data: bytes):
        if not self.serial:
            return False
        try:
            
            self.serial.write(data)
            
            return True
        except:
            return False

    # -----------------------------
    # Background read loop 
    # -----------------------------
    def read_loop(self):
        while self.running and self.serial:
            self.start_reading_event.wait()
            try:
                # flush buffer if page changed
                #if self.current_page != self.last_page:
                #    self.serial_buffer = b''
                #    self.last_page = self.current_page
                #    print(f"page changed, current buffer value : {self.serial_buffer.hex()}")
                #print("Listening on UART...")
                #print(f"in waiting: {self.serial.in_waiting}")
                data = self.serial.read(1)
                if not data:
                    continue
                #print(self.serial.in_waiting)
                print(f"data: {data.hex()}")
                # accumulate
                self.serial_buffer += data
                print (f"buffer data: {self.serial_buffer.hex()}")



                # -------------------------
                # BLOCK LAB PAGE
                # -------------------------
                if self.current_page == "block_lab":
                    
                    while len(self.serial_buffer) >= 16:
                        block = self.serial_buffer[:16]
                        self.serial_buffer = self.serial_buffer[16:]
                        self.uart_blocklab_page_received.emit(block)
                        print("we are in the while loop for some reason. ")

                # -------------------------
                # TEST PAGE
                # -------------------------
                elif self.current_page == "test":
                    print(f"received: {self.serial_buffer.hex()}")
                    while len(self.serial_buffer) >= 1:
                        block = self.serial_buffer[:1]
                        self.serial_buffer = self.serial_buffer[1:]
                        self.uart_test_page_received.emit(block)

                # -------------------------
                # STREAM PAGE
                # -------------------------
                elif self.current_page == "stream":
                    print(f"received: {self.serial_buffer.hex()}")
                    while len(self.serial_buffer) >= 16:
                        block = self.serial_buffer[:16]
                        self.serial_buffer = self.serial_buffer[16:]
                        self.stream_buffer += block
                        print("we are in the while loop for some reason. ")

                        if len(self.stream_buffer) >= self.stream_expected_len:
                            result = self.stream_buffer
                            if self.config["direction"] == "dec":
                                result = self.data_processing.pkcs7_unpad(result)
                                
                                    

                            if self.stream_output_path:
                                self.data_processing.write_file(self.stream_output_path, result)
                            else:
                                print(f"emitted signal")
                                self.uart_stream_page_received.emit(result)
                            # Reset stream state
                            self.stream_buffer = b''
                            self.stream_expected_len = 0
                            self.stream_output_path = None
                            
                # -------------------------
                # IMAGE PAGE
                # -------------------------
                elif self.current_page == "image":
                    # Make sure we know the expected length
                    if not self.stream_expected_len or not hasattr(self.controller, "image_header"):
                        continue  # wait until image_operation set these

                    while len(self.serial_buffer) >= 16:  # process in 16-byte chunks
                        block = self.serial_buffer[:16]
                        self.serial_buffer = self.serial_buffer[16:]
                        self.stream_buffer += block

                        # Check if full image data received
                        if len(self.stream_buffer) >= self.stream_expected_len:
                            result = self.stream_buffer

                            # Decrypt if needed
                            if self.config["direction"] == "dec":
                                result = self.data_processing.pkcs7_unpad(result)

                            # Reconstruct BMP with original header
                            bmp_bytes = self.controller.image_header + result

                            # Write to file if path exists
                            if self.stream_output_path:
                                self.data_processing.write_file(self.stream_output_path, bmp_bytes)
                            else:
                                # Emit signal to page to show preview
                                self.uart_image_page_received.emit(bmp_bytes)

                            # Reset stream state
                            self.stream_buffer = b''
                            self.stream_expected_len = 0
                            self.stream_output_path = None
            
                # -------------------------
                # SHA PAGE
                # -------------------------
                elif self.current_page == "sha":
                    print(f"received SHA data: {self.serial_buffer.hex()}")
                    
                    while len(self.serial_buffer) >= 32:  # SHA-256 output is 32 bytes
                        sha_block = self.serial_buffer[:32]
                        self.serial_buffer = self.serial_buffer[32:]
                        self.uart_sha_page_received.emit(sha_block)
                        print(f"emitted SHA block: {sha_block.hex()}")               
                            

                # -------------------------
                # RNG PAGE
                # -------------------------
                elif self.current_page == "rng":
                    ks_inbytes = {"128": 16, "192": 24, "256": 32}.get(self.config["key_size"])
                    if ks_inbytes is None:
                        continue

                    total_len = ks_inbytes + 16  # key + IV
                    while len(self.serial_buffer) >= total_len:
                        packet = self.serial_buffer[:total_len]
                        self.serial_buffer = self.serial_buffer[total_len:]
                        key = packet[:ks_inbytes]
                        iv = packet[ks_inbytes:]
                        self.uart_rng_page_received.emit(key, iv)

            except Exception as e:
                print(f"UART read error: {e}")

    # ---- PLACEHOLDERS FOR FUTURE ----
    def start_block_encryption(self):
        print("[Controller] Start block encryption")
        # TODO:
        # 1. Prepare FPGA
        # 2. Send commands over UART
        # 3. Receive ACK
        # 4. Update UI

    def reset_fpga(self):
        print("[Controller] Reset FPGA")
