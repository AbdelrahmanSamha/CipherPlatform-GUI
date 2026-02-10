class DataProcessing:
    def __init__(self, config):
        self.config = config

    def hex_to_bytes(self, value):
        """Convert hex string or bytes to bytes."""
        if value is None:
            return None

        if isinstance(value, bytes):
            return value

        if isinstance(value, str):
            value = value.replace(" ", "")
            return bytes.fromhex(value)

        raise TypeError("Unsupported data type")

    def get_key_bytes(self):
        #print(f"config in the dp class: {self.config}")
        key = self.config.get("key")
        return self.hex_to_bytes(key)

    def get_block_bytes(self, block):
        return self.hex_to_bytes(block)

    def get_iv_bytes(self):
        iv = self.config.get("iv")
        return self.hex_to_bytes(iv)

    def bits_to_byte(self, bits: str) -> bytes:
        """
        Convert a string of 8 bits (e.g., '10101010') into a single byte.
        Raises ValueError if the string is not exactly 8 bits or contains invalid characters.
        """
        if len(bits) != 8:
            raise ValueError("Input must be exactly 8 bits")
        if any(b not in "01" for b in bits):
            raise ValueError("Input must contain only '0' or '1' characters")

        byte_value = int(bits, 2)
        return bytes([byte_value])




    def get_stream_bytes(self, data, is_hex=False):
        if isinstance(data, bytes):
            return data

        if is_hex:
            return self.hex_to_bytes(data)

        if isinstance(data, str):
            return data.encode("utf-8")

        raise TypeError("Unsupported stream data type")

    # -------------------------
    # FILE FUNCTIONS
    # -------------------------

    def read_file(self, path, is_hex=False):
        """
        Read file contents.
        """
        with open(path, "rb") as f:
            content = f.read()

        if is_hex:
            content = content.decode().replace(" ", "")
            return bytes.fromhex(content)

        return content

    def write_file(self, path, data, as_hex=False):
        """
        Write output to file.
        """
        if as_hex:
            with open(path, "w") as f:
                f.write(data.hex())
        else:
            with open(path, "wb") as f:
                f.write(data)

    # -------------------------
    # PADDING
    # -------------------------

    def pkcs7_pad(self, data: bytes, block_size=16) -> bytes:
        pad_len = block_size - (len(data) % block_size)
        if pad_len == 0:
            pad_len = block_size
        return data + bytes([pad_len] * pad_len)

    def pkcs7_unpad(self, data: bytes, block_size=16) -> bytes:
        if not data or len(data) % block_size != 0:
            raise ValueError("Invalid padded data length")

        pad_len = data[-1]

        if pad_len < 1 or pad_len > block_size:
            raise ValueError("Invalid padding")

        if data[-pad_len:] != bytes([pad_len] * pad_len):
            raise ValueError("Invalid padding pattern")

        return data[:-pad_len]