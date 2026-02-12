from copy import deepcopy


"""
AES Encryption/Decryption with Round Tracking
Supports: ECB, CBC, CFB, OFB, CTR modes
Key sizes: 128, 192, 256 bits
"""

class AES:
    # ========================================
    # PLACEHOLDERS - PASTE YOUR VALUES HERE
    # ========================================
    SBOX = [
    0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
    0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
    0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
    0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
    0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
    0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
    0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
    0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
    0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
    0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
    0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
    0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
    0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
    0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
    0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16
    ]
    
    INV_SBOX = [
    0x52,0x09,0x6a,0xd5,0x30,0x36,0xa5,0x38,0xbf,0x40,0xa3,0x9e,0x81,0xf3,0xd7,0xfb,
    0x7c,0xe3,0x39,0x82,0x9b,0x2f,0xff,0x87,0x34,0x8e,0x43,0x44,0xc4,0xde,0xe9,0xcb,
    0x54,0x7b,0x94,0x32,0xa6,0xc2,0x23,0x3d,0xee,0x4c,0x95,0x0b,0x42,0xfa,0xc3,0x4e,
    0x08,0x2e,0xa1,0x66,0x28,0xd9,0x24,0xb2,0x76,0x5b,0xa2,0x49,0x6d,0x8b,0xd1,0x25,
    0x72,0xf8,0xf6,0x64,0x86,0x68,0x98,0x16,0xd4,0xa4,0x5c,0xcc,0x5d,0x65,0xb6,0x92,
    0x6c,0x70,0x48,0x50,0xfd,0xed,0xb9,0xda,0x5e,0x15,0x46,0x57,0xa7,0x8d,0x9d,0x84,
    0x90,0xd8,0xab,0x00,0x8c,0xbc,0xd3,0x0a,0xf7,0xe4,0x58,0x05,0xb8,0xb3,0x45,0x06,
    0xd0,0x2c,0x1e,0x8f,0xca,0x3f,0x0f,0x02,0xc1,0xaf,0xbd,0x03,0x01,0x13,0x8a,0x6b,
    0x3a,0x91,0x11,0x41,0x4f,0x67,0xdc,0xea,0x97,0xf2,0xcf,0xce,0xf0,0xb4,0xe6,0x73,
    0x96,0xac,0x74,0x22,0xe7,0xad,0x35,0x85,0xe2,0xf9,0x37,0xe8,0x1c,0x75,0xdf,0x6e,
    0x47,0xf1,0x1a,0x71,0x1d,0x29,0xc5,0x89,0x6f,0xb7,0x62,0x0e,0xaa,0x18,0xbe,0x1b,
    0xfc,0x56,0x3e,0x4b,0xc6,0xd2,0x79,0x20,0x9a,0xdb,0xc0,0xfe,0x78,0xcd,0x5a,0xf4,
    0x1f,0xdd,0xa8,0x33,0x88,0x07,0xc7,0x31,0xb1,0x12,0x10,0x59,0x27,0x80,0xec,0x5f,
    0x60,0x51,0x7f,0xa9,0x19,0xb5,0x4a,0x0d,0x2d,0xe5,0x7a,0x9f,0x93,0xc9,0x9c,0xef,
    0xa0,0xe0,0x3b,0x4d,0xae,0x2a,0xf5,0xb0,0xc8,0xeb,0xbb,0x3c,0x83,0x53,0x99,0x61,
    0x17,0x2b,0x04,0x7e,0xba,0x77,0xd6,0x26,0xe1,0x69,0x14,0x63,0x55,0x21,0x0c,0x7d
    ]
    
    # Rcon values for key expansion
    RCON = [
        0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40,
        0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a
    ]
    
    def __init__(self, key_hex):
        """
        Initialize AES cipher
        
        Args:
            key_hex: Key as hex string (32, 48, or 64 chars for 128/192/256 bit keys)
        """
        print(f"\n=== AES INIT ===")
        print(f"Key (hex): {key_hex}")
        print(f"Key length: {len(key_hex)} chars = {len(key_hex)*4} bits")
        
        self.key_hex = key_hex
        self.key_size = len(key_hex) * 4  # bits
        
        # Determine rounds based on key size
        if self.key_size == 128:
            self.num_rounds = 10
            self.nk = 4  # Number of 32-bit words in key
        elif self.key_size == 192:
            self.num_rounds = 12
            self.nk = 6
        elif self.key_size == 256:
            self.num_rounds = 14
            self.nk = 8
        else:
            raise ValueError(f"Invalid key size: {self.key_size} bits. Must be 128, 192, or 256.")
        
        print(f"Number of rounds: {self.num_rounds}")
        
        # Expand the key
        self.round_keys = self._key_expansion()
        print(f"Key expansion complete: {len(self.round_keys)} round keys generated")
        print("================\n")
    
    def _key_expansion(self):
        """Expand the cipher key into round keys"""
        # Convert hex key to list of integers
        key_bytes = [int(self.key_hex[i:i+2], 16) for i in range(0, len(self.key_hex), 2)]
        
        # Total number of words needed: (num_rounds + 1) * 4
        total_words = (self.num_rounds + 1) * 4
        
        # Initialize with original key words
        w = []
        for i in range(self.nk):
            w.append([key_bytes[4*i], key_bytes[4*i+1], key_bytes[4*i+2], key_bytes[4*i+3]])
        
        # Expand to fill remaining words
        for i in range(self.nk, total_words):
            temp = w[i-1][:]
            
            if i % self.nk == 0:
                # RotWord
                temp = temp[1:] + temp[:1]
                # SubWord
                temp = [self.SBOX[b] for b in temp]
                # XOR with Rcon
                temp[0] ^= self.RCON[i // self.nk]
            elif self.nk > 6 and i % self.nk == 4:
                # Extra SubWord for 256-bit keys
                temp = [self.SBOX[b] for b in temp]
            
            # XOR with word nk positions earlier
            w.append([w[i-self.nk][j] ^ temp[j] for j in range(4)])
        
        # Convert words to round keys (each round key is 16 bytes)
        round_keys = []
        for round_num in range(self.num_rounds + 1):
            round_key = []
            for col in range(4):
                round_key.extend(w[round_num * 4 + col])
            round_keys.append(round_key)
        
        return round_keys
    
    # ========================================
    # STATE CONVERSION HELPERS
    # ========================================
    
    def _hex_to_state(self, hex_string):
        """Convert 32-char hex string to 4x4 state matrix (column-major order)"""
        print(f"[DEBUG] Converting hex to state: {hex_string}")
        
        # Convert to bytes
        bytes_list = [int(hex_string[i:i+2], 16) for i in range(0, 32, 2)]
        
        # Create 4x4 state matrix in COLUMN-major order
        # AES processes data in columns
        state = [[0]*4 for _ in range(4)]
        for i in range(16):
            row = i % 4
            col = i // 4
            state[row][col] = bytes_list[i]
        
        print(f"[DEBUG] State matrix:")
        for row in state:
            print(f"  {' '.join(f'{b:02x}' for b in row)}")
        
        return state
    
    def _state_to_hex(self, state):
        """Convert 4x4 state matrix to 32-char hex string (column-major order)"""
        hex_string = ""
        for col in range(4):
            for row in range(4):
                hex_string += f"{state[row][col]:02x}"
        
        print(f"[DEBUG] State to hex: {hex_string}")
        return hex_string
    
    # ========================================
    # AES CORE OPERATIONS
    # ========================================
    
    def _add_round_key(self, state, round_key):
        """XOR state with round key"""
        for col in range(4):
            for row in range(4):
                state[row][col] ^= round_key[col * 4 + row]
        return state
    
    def _sub_bytes(self, state):
        """Apply S-box substitution"""
        for row in range(4):
            for col in range(4):
                state[row][col] = self.SBOX[state[row][col]]
        return state
    
    def _inv_sub_bytes(self, state):
        """Apply inverse S-box substitution"""
        for row in range(4):
            for col in range(4):
                state[row][col] = self.INV_SBOX[state[row][col]]
        return state
    
    def _shift_rows(self, state):
        """Shift rows (row i shifted left by i positions)"""
        state[1] = state[1][1:] + state[1][:1]  # Shift row 1 by 1
        state[2] = state[2][2:] + state[2][:2]  # Shift row 2 by 2
        state[3] = state[3][3:] + state[3][:3]  # Shift row 3 by 3
        return state
    
    def _inv_shift_rows(self, state):
        """Inverse shift rows (row i shifted right by i positions)"""
        state[1] = state[1][-1:] + state[1][:-1]  # Shift row 1 right by 1
        state[2] = state[2][-2:] + state[2][:-2]  # Shift row 2 right by 2
        state[3] = state[3][-3:] + state[3][:-3]  # Shift row 3 right by 3
        return state
    
    def _gmul(self, a, b):
        """Galois field multiplication"""
        p = 0
        for _ in range(8):
            if b & 1:
                p ^= a
            hi_bit_set = a & 0x80
            a <<= 1
            if hi_bit_set:
                a ^= 0x1b  # AES irreducible polynomial
            b >>= 1
        return p & 0xff
    
    def _mix_columns(self, state):
        """Mix columns transformation"""
        for col in range(4):
            s0, s1, s2, s3 = state[0][col], state[1][col], state[2][col], state[3][col]
            
            state[0][col] = self._gmul(s0, 2) ^ self._gmul(s1, 3) ^ s2 ^ s3
            state[1][col] = s0 ^ self._gmul(s1, 2) ^ self._gmul(s2, 3) ^ s3
            state[2][col] = s0 ^ s1 ^ self._gmul(s2, 2) ^ self._gmul(s3, 3)
            state[3][col] = self._gmul(s0, 3) ^ s1 ^ s2 ^ self._gmul(s3, 2)
        
        return state
    
    def _inv_mix_columns(self, state):
        """Inverse mix columns transformation"""
        for col in range(4):
            s0, s1, s2, s3 = state[0][col], state[1][col], state[2][col], state[3][col]
            
            state[0][col] = self._gmul(s0, 14) ^ self._gmul(s1, 11) ^ self._gmul(s2, 13) ^ self._gmul(s3, 9)
            state[1][col] = self._gmul(s0, 9) ^ self._gmul(s1, 14) ^ self._gmul(s2, 11) ^ self._gmul(s3, 13)
            state[2][col] = self._gmul(s0, 13) ^ self._gmul(s1, 9) ^ self._gmul(s2, 14) ^ self._gmul(s3, 11)
            state[3][col] = self._gmul(s0, 11) ^ self._gmul(s1, 13) ^ self._gmul(s2, 9) ^ self._gmul(s3, 14)
        
        return state
    
    # ========================================
    # CORE BLOCK ENCRYPTION/DECRYPTION
    # ========================================
    
    def encrypt_block(self, block_hex):
        """
        Encrypt a single block and return all round states
        
        Args:
            block_hex: 32-char hex string (128 bits)
        
        Returns:
            dict: {"rounds": ["round0", "round1", ..., "roundN"], "final": "final_output"}
        """
        print(f"\n{'='*60}")
        print(f"ENCRYPTING BLOCK: {block_hex}")
        print(f"{'='*60}")
        
        state = self._hex_to_state(block_hex)
        rounds_output = []
        
        # Initial round (round 0) - just AddRoundKey
        print(f"\n--- ROUND 0 (Initial AddRoundKey) ---")
        state = self._add_round_key(state, self.round_keys[0])
        round0_hex = self._state_to_hex(state)
        rounds_output.append(round0_hex)
        print(f"After AddRoundKey: {round0_hex}")
        
        # Main rounds (1 to num_rounds-1)
        for round_num in range(1, self.num_rounds):
            print(f"\n--- ROUND {round_num} ---")
            
            state = self._sub_bytes(state)
            print(f"After SubBytes: {self._state_to_hex(state)}")
            
            state = self._shift_rows(state)
            print(f"After ShiftRows: {self._state_to_hex(state)}")
            
            state = self._mix_columns(state)
            print(f"After MixColumns: {self._state_to_hex(state)}")
            
            state = self._add_round_key(state, self.round_keys[round_num])
            round_hex = self._state_to_hex(state)
            rounds_output.append(round_hex)
            print(f"After AddRoundKey: {round_hex}")
        
        # Final round (no MixColumns)
        print(f"\n--- ROUND {self.num_rounds} (Final) ---")
        state = self._sub_bytes(state)
        print(f"After SubBytes: {self._state_to_hex(state)}")
        
        state = self._shift_rows(state)
        print(f"After ShiftRows: {self._state_to_hex(state)}")
        
        state = self._add_round_key(state, self.round_keys[self.num_rounds])
        final_hex = self._state_to_hex(state)
        rounds_output.append(final_hex)
        print(f"After AddRoundKey (FINAL): {final_hex}")
        
        print(f"\n{'='*60}")
        print(f"ENCRYPTION COMPLETE")
        print(f"{'='*60}\n")
        
        return {
            "rounds": rounds_output,
            "final": final_hex
        }
    
    def decrypt_block(self, block_hex):
        """
        Decrypt a single block and return all round states
        
        Args:
            block_hex: 32-char hex string (128 bits)
        
        Returns:
            dict: {"rounds": ["round0", "round1", ..., "roundN"], "final": "final_output"}
        """
        print(f"\n{'='*60}")
        print(f"DECRYPTING BLOCK: {block_hex}")
        print(f"{'='*60}")
        
        state = self._hex_to_state(block_hex)
        rounds_output = []
        
        # Initial round - AddRoundKey with last round key
        print(f"\n--- ROUND 0 (Initial AddRoundKey) ---")
        state = self._add_round_key(state, self.round_keys[self.num_rounds])
        round0_hex = self._state_to_hex(state)
        rounds_output.append(round0_hex)
        print(f"After AddRoundKey: {round0_hex}")
        
        # Main rounds (in reverse)
        for round_num in range(self.num_rounds - 1, 0, -1):
            print(f"\n--- ROUND {self.num_rounds - round_num} ---")
            
            state = self._inv_shift_rows(state)
            print(f"After InvShiftRows: {self._state_to_hex(state)}")
            
            state = self._inv_sub_bytes(state)
            print(f"After InvSubBytes: {self._state_to_hex(state)}")
            
            state = self._add_round_key(state, self.round_keys[round_num])
            print(f"After AddRoundKey: {self._state_to_hex(state)}")
            
            state = self._inv_mix_columns(state)
            round_hex = self._state_to_hex(state)
            rounds_output.append(round_hex)
            print(f"After InvMixColumns: {round_hex}")
        
        # Final round (no InvMixColumns)
        print(f"\n--- ROUND {self.num_rounds} (Final) ---")
        state = self._inv_shift_rows(state)
        print(f"After InvShiftRows: {self._state_to_hex(state)}")
        
        state = self._inv_sub_bytes(state)
        print(f"After InvSubBytes: {self._state_to_hex(state)}")
        
        state = self._add_round_key(state, self.round_keys[0])
        final_hex = self._state_to_hex(state)
        rounds_output.append(final_hex)
        print(f"After AddRoundKey (FINAL): {final_hex}")
        
        print(f"\n{'='*60}")
        print(f"DECRYPTION COMPLETE")
        print(f"{'='*60}\n")
        
        return {
            "rounds": rounds_output,
            "final": final_hex
        }
    
    # ========================================
    # BLOCK CIPHER MODES
    # ========================================
    
    def _xor_blocks(self, block1_hex, block2_hex):
        """XOR two hex blocks"""
        b1 = [int(block1_hex[i:i+2], 16) for i in range(0, 32, 2)]
        b2 = [int(block2_hex[i:i+2], 16) for i in range(0, 32, 2)]
        result = [b1[i] ^ b2[i] for i in range(16)]
        return ''.join(f'{b:02x}' for b in result)
    
    def _increment_counter(self, counter_hex):
        """Increment a counter block (for CTR mode)"""
        counter_int = int(counter_hex, 16)
        counter_int = (counter_int + 1) % (2**128)
        return f"{counter_int:032x}"
    
    def encrypt_block_mode(self, block_hex, mode, iv_hex=None):
        """
        Encrypt block with specified mode
        
        Args:
            block_hex: 32-char hex string
            mode: "ECB", "CBC", "CFB", "OFB", or "CTR"
            iv_hex: 32-char hex IV (required for CBC, CFB, OFB, CTR)
        
        Returns:
            dict: {"rounds": [...], "final": "..."}
        """
        mode = mode.upper()
        print(f"\n*** ENCRYPTION MODE: {mode} ***")
        
        if mode == "ECB":
            # Electronic Codebook - direct encryption
            return self.encrypt_block(block_hex)
        
        elif mode == "CBC":
            # Cipher Block Chaining
            if not iv_hex:
                raise ValueError("CBC mode requires IV")
            xored = self._xor_blocks(block_hex, iv_hex)
            print(f"After XOR with IV: {xored}")
            return self.encrypt_block(xored)
        
        elif mode == "CFB":
            # Cipher Feedback
            if not iv_hex:
                raise ValueError("CFB mode requires IV")
            encrypted_iv = self.encrypt_block(iv_hex)
            result_hex = self._xor_blocks(block_hex, encrypted_iv["final"])
            return {
                "rounds": encrypted_iv["rounds"],
                "final": result_hex
            }
        
        elif mode == "OFB":
            # Output Feedback
            if not iv_hex:
                raise ValueError("OFB mode requires IV")
            encrypted_iv = self.encrypt_block(iv_hex)
            result_hex = self._xor_blocks(block_hex, encrypted_iv["final"])
            return {
                "rounds": encrypted_iv["rounds"],
                "final": result_hex
            }
        
        elif mode == "CTR":
            # Counter mode
            if not iv_hex:
                raise ValueError("CTR mode requires counter/nonce")
            encrypted_counter = self.encrypt_block(iv_hex)
            result_hex = self._xor_blocks(block_hex, encrypted_counter["final"])
            return {
                "rounds": encrypted_counter["rounds"],
                "final": result_hex
            }
        
        else:
            raise ValueError(f"Unknown mode: {mode}")
    
    def decrypt_block_mode(self, block_hex, mode, iv_hex=None):
        """
        Decrypt block with specified mode
        
        Args:
            block_hex: 32-char hex string
            mode: "ECB", "CBC", "CFB", "OFB", or "CTR"
            iv_hex: 32-char hex IV (required for CBC, CFB, OFB, CTR)
        
        Returns:
            dict: {"rounds": [...], "final": "..."}
        """
        mode = mode.upper()
        print(f"\n*** DECRYPTION MODE: {mode} ***")
        
        if mode == "ECB":
            # Electronic Codebook - direct decryption
            return self.decrypt_block(block_hex)
        
        elif mode == "CBC":
            # Cipher Block Chaining
            if not iv_hex:
                raise ValueError("CBC mode requires IV")
            decrypted = self.decrypt_block(block_hex)
            result_hex = self._xor_blocks(decrypted["final"], iv_hex)
            return {
                "rounds": decrypted["rounds"],
                "final": result_hex
            }
        
        elif mode == "CFB":
            # Cipher Feedback (encryption and decryption are the same)
            if not iv_hex:
                raise ValueError("CFB mode requires IV")
            encrypted_iv = self.encrypt_block(iv_hex)
            result_hex = self._xor_blocks(block_hex, encrypted_iv["final"])
            return {
                "rounds": encrypted_iv["rounds"],
                "final": result_hex
            }
        
        elif mode == "OFB":
            # Output Feedback (encryption and decryption are the same)
            if not iv_hex:
                raise ValueError("OFB mode requires IV")
            encrypted_iv = self.encrypt_block(iv_hex)
            result_hex = self._xor_blocks(block_hex, encrypted_iv["final"])
            return {
                "rounds": encrypted_iv["rounds"],
                "final": result_hex
            }
        
        elif mode == "CTR":
            # Counter mode (encryption and decryption are the same)
            if not iv_hex:
                raise ValueError("CTR mode requires counter/nonce")
            encrypted_counter = self.encrypt_block(iv_hex)
            result_hex = self._xor_blocks(block_hex, encrypted_counter["final"])
            return {
                "rounds": encrypted_counter["rounds"],
                "final": result_hex
            }
        
        else:
            raise ValueError(f"Unknown mode: {mode}")