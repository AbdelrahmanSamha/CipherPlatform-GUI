#controll the operations sent to the FPGA. can be done serially. 

class FPGA: 
    def __init__(self, controller): 
        self.controller = controller 
        self.config = controller.config
        self.dp = controller.data_processing  

    def block_lab_operation(self, single_block):
        # ----------------- Send command -----------------
        some_cmd = self.dp.bits_to_byte("00000010")
        self.controller.send_bytes(some_cmd)
        print(f"sent byte: {some_cmd.hex()}")

        # ----------------- build flags byte -----------------
        mode_map = {
            "ECB": 0b000,
            "CTR": 0b001,
            "CBC": 0b010,
            "CFB": 0b011,
            "OFB": 0b100,
        }

        mode_bits = mode_map.get(self.config["mode"], 0)
        dir_bit = 1 if self.config["direction"] == "dec" else 0
        
        # Get key size bits (bits 7-6)
        key_size_bits = self.dp.get_key_size_bits()
        
        # Build flags: [key_size(2) | unused(2) | dir(1) | mode(3)]
        flags_val = (key_size_bits << 6) | (dir_bit << 3) | mode_bits
        flags = bytes([flags_val])

        self.controller.send_bytes(flags)
        print(f"sent byte: {flags_val:02X}")

        # ----------------- send length -----------------
        length = self.dp.bits_to_byte("00010000")  # 16 bytes
        self.controller.send_bytes(length)
        print(f"sent byte: {length.hex()}")

        # ----------------- Process and send key (ALWAYS 256 bits = 32 bytes) -----------------
        key_bytes = self.dp.get_padded_key_bytes()  # Use padded key
        print("about to print the key bytes:")
        for byte in key_bytes:
            self.controller.send_bytes(bytes([byte]))
            print(f"sent byte: {byte:02X}")

        # ----------------- send iv if needed -----------------
        if self.config["mode"] in ["CBC", "CTR", "CFB", "OFB"]:
            iv_bytes = self.dp.get_iv_bytes()
            for byte in iv_bytes:
                self.controller.send_bytes(bytes([byte]))
                print(f"sent byte: {byte:02X}")
                
        # ----------------- Process and send block -----------------
        block_bytes = self.dp.get_block_bytes(single_block)
        print("about to print the data bytes:")
        for byte in block_bytes:
            self.controller.send_bytes(bytes([byte]))
            print(f"sent byte: {byte:02X}")

    def test_byte(self, test_byte_tx: bytes): 
        self.controller.send_bytes(test_byte_tx)


    def stream_operation(self,
                        text_data=None,
                        input_path=None,
                        output_path=None,
                        is_hex=False):
        """
        text_data: text from GUI
        input_path: file path (if used)
        output_path: where to store result
        is_hex: whether input is hex
        """

        # remember output destination
        self.controller.stream_output_path = output_path
        self.controller.stream_buffer = b''

        # ----------------- operation code -----------------
        stream_cmd = self.dp.bits_to_byte("00000001")
        self.controller.send_bytes(stream_cmd)
        print(f"sent byte: {stream_cmd.hex()}")

        # ----------------------------- get stream data -----------------------------
        if input_path:
            stream_bytes = self.dp.read_file(input_path, is_hex)
        else:
            stream_bytes = self.dp.get_stream_bytes(text_data, is_hex)

        
        if self.config["direction"] == "enc":
            stream_bytes = self.dp.pkcs7_pad(stream_bytes)
            print(f"Padding applied : {stream_bytes.hex()}")

        total_len = len(stream_bytes)

        # ----------------------------- determine number of length bytes -----------------------------
        if total_len <= 0xFF:
            length_bytes_count = 1
        elif total_len <= 0xFFFF:
            length_bytes_count = 2
        elif total_len <= 0xFFFFFF:
            length_bytes_count = 3
        else:
            length_bytes_count = 4

        # ----------------------------- build flags byte -----------------------------
        mode_map = {
            "ECB": 0b000,
            "CTR": 0b001,
            "CBC": 0b010,
            "CFB": 0b011,
            "OFB": 0b100,
        }
        mode_bits = mode_map.get(self.config["mode"], 0)
        dir_bit = 0 if self.config["direction"] == "enc" else 1
        length_size_bits = (length_bytes_count - 1) & 0b11
        
        # NEW: Get key size bits (bits 7-6)
        key_size_bits = self.dp.get_key_size_bits()
        
        # Build flags: [key_size(2) | length_size(2) | dir(1) | mode(3)]
        flags_val = (key_size_bits << 6) | (length_size_bits << 4) | (dir_bit << 3) | mode_bits
        flags = bytes([flags_val])

        # ----------------- send flags -----------------
        for byte in flags:
            self.controller.send_bytes(bytes([byte]))
            print(f"sent byte: {byte:02X}")

        # ----------------- send length bytes (MSB first) -----------------
        length_bytes = total_len.to_bytes(length_bytes_count, byteorder="big")
        for byte in length_bytes:
            self.controller.send_bytes(bytes([byte]))
            print(f"sent byte: {byte:02X}")

        # store expected length
        self.controller.stream_expected_len = total_len

        # ----------------- send key (ALWAYS 256 bits = 32 bytes) -----------------
        print("about to print the key bytes:")
        key_bytes = self.dp.get_padded_key_bytes()  # NEW: Use padded key
        for byte in key_bytes:
            self.controller.send_bytes(bytes([byte]))
            print(f"sent byte: {byte:02X}")

        # ----------------- send IV if needed -----------------
        if self.config["mode"] in ["CBC", "CTR", "CFB", "OFB"]:
            iv_bytes = self.dp.get_iv_bytes()
            for byte in iv_bytes:
                self.controller.send_bytes(bytes([byte]))
                print(f"sent byte: {byte:02X}")

        # ----------------- send stream data -----------------
        print("about to print the data bytes:")
        for byte in stream_bytes:
            self.controller.send_bytes(bytes([byte]))
            print(f"sent byte: {byte:02X}")


    def image_operation(self, input_path=None, output_path=None):
        """
        Send an image to the FPGA for encryption/decryption.

        input_path: path to the prepared BMP (from ImagePage)
        output_path: where to store the received result (handled by read thread)
        """

        if not input_path:
            print("❌ No input path provided")
            return

        # Remember output destination
        self.controller.stream_output_path = output_path
        self.controller.stream_buffer = b''

        # ----------------- Read BMP -----------------
        with open(input_path, "rb") as f:
            bmp_bytes = f.read()

        # BMP header is usually 54 bytes
        header_len = 54
        header = bmp_bytes[:header_len]
        pixel_data = bmp_bytes[header_len:]

        # Store header in controller for later use
        self.controller.image_header = header

        # ----------------- Apply padding to pixel data -----------------
        if self.config["direction"] == "enc":
            pixel_data = self.dp.pkcs7_pad(pixel_data)

        total_len = len(pixel_data)

        # ----------------- Determine number of length bytes -----------------
        if total_len <= 0xFF:
            length_bytes_count = 1
        elif total_len <= 0xFFFF:
            length_bytes_count = 2
        elif total_len <= 0xFFFFFF:
            length_bytes_count = 3
        else:
            length_bytes_count = 4

        # ----------------- Build flags byte -----------------
        mode_map = {
            "ECB": 0b000,
            "CTR": 0b001,
            "CBC": 0b010,
            "CFB": 0b011,
            "OFB": 0b100,
        }
        mode_bits = mode_map.get(self.config["mode"], 0)
        dir_bit = 0 if self.config["direction"] == "enc" else 1
        length_size_bits = (length_bytes_count - 1) & 0b11
        
        # NEW: Get key size bits (bits 7-6)
        key_size_bits = self.dp.get_key_size_bits()
        
        # Build flags: [key_size(2) | length_size(2) | dir(1) | mode(3)]
        flags_val = (key_size_bits << 6) | (length_size_bits << 4) | (dir_bit << 3) | mode_bits
        flags = bytes([flags_val])

        # ----------------- Send command -----------------
        img_cmd = self.dp.bits_to_byte("00000001")
        self.controller.send_bytes(img_cmd)
        print(f"sent byte: {img_cmd.hex()}")

        # ----------------- Send flags -----------------
        for byte in flags:
            self.controller.send_bytes(bytes([byte]))
            print(f"sent flag byte: {byte:02X}")

        # ----------------- Send length bytes (MSB first) -----------------
        length_bytes = total_len.to_bytes(length_bytes_count, byteorder="big")
        for byte in length_bytes:
            self.controller.send_bytes(bytes([byte]))
            print(f"sent length byte: {byte:02X}")

        # ----------------- Store expected length -----------------
        self.controller.stream_expected_len = total_len

        # ----------------- Send key (ALWAYS 256 bits = 32 bytes) -----------------
        print("about to send key bytes:")
        key_bytes = self.dp.get_padded_key_bytes()  # NEW: Use padded key
        for byte in key_bytes:
            self.controller.send_bytes(bytes([byte]))
            print(f"sent key byte: {byte:02X}")

        # ----------------- Send IV/Nonce if needed -----------------
        if self.config["mode"] in ["CBC", "CTR", "CFB", "OFB"]:
            iv_bytes = self.dp.get_iv_bytes()
            for byte in iv_bytes:
                self.controller.send_bytes(bytes([byte]))
                print(f"sent IV byte: {byte:02X}")

        # ----------------- Send pixel data -----------------
        print("about to send pixel data bytes:")
        for byte in pixel_data:
            self.controller.send_bytes(bytes([byte]))
            print(f"sent data byte: {byte:02X}")




    def rng_operation(self, mode, key_size ):

        pass 



    def sha_operation(self, text=None, in_path=None, is_hex=False):
        """
        Send a SHA-256 operation to the FPGA.

        text: text input from GUI
        in_path: optional file input
        is_hex: whether input is hex
        """

        # ----------------- prepare output -----------------
        self.controller.stream_output_path = None  # not used for SHA
        self.controller.stream_buffer = b''

        # ----------------- operation code -----------------
        sha_cmd = self.dp.bits_to_byte("00000002")  # SHA operation command
        self.controller.send_bytes(sha_cmd)
        print(f"sent byte: {sha_cmd.hex()}")

        # ----------------- get input data -----------------
        if in_path:
            data_bytes = self.dp.read_file(in_path, is_hex)
        else:
            data_bytes = self.dp.get_stream_bytes(text, is_hex)

        # ----------------- SHA-256 padding (512-bit / 64-byte blocks) -----------------
        bit_len = len(data_bytes) * 8
        data_bytes += b'\x80'  # append '1' bit
        pad_len = (56 - (len(data_bytes) % 64)) % 64
        data_bytes += b'\x00' * pad_len
        data_bytes += bit_len.to_bytes(8, "big")  # append original length in bits

        total_chunks = len(data_bytes) // 64  # number of 512-bit chunks
        print(f"Padded data length: {len(data_bytes)} bytes, total_chunks: {total_chunks}")

        
        if total_chunks <= 0xFF:
            length_bytes_count = 1
        elif total_chunks <= 0xFFFF:
            length_bytes_count = 2
        elif total_chunks <= 0xFFFFFF:
            length_bytes_count = 3
        else:
            raise ValueError("Message too long for SHA operation")

        # ----------------- build flags byte -----------------
        # Bits 7-6 unused (0), bits 5-4 = length_bytes_count-1, bits 3-0 unused (0)
        flags_bits_54 = (length_bytes_count - 1) & 0b11
        flags_val = (flags_bits_54 << 4)
        flags = bytes([flags_val])

        # ----------------- send flags -----------------
        for byte in flags:
            self.controller.send_bytes(bytes([byte]))
            print(f"sent byte: {byte:02X}")

        # ----------------- send length bytes (MSB-first) -----------------
        length_bytes = total_chunks.to_bytes(length_bytes_count, "big")
        for byte in length_bytes:
            self.controller.send_bytes(bytes([byte]))
            print(f"sent byte: {byte:02X}")

        # ----------------- send SHA-256 data bytes -----------------
        print("about to print SHA-256 data bytes:")
        for byte in data_bytes:
            self.controller.send_bytes(bytes([byte]))
            print(f"sent byte: {byte:02X}")

        # store expected length in bytes (useful for verification later)
        self.controller.sha_expected_len = len(data_bytes)