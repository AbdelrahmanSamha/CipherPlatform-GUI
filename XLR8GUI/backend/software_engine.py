import hashlib
import binascii
from backend.aes import AES
class SoftwareEngine:
    """
    Wrapper for software-based encryption.
    Keeps the same interface as the hardware cipher.
    """

    def __init__(self, controller):
        """
        cipher: instance of AES, DES, etc.
        """
        self.controller = controller
        self.config = controller.config
        self.dp = controller.data_processing 

    def block_lab_operation(self, single_block):
        key = bytes.fromhex(self.config["key"])
        iv = bytes.fromhex(self.config["iv"]) if self.config["iv"] else None
        aes = AES(key)

        blk_bytes = bytes.fromhex(single_block)
        if self.config["direction"]=="enc":
            return aes.encrypt_block_mode(blk_bytes, self.config["mode"], iv)
        else:
            return aes.decrypt_block_mode(blk_bytes, self.config["mode"], iv)

    # ---------------------------------------------------
    # SHA256 Hashing
    # ---------------------------------------------------
    def hash_sha256(self, sha_text, sha_in_path, sha_is_hex, sha_out_hex):
        """
        sha_text: text input from GUI
        sha_in_path: optional file input path
        sha_is_hex: whether input text is hex
        sha_out_hex: whether output should be hex or ASCII
        """
        # -----------------------------------------
        # Get input data
        # -----------------------------------------
        if sha_in_path:
            # File input
            if sha_is_hex:
                # File contains hex text
                with open(sha_in_path, "r") as f:
                    hex_text = f.read().strip()
                try:
                    data = binascii.unhexlify(hex_text)
                except Exception:
                    raise ValueError("Invalid hex input in file for SHA256")
            else:
                # Raw binary file
                with open(sha_in_path, "rb") as f:
                    data = f.read()
        else:
            # Text input
            if sha_text is None:
                data = b""
            else:
                if sha_is_hex:
                    # Interpret text as hex
                    try:
                        data = binascii.unhexlify(sha_text.strip())
                    except Exception:
                        raise ValueError("Invalid hex input for SHA256")
                else:
                    # Normal ASCII/UTF-8 text
                    data = sha_text.encode("utf-8")

        # -----------------------------------------
        # Perform SHA256
        # -----------------------------------------
        hasher = hashlib.sha256()
        hasher.update(data)
        digest_bytes = hasher.digest()
        digest_hex = hasher.hexdigest().upper()

        # -----------------------------------------
        # Prepare output
        # -----------------------------------------
        if sha_out_hex:
            output = digest_hex
        else:
            # ASCII-style output (raw bytes decoded safely)
            output = digest_bytes.decode("latin-1", errors="replace")

        return {
            "hash_hex": digest_hex,
            "hash_out": output
        }