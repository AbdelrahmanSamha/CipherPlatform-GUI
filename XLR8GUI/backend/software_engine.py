import hashlib
import binascii
from Crypto.Cipher import AES as CryptoAES
from Crypto.Util.Padding import pad, unpad

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
        """
        Modified version - works directly with hex strings
        
        Args:
            single_block: 32 hex character string (128 bits)
        
        Returns:
            dict: {"rounds": [...], "final": "..."}
        """
        key = self.config["key"]  # hex string
        iv = self.config["iv"] if self.config["iv"] else None  # hex string or None
        
        
        aes = AES(key)
        
        if self.config["direction"] == "enc":
            return aes.encrypt_block_mode(single_block, self.config["mode"], iv)
        else:
            return aes.decrypt_block_mode(single_block, self.config["mode"], iv)

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
    def stream_operation(self, stream_text=None, stream_in_path=None, 
                        stream_out_path=None, stream_is_hex=None, 
                        stream_out_hex=None):
        """
        Perform streaming cipher operation in software using pycryptodome.
        
        Args:
            stream_text: Text data to process (if text mode)
            stream_in_path: Input file path (if file mode)
            stream_out_path: Output file path where result will be written
            stream_is_hex: Whether input is hex format (True/False)
            stream_out_hex: Whether output should be hex format (True/False)
        
        Returns:
            dict: {"output": "processed_data", "status": "success"}
        """
        
        print("\n" + "="*60)
        print("SOFTWARE STREAM OPERATION")
        print("="*60)
        
        # Get configuration
        key_hex = self.config["key"]
        iv_hex = self.config["iv"]
        mode = self.config["mode"].upper()
        direction = self.config["direction"]
        
        print(f"Mode: {mode}")
        print(f"Direction: {direction}")
        print(f"Key: {key_hex}")
        print(f"IV: {iv_hex}")
        print(f"Input is hex: {stream_is_hex}")
        print(f"Output as hex: {stream_out_hex}")
        
        # Convert key and IV from hex to bytes
        key_bytes = bytes.fromhex(key_hex)
        iv_bytes = bytes.fromhex(iv_hex) if iv_hex else None
        
        # -------------------------
        # GET INPUT DATA
        # -------------------------
        if stream_text is not None:
            print(f"\n[INPUT] Processing text input ({len(stream_text)} chars)")
            
            if stream_is_hex:
                # Input is hex string - convert to bytes
                print("[INPUT] Format: HEX")
                try:
                    input_bytes = bytes.fromhex(stream_text.replace(" ", "").replace("\n", ""))
                except ValueError as e:
                    print(f"[ERROR] Invalid hex input: {e}")
                    return None
            else:
                # Input is ASCII - encode to bytes
                print("[INPUT] Format: ASCII")
                input_bytes = stream_text.encode('utf-8')
            
            print(f"[INPUT] Input bytes length: {len(input_bytes)}")
        
        elif stream_in_path is not None:
            print(f"\n[INPUT] Processing file: {stream_in_path}")
            
            if stream_is_hex:
                # File contains hex text
                print("[INPUT] Format: HEX file")
                with open(stream_in_path, 'r') as f:
                    hex_data = f.read().replace(" ", "").replace("\n", "")
                try:
                    input_bytes = bytes.fromhex(hex_data)
                except ValueError as e:
                    print(f"[ERROR] Invalid hex in file: {e}")
                    return None
            else:
                # File contains binary/ASCII data
                print("[INPUT] Format: Binary file")
                with open(stream_in_path, 'rb') as f:
                    input_bytes = f.read()
            
            print(f"[INPUT] File bytes length: {len(input_bytes)}")
        
        else:
            print("[ERROR] No input provided")
            return None
        
        # -------------------------
        # PERFORM ENCRYPTION/DECRYPTION
        # -------------------------
        print(f"\n[CIPHER] Performing {direction.upper()}")
        
        try:
            if direction == "enc":
                # ENCRYPTION
                
                # Pad the input (PKCS7 padding to 16-byte blocks)
                padded_input = pad(input_bytes, CryptoAES.block_size)
                print(f"[CIPHER] After padding: {len(padded_input)} bytes")
                
                # Create cipher based on mode
                if mode == "ECB":
                    cipher = CryptoAES.new(key_bytes, CryptoAES.MODE_ECB)
                elif mode == "CBC":
                    if not iv_bytes:
                        print("[ERROR] CBC mode requires IV")
                        return None
                    cipher = CryptoAES.new(key_bytes, CryptoAES.MODE_CBC, iv=iv_bytes)
                elif mode == "CFB":
                    if not iv_bytes:
                        print("[ERROR] CFB mode requires IV")
                        return None
                    cipher = CryptoAES.new(key_bytes, CryptoAES.MODE_CFB, iv=iv_bytes, segment_size=128)
                elif mode == "OFB":
                    if not iv_bytes:
                        print("[ERROR] OFB mode requires IV")
                        return None
                    cipher = CryptoAES.new(key_bytes, CryptoAES.MODE_OFB, iv=iv_bytes)
                elif mode == "CTR":
                    if not iv_bytes:
                        print("[ERROR] CTR mode requires nonce")
                        return None
                    # CTR uses nonce, we'll use IV as nonce
                    from Crypto.Util import Counter
                    # Create counter starting from IV
                    ctr = Counter.new(128, initial_value=int.from_bytes(iv_bytes, 'big'))
                    cipher = CryptoAES.new(key_bytes, CryptoAES.MODE_CTR, counter=ctr)
                else:
                    print(f"[ERROR] Unknown mode: {mode}")
                    return None
                
                # Encrypt
                output_bytes = cipher.encrypt(padded_input)
                print(f"[CIPHER] Encrypted: {len(output_bytes)} bytes")
            
            else:
                # DECRYPTION
                
                # Create cipher based on mode
                if mode == "ECB":
                    cipher = CryptoAES.new(key_bytes, CryptoAES.MODE_ECB)
                elif mode == "CBC":
                    if not iv_bytes:
                        print("[ERROR] CBC mode requires IV")
                        return None
                    cipher = CryptoAES.new(key_bytes, CryptoAES.MODE_CBC, iv=iv_bytes)
                elif mode == "CFB":
                    if not iv_bytes:
                        print("[ERROR] CFB mode requires IV")
                        return None
                    cipher = CryptoAES.new(key_bytes, CryptoAES.MODE_CFB, iv=iv_bytes, segment_size=128)
                elif mode == "OFB":
                    if not iv_bytes:
                        print("[ERROR] OFB mode requires IV")
                        return None
                    cipher = CryptoAES.new(key_bytes, CryptoAES.MODE_OFB, iv=iv_bytes)
                elif mode == "CTR":
                    if not iv_bytes:
                        print("[ERROR] CTR mode requires nonce")
                        return None
                    from Crypto.Util import Counter
                    ctr = Counter.new(128, initial_value=int.from_bytes(iv_bytes, 'big'))
                    cipher = CryptoAES.new(key_bytes, CryptoAES.MODE_CTR, counter=ctr)
                else:
                    print(f"[ERROR] Unknown mode: {mode}")
                    return None
                
                # Decrypt
                decrypted_padded = cipher.decrypt(input_bytes)
                print(f"[CIPHER] Decrypted (padded): {len(decrypted_padded)} bytes")
                
                # Unpad the result
                try:
                    output_bytes = unpad(decrypted_padded, CryptoAES.block_size)
                    print(f"[CIPHER] After unpadding: {len(output_bytes)} bytes")
                except ValueError as e:
                    print(f"[ERROR] Unpadding failed: {e}")
                    # Return without unpadding if it fails
                    output_bytes = decrypted_padded
        
        except Exception as e:
            print(f"[ERROR] Cipher operation failed: {e}")
            return None
        
        # -------------------------
        # FORMAT OUTPUT
        # -------------------------
        print(f"\n[OUTPUT] Formatting output")
        
        if stream_out_hex:
            # Output as hex string
            final_output = output_bytes.hex()
            print(f"[OUTPUT] Format: HEX ({len(final_output)} chars)")
        else:
            # Output as ASCII
            try:
                final_output = output_bytes.decode('utf-8', errors='replace')
                print(f"[OUTPUT] Format: ASCII ({len(final_output)} chars)")
            except:
                # Fallback to latin-1 if UTF-8 fails
                final_output = output_bytes.decode('latin-1', errors='replace')
                print(f"[OUTPUT] Format: ASCII (latin-1 fallback)")
        
        # -------------------------
        # WRITE TO FILE
        # -------------------------
        print(f"[OUTPUT] Writing to: {stream_out_path}")
        
        try:
            with open(stream_out_path, 'w') as f:
                f.write(final_output)
            print(f"[OUTPUT] ✅ File write successful")
        except Exception as e:
            print(f"[OUTPUT] ❌ File write error: {e}")
            return None
        
        # -------------------------
        # RETURN RESULT
        # -------------------------
        print("="*60)
        print("STREAM OPERATION COMPLETE")
        print("="*60 + "\n")
        
        # Return first 1000 chars for GUI display (to avoid huge text)
        return {
            "output": final_output[:1000] + ("..." if len(final_output) > 1000 else ""),
            "status": "success",
            "output_path": stream_out_path,
            "output_length": len(final_output)
        }