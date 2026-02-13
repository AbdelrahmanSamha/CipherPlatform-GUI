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
        """Get key bytes from config."""
        key = self.config.get("key")
        return self.hex_to_bytes(key)
    
    # ==================== NEW KEY SIZE METHODS ====================
    
    def get_key_size(self):
        """
        Get the key size in bits (128, 192, or 256).
        
        Returns:
            int: Key size in bits
        """
        key_bytes = self.get_key_bytes()
        key_len = len(key_bytes)
        
        if key_len == 16:
            return 128
        elif key_len == 24:
            return 192
        elif key_len == 32:
            return 256
        else:
            raise ValueError(f"Invalid key size: {key_len} bytes. Must be 16, 24, or 32 bytes.")
    
    def get_key_size_bits(self):
        """
        Get the 2-bit encoding for key size.
        
        Returns:
            int: 0b00 for 128-bit, 0b01 for 192-bit, 0b10 for 256-bit
        """
        key_size = self.get_key_size()
        
        if key_size == 128:
            return 0b00
        elif key_size == 192:
            return 0b01
        elif key_size == 256:
            return 0b10
        else:
            raise ValueError(f"Unsupported key size: {key_size}")
    
    def get_padded_key_bytes(self):
        """
        Get key bytes padded to 256 bits (32 bytes).
        
        - 128-bit key: 16 bytes of zeros + 16 bytes of key
        - 192-bit key: 8 bytes of zeros + 24 bytes of key
        - 256-bit key: 32 bytes of key (no padding)
        
        Returns:
            bytes: 32-byte padded key
        """
        key_bytes = self.get_key_bytes()
        key_len = len(key_bytes)
        
        if key_len == 16:
            # 128-bit key: pad with 16 zeros at the start
            return b'\x00' * 16 + key_bytes
        elif key_len == 24:
            # 192-bit key: pad with 8 zeros at the start
            return b'\x00' * 8 + key_bytes
        elif key_len == 32:
            # 256-bit key: no padding needed
            return key_bytes
        else:
            raise ValueError(f"Invalid key size: {key_len} bytes")
    
    # ==================== END NEW METHODS ====================

    def get_block_bytes(self, block):
        """Get block bytes."""
        return self.hex_to_bytes(block)

    def get_iv_bytes(self):
        """Get IV bytes from config."""
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
        """Get stream bytes from data."""
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
        """Read file contents."""
        with open(path, "rb") as f:
            content = f.read()

        if is_hex:
            content = content.decode().replace(" ", "")
            return bytes.fromhex(content)

        return content

    def write_file(self, path, data, as_hex=False):
        """Write output to file."""
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
        """Apply PKCS7 padding."""
        pad_len = block_size - (len(data) % block_size)
        if pad_len == 0:
            pad_len = block_size
        return data + bytes([pad_len] * pad_len)

    def pkcs7_unpad(self, data: bytes, block_size=16) -> bytes:
        """Remove PKCS7 padding."""
        if not data or len(data) % block_size != 0:
            raise ValueError("Invalid padded data length")

        pad_len = data[-1]

        if pad_len < 1 or pad_len > block_size:
            raise ValueError("Invalid padding")

        if data[-pad_len:] != bytes([pad_len] * pad_len):
            raise ValueError("Invalid padding pattern")

        return data[:-pad_len]