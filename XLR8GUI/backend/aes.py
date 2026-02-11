from copy import deepcopy

# -----------------------------
# PASTE S-BOX TABLES HERE
# -----------------------------
s_box = [
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
inv_s_box = [
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

# Rcon values for key expansion (as bytes, not words)
Rcon = (
    0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40,
    0x80, 0x1B, 0x36, 0x6C, 0xD8, 0xAB, 0x4D, 0x9A,
    0x2F, 0x5E, 0xBC, 0x63, 0xC6, 0x97, 0x35, 0x6A,
    0xD4, 0xB3, 0x7D, 0xFA, 0xEF, 0xC5, 0x91, 0x39,
)

# -----------------------------
# AES helper functions
# -----------------------------
def xtime(a):
    """Multiply by x in GF(2^8)."""
    return ((a << 1) ^ 0x1B) & 0xFF if a & 0x80 else (a << 1)

def sub_bytes(state):
    """Apply S-box substitution to each byte."""
    return [s_box[b] for b in state]

def inv_sub_bytes(state):
    """Apply inverse S-box substitution to each byte."""
    return [inv_s_box[b] for b in state]

def shift_rows(state):
    """Shift rows of the state (column-major representation)."""
    new_state = state[:]
    # Row 1: shift left by 1
    new_state[1], new_state[5], new_state[9], new_state[13] = state[5], state[9], state[13], state[1]
    # Row 2: shift left by 2
    new_state[2], new_state[6], new_state[10], new_state[14] = state[10], state[14], state[2], state[6]
    # Row 3: shift left by 3
    new_state[3], new_state[7], new_state[11], new_state[15] = state[15], state[3], state[7], state[11]
    return new_state

def inv_shift_rows(state):
    """Inverse shift rows of the state."""
    new_state = state[:]
    # Row 1: shift right by 1
    new_state[1], new_state[5], new_state[9], new_state[13] = state[13], state[1], state[5], state[9]
    # Row 2: shift right by 2 (same as left by 2)
    new_state[2], new_state[6], new_state[10], new_state[14] = state[10], state[14], state[2], state[6]
    # Row 3: shift right by 3
    new_state[3], new_state[7], new_state[11], new_state[15] = state[7], state[11], state[15], state[3]
    return new_state

def add_round_key(state, round_key):
    """XOR state with round key."""
    return [b ^ rk for b, rk in zip(state, round_key)]

def mix_single_column(a):
    """Mix a single column (operates on 4-byte column in-place)."""
    t = a[0] ^ a[1] ^ a[2] ^ a[3]
    u = a[0]
    a[0] ^= t ^ xtime(a[0] ^ a[1])
    a[1] ^= t ^ xtime(a[1] ^ a[2])
    a[2] ^= t ^ xtime(a[2] ^ a[3])
    a[3] ^= t ^ xtime(a[3] ^ u)
    return a

def mix_columns(state):
    """Apply MixColumns transformation."""
    state = state[:]
    for i in range(4):
        # Extract column i (4 consecutive bytes starting at index i*4)
        col = [state[i * 4], state[i * 4 + 1], state[i * 4 + 2], state[i * 4 + 3]]
        col = mix_single_column(col)
        state[i * 4] = col[0]
        state[i * 4 + 1] = col[1]
        state[i * 4 + 2] = col[2]
        state[i * 4 + 3] = col[3]
    return state

def inv_mix_columns(state):
    """Apply inverse MixColumns transformation."""
    state = state[:]
    for i in range(4):
        # Extract column i
        col = [state[i * 4], state[i * 4 + 1], state[i * 4 + 2], state[i * 4 + 3]]
        
        u = xtime(xtime(col[0] ^ col[2]))
        v = xtime(xtime(col[1] ^ col[3]))
        col[0] ^= u
        col[1] ^= v
        col[2] ^= u
        col[3] ^= v
        
        col = mix_single_column(col)
        
        state[i * 4] = col[0]
        state[i * 4 + 1] = col[1]
        state[i * 4 + 2] = col[2]
        state[i * 4 + 3] = col[3]
    return state

def state_to_hex(state):
    """Convert column-major state to row-major hex string (for display)."""
    out = [0] * 16
    for i in range(16):
        out[(i % 4) * 4 + (i // 4)] = state[i]
    return ''.join(f"{b:02X}" for b in out)

# -----------------------------
# AES class
# -----------------------------
class AES:
    def __init__(self, key: bytes):
        """Initialize AES with the given key (128, 192, or 256 bits)."""
        self.key = key
        self.Nk = len(key) // 4  # Number of 32-bit words in key
        self.Nr = {4: 10, 6: 12, 8: 14}[self.Nk]  # Number of rounds
        self.Nb = 4  # Number of columns in state (always 4)
        self.round_keys = self.key_expansion(key)

    def block_to_state(self, block):
        """Convert row-major input block to column-major state."""
        state = [0] * 16
        for i in range(16):
            state[i] = block[(i % 4) * 4 + (i // 4)]
        return state

    def key_expansion(self, key):
        """Expand the cipher key into round keys."""
        Nk = self.Nk
        Nr = self.Nr
        
        # Initialize with key bytes (convert to column-major)
        w = []
        for i in range(Nk):
            w.append([
                key[4 * i],
                key[4 * i + 1],
                key[4 * i + 2],
                key[4 * i + 3]
            ])
        
        # Generate remaining words
        for i in range(Nk, 4 * (Nr + 1)):
            temp = w[i - 1][:]
            
            if i % Nk == 0:
                # RotWord
                temp = temp[1:] + temp[:1]
                
                # SubWord
                temp = [s_box[b] for b in temp]
                
                # XOR with Rcon
                temp[0] ^= Rcon[i // Nk]
            
            elif Nk > 6 and i % Nk == 4:
                # SubWord for 256-bit keys
                temp = [s_box[b] for b in temp]
            
            # XOR with word Nk positions earlier
            new_word = [w[i - Nk][j] ^ temp[j] for j in range(4)]
            w.append(new_word)
        
        # Convert to round keys (16 bytes each, column-major)
        round_keys = []
        for r in range(Nr + 1):
            rk = []
            for c in range(4):
                rk.extend(w[r * 4 + c])
            round_keys.append(rk)
        
        return round_keys

    def encrypt_block(self, block: bytes):
        """Encrypt a single 16-byte block."""
        print(f"current block :{block}")
        state = self.block_to_state(block)
        rounds = []
        
        # Initial round: AddRoundKey
        print(f"state current: {state}")
        print(f"current roundkey for init: {self.round_keys[0]}")
        state = add_round_key(state, self.round_keys[0])
        print(f"the init state before{state}")
        print(f"the init state after conv: {state_to_hex(state)}")
        rounds.append(state_to_hex(state))
        
        # Main rounds
        for r in range(1, self.Nr):
            state = sub_bytes(state)
            state = shift_rows(state)
            state = mix_columns(state)
            state = add_round_key(state, self.round_keys[r])
            rounds.append(state_to_hex(state))
        
        # Final round (no MixColumns)
        state = sub_bytes(state)
        state = shift_rows(state)
        state = add_round_key(state, self.round_keys[self.Nr])
        final = state_to_hex(state)
        rounds.append(final)
        
        return {"rounds": rounds, "final": final}

    def decrypt_block(self, block: bytes):
        """Decrypt a single 16-byte block."""
        state = self.block_to_state(block)
        rounds = []
        
        # Initial round: AddRoundKey
        state = add_round_key(state, self.round_keys[self.Nr])
        rounds.append(state_to_hex(state))
        
        # Main rounds
        for r in range(self.Nr - 1, 0, -1):
            state = inv_shift_rows(state)
            state = inv_sub_bytes(state)
            state = add_round_key(state, self.round_keys[r])
            state = inv_mix_columns(state)
            rounds.append(state_to_hex(state))
        
        # Final round (no InvMixColumns)
        state = inv_shift_rows(state)
        state = inv_sub_bytes(state)
        state = add_round_key(state, self.round_keys[0])
        final = state_to_hex(state)
        rounds.append(final)
        
        return {"rounds": rounds, "final": final}

    def encrypt_block_mode(self, block: bytes, mode="ECB", iv: bytes = None):
        """Encrypt a block using the specified mode of operation."""
        if mode == "ECB":
            return self.encrypt_block(block)
        
        elif mode == "CBC":
            if iv is None:
                raise ValueError("IV required for CBC mode")
            # XOR plaintext with IV before encryption
            xored_block = bytes([b ^ iv[i] for i, b in enumerate(block)])
            return self.encrypt_block(xored_block)
        
        elif mode == "CFB":
            if iv is None:
                raise ValueError("IV required for CFB mode")
            # Encrypt IV and XOR with plaintext
            keystream = self.encrypt_block(iv)
            ks_bytes = bytes.fromhex(keystream["final"])
            ks_bytes = bytes([ks_bytes[(i % 4) * 4 + (i // 4)] for i in range(16)])  # Convert to column-major
            ciphertext = bytes([b ^ ks_bytes[i] for i, b in enumerate(block)])
            result = {"rounds": keystream["rounds"], "final": ciphertext.hex().upper()}
            return result
        
        elif mode == "OFB":
            if iv is None:
                raise ValueError("IV required for OFB mode")
            # Encrypt IV and XOR with plaintext
            keystream = self.encrypt_block(iv)
            ks_bytes = bytes.fromhex(keystream["final"])
            ks_bytes = bytes([ks_bytes[(i % 4) * 4 + (i // 4)] for i in range(16)])  # Convert to column-major
            ciphertext = bytes([b ^ ks_bytes[i] for i, b in enumerate(block)])
            result = {"rounds": keystream["rounds"], "final": ciphertext.hex().upper()}
            return result
        
        elif mode == "CTR":
            if iv is None:
                raise ValueError("IV (counter) required for CTR mode")
            # Encrypt counter and XOR with plaintext
            keystream = self.encrypt_block(iv)
            ks_bytes = bytes.fromhex(keystream["final"])
            ks_bytes = bytes([ks_bytes[(i % 4) * 4 + (i // 4)] for i in range(16)])  # Convert to column-major
            ciphertext = bytes([b ^ ks_bytes[i] for i, b in enumerate(block)])
            result = {"rounds": keystream["rounds"], "final": ciphertext.hex().upper()}
            return result
        
        else:
            raise ValueError(f"Unsupported mode: {mode}")

    def decrypt_block_mode(self, block: bytes, mode="ECB", iv: bytes = None):
        """Decrypt a block using the specified mode of operation."""
        if mode == "ECB":
            return self.decrypt_block(block)
        
        elif mode == "CBC":
            if iv is None:
                raise ValueError("IV required for CBC mode")
            # Decrypt ciphertext then XOR with IV
            decrypted = self.decrypt_block(block)
            plaintext_bytes = bytes.fromhex(decrypted["final"])
            plaintext_bytes = bytes([plaintext_bytes[(i % 4) * 4 + (i // 4)] for i in range(16)])  # Convert to column-major
            plaintext = bytes([b ^ iv[i] for i, b in enumerate(plaintext_bytes)])
            result = {"rounds": decrypted["rounds"], "final": plaintext.hex().upper()}
            return result
        
        elif mode == "CFB":
            if iv is None:
                raise ValueError("IV required for CFB mode")
            # Encrypt IV and XOR with ciphertext
            keystream = self.encrypt_block(iv)
            ks_bytes = bytes.fromhex(keystream["final"])
            ks_bytes = bytes([ks_bytes[(i % 4) * 4 + (i // 4)] for i in range(16)])  # Convert to column-major
            plaintext = bytes([b ^ ks_bytes[i] for i, b in enumerate(block)])
            result = {"rounds": keystream["rounds"], "final": plaintext.hex().upper()}
            return result
        
        elif mode == "OFB":
            if iv is None:
                raise ValueError("IV required for OFB mode")
            # Encrypt IV and XOR with ciphertext
            keystream = self.encrypt_block(iv)
            ks_bytes = bytes.fromhex(keystream["final"])
            ks_bytes = bytes([ks_bytes[(i % 4) * 4 + (i // 4)] for i in range(16)])  # Convert to column-major
            plaintext = bytes([b ^ ks_bytes[i] for i, b in enumerate(block)])
            result = {"rounds": keystream["rounds"], "final": plaintext.hex().upper()}
            return result
        
        elif mode == "CTR":
            if iv is None:
                raise ValueError("IV (counter) required for CTR mode")
            # Encrypt counter and XOR with ciphertext
            keystream = self.encrypt_block(iv)
            ks_bytes = bytes.fromhex(keystream["final"])
            ks_bytes = bytes([ks_bytes[(i % 4) * 4 + (i // 4)] for i in range(16)])  # Convert to column-major
            plaintext = bytes([b ^ ks_bytes[i] for i, b in enumerate(block)])
            result = {"rounds": keystream["rounds"], "final": plaintext.hex().upper()}
            return result
        
        else:
            raise ValueError(f"Unsupported mode: {mode}")