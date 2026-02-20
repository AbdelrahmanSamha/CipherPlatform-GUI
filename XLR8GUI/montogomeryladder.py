# ============================================================
# X25519 Montgomery Ladder - Memory-Mapped Version (VERBOSE)
# Prints every operation and memory change
# ============================================================

# Prime for Curve25519
p = 2**255 - 19

# Memory map indices
MEM_SCALAR      = 0
MEM_X1          = 1
MEM_X2          = 2
MEM_Z2          = 3
MEM_X3          = 4
MEM_Z3          = 5
MEM_SWAP        = 6
MEM_K_T         = 7
MEM_BIT_INDEX   = 8
MEM_A           = 9
MEM_B           = 10
MEM_C           = 11
MEM_D           = 12
MEM_AA          = 13
MEM_BB          = 14
MEM_E           = 15
MEM_DA          = 16
MEM_CB          = 17
MEM_TEMP1       = 18
MEM_TEMP2       = 19
MEM_TEMP3       = 20
MEM_TEMP4       = 21
MEM_TEMP5       = 22
MEM_Z2_INV      = 23
MEM_RESULT      = 24
MEM_A24         = 25


# ============================================================
# Field Arithmetic
# ============================================================

def mod_add(a, b):
    return (a + b) % p

def mod_sub(a, b):
    return (a - b) % p

def mod_mul(a, b):
    return (a * b) % p

def mod_inv(a):
    return pow(a, p - 2, p)


# ============================================================
# Memory-Mapped Implementation with Verbose Logging
# ============================================================

def scalar_multiply_memory_mapped(INPUT_scalar, INPUT_u_coordinate):
    
    # Initialize memory array (26 locations)
    mem = [0] * 26
    
    print("=" * 80)
    print("X25519 MONTGOMERY LADDER - DETAILED MEMORY-MAPPED EXECUTION")
    print("=" * 80)

    # ---- Initialize constant ----
    print("\n[INIT] Setting MEM[25] = A24 constant")
    mem[MEM_A24] = 121665
    print(f"       MEM[25] ← 121665")
    
    # ---- Step 1: Clamp the scalar ----
    print("\n" + "=" * 80)
    print("STEP 1: CLAMP SCALAR")
    print("=" * 80)
    mem[MEM_SCALAR] = INPUT_scalar
    print(f"[WRITE] MEM[0] ← {hex(INPUT_scalar)} (original scalar)")
    
    mem[MEM_SCALAR] &= ~7
    print(f"[CLAMP] Clear bits [2:0]")
    print(f"        MEM[0] ← {hex(mem[MEM_SCALAR])}")
    
    mem[MEM_SCALAR] &= ~(1 << 255)
    print(f"[CLAMP] Clear bit 255")
    print(f"        MEM[0] ← {hex(mem[MEM_SCALAR])}")
    
    mem[MEM_SCALAR] |= (1 << 254)
    print(f"[CLAMP] Set bit 254")
    print(f"        MEM[0] ← {hex(mem[MEM_SCALAR])}")
    
    # ---- Step 2: Initialize ladder variables ----
    print("\n" + "=" * 80)
    print("STEP 2: INITIALIZE LADDER VARIABLES")
    print("=" * 80)
    
    mem[MEM_X1] = INPUT_u_coordinate
    print(f"[WRITE] MEM[1] (x1) ← {hex(mem[MEM_X1])}")
    
    mem[MEM_X2] = 1
    print(f"[WRITE] MEM[2] (x2) ← {hex(mem[MEM_X2])}")
    
    mem[MEM_Z2] = 0
    print(f"[WRITE] MEM[3] (z2) ← {hex(mem[MEM_Z2])}")
    
    mem[MEM_X3] = INPUT_u_coordinate
    print(f"[WRITE] MEM[4] (x3) ← {hex(mem[MEM_X3])}")
    
    mem[MEM_Z3] = 1
    print(f"[WRITE] MEM[5] (z3) ← {hex(mem[MEM_Z3])}")
    
    mem[MEM_SWAP] = 0
    print(f"[WRITE] MEM[6] (swap) ← {hex(mem[MEM_SWAP])}")
    
    mem[MEM_BIT_INDEX] = 254
    print(f"[WRITE] MEM[8] (bit_index) ← {mem[MEM_BIT_INDEX]}")
    
    # ---- Step 3: Main ladder loop ----
    print("\n" + "=" * 80)
    print("STEP 3: MAIN LADDER LOOP (255 ITERATIONS)")
    print("=" * 80)
    
    for mem[MEM_BIT_INDEX] in reversed(range(255)):
        
        print(f"\n{'─' * 80}")
        print(f"ITERATION {mem[MEM_BIT_INDEX]:3d}")
        print(f"{'─' * 80}")
        
        # 3a. Read current bit
        mem[MEM_K_T] = (mem[MEM_SCALAR] >> mem[MEM_BIT_INDEX]) & 1
        print(f"\n[READ BIT] MEM[7] (k_t) ← scalar[{mem[MEM_BIT_INDEX]}] = {mem[MEM_K_T]}")
        
        # 3b. Conditional swap
        old_swap = mem[MEM_SWAP]
        mem[MEM_SWAP] = mem[MEM_SWAP] ^ mem[MEM_K_T]
        print(f"[XOR]      MEM[6] (swap) ← {old_swap} XOR {mem[MEM_K_T]} = {mem[MEM_SWAP]}")
        
        if mem[MEM_SWAP] == 1:
            print(f"\n[SWAP] Swapping x2 ↔ x3, z2 ↔ z3")
            print(f"       Before: MEM[2]={hex(mem[MEM_X2])}, MEM[4]={hex(mem[MEM_X3])}")
            print(f"               MEM[3]={hex(mem[MEM_Z2])}, MEM[5]={hex(mem[MEM_Z3])}")
            
            mem[MEM_X2], mem[MEM_X3] = mem[MEM_X3], mem[MEM_X2]
            mem[MEM_Z2], mem[MEM_Z3] = mem[MEM_Z3], mem[MEM_Z2]
            
            print(f"       After:  MEM[2]={hex(mem[MEM_X2])}, MEM[4]={hex(mem[MEM_X3])}")
            print(f"               MEM[3]={hex(mem[MEM_Z2])}, MEM[5]={hex(mem[MEM_Z3])}")
        else:
            print(f"[NO SWAP] swap = 0, no exchange")
        
        mem[MEM_SWAP] = mem[MEM_K_T]
        print(f"[UPDATE]   MEM[6] (swap) ← {mem[MEM_SWAP]}")
        
        # 3c. Montgomery differential addition and doubling
        print(f"\n[MONTGOMERY STEP]")
        
        # Compute A, B, C, D
        print(f"\n  Computing A, B, C, D:")
        mem[MEM_A] = mod_add(mem[MEM_X2], mem[MEM_Z2])
        print(f"  [ADD] MEM[9]  (A) ← MEM[2] + MEM[3] = {hex(mem[MEM_A])}")
        
        mem[MEM_B] = mod_sub(mem[MEM_X2], mem[MEM_Z2])
        print(f"  [SUB] MEM[10] (B) ← MEM[2] - MEM[3] = {hex(mem[MEM_B])}")
        
        mem[MEM_C] = mod_add(mem[MEM_X3], mem[MEM_Z3])
        print(f"  [ADD] MEM[11] (C) ← MEM[4] + MEM[5] = {hex(mem[MEM_C])}")
        
        mem[MEM_D] = mod_sub(mem[MEM_X3], mem[MEM_Z3])
        print(f"  [SUB] MEM[12] (D) ← MEM[4] - MEM[5] = {hex(mem[MEM_D])}")
        
        # Compute AA, BB, E
        print(f"\n  Computing AA, BB, E:")
        mem[MEM_AA] = mod_mul(mem[MEM_A], mem[MEM_A])
        print(f"  [MUL] MEM[13] (AA) ← MEM[9] × MEM[9] = {hex(mem[MEM_AA])}")
        
        mem[MEM_BB] = mod_mul(mem[MEM_B], mem[MEM_B])
        print(f"  [MUL] MEM[14] (BB) ← MEM[10] × MEM[10] = {hex(mem[MEM_BB])}")
        
        mem[MEM_E] = mod_sub(mem[MEM_AA], mem[MEM_BB])
        print(f"  [SUB] MEM[15] (E)  ← MEM[13] - MEM[14] = {hex(mem[MEM_E])}")
        
        # Compute DA, CB
        print(f"\n  Computing DA, CB:")
        mem[MEM_DA] = mod_mul(mem[MEM_D], mem[MEM_A])
        print(f"  [MUL] MEM[16] (DA) ← MEM[12] × MEM[9] = {hex(mem[MEM_DA])}")
        
        mem[MEM_CB] = mod_mul(mem[MEM_C], mem[MEM_B])
        print(f"  [MUL] MEM[17] (CB) ← MEM[11] × MEM[10] = {hex(mem[MEM_CB])}")
        
        # Compute new x3
        print(f"\n  Computing new x3:")
        mem[MEM_TEMP1] = mod_add(mem[MEM_DA], mem[MEM_CB])
        print(f"  [ADD] MEM[18] (temp1) ← MEM[16] + MEM[17] = {hex(mem[MEM_TEMP1])}")
        
        mem[MEM_TEMP2] = mod_mul(mem[MEM_TEMP1], mem[MEM_TEMP1])
        print(f"  [MUL] MEM[19] (temp2) ← MEM[18] × MEM[18] = {hex(mem[MEM_TEMP2])}")
        
        mem[MEM_X3] = mem[MEM_TEMP2]
        print(f"  [MOVE] MEM[4] (x3) ← MEM[19] = {hex(mem[MEM_X3])}")
        
        # Compute new z3
        print(f"\n  Computing new z3:")
        mem[MEM_TEMP3] = mod_sub(mem[MEM_DA], mem[MEM_CB])
        print(f"  [SUB] MEM[20] (temp3) ← MEM[16] - MEM[17] = {hex(mem[MEM_TEMP3])}")
        
        mem[MEM_TEMP4] = mod_mul(mem[MEM_TEMP3], mem[MEM_TEMP3])
        print(f"  [MUL] MEM[21] (temp4) ← MEM[20] × MEM[20] = {hex(mem[MEM_TEMP4])}")
        
        mem[MEM_Z3] = mod_mul(mem[MEM_X1], mem[MEM_TEMP4])
        print(f"  [MUL] MEM[5] (z3) ← MEM[1] × MEM[21] = {hex(mem[MEM_Z3])}")
        
        # Compute new x2
        print(f"\n  Computing new x2:")
        mem[MEM_X2] = mod_mul(mem[MEM_AA], mem[MEM_BB])
        print(f"  [MUL] MEM[2] (x2) ← MEM[13] × MEM[14] = {hex(mem[MEM_X2])}")
        
        # Compute new z2
        print(f"\n  Computing new z2:")
        mem[MEM_TEMP5] = mod_mul(mem[MEM_A24], mem[MEM_E])
        print(f"  [MUL] MEM[22] (temp5) ← MEM[25] × MEM[15] = {hex(mem[MEM_TEMP5])}")
        
        mem[MEM_TEMP1] = mod_add(mem[MEM_AA], mem[MEM_TEMP5])
        print(f"  [ADD] MEM[18] (temp1) ← MEM[13] + MEM[22] = {hex(mem[MEM_TEMP1])}")
        
        mem[MEM_Z2] = mod_mul(mem[MEM_E], mem[MEM_TEMP1])
        print(f"  [MUL] MEM[3] (z2) ← MEM[15] × MEM[18] = {hex(mem[MEM_Z2])}")
        
        print(f"\n[END OF ITERATION {mem[MEM_BIT_INDEX]}]")
        print(f"  Final state:")
        print(f"    MEM[2] (x2) = {hex(mem[MEM_X2])}")
        print(f"    MEM[3] (z2) = {hex(mem[MEM_Z2])}")
        print(f"    MEM[4] (x3) = {hex(mem[MEM_X3])}")
        print(f"    MEM[5] (z3) = {hex(mem[MEM_Z3])}")
        print(f"    MEM[6] (swap) = {mem[MEM_SWAP]}")
    
    # ---- Step 4: Final conditional swap ----
    print("\n" + "=" * 80)
    print("STEP 4: FINAL CONDITIONAL SWAP")
    print("=" * 80)
    print(f"MEM[6] (swap) = {mem[MEM_SWAP]}")
    
    if mem[MEM_SWAP] == 1:
        print(f"[FINAL SWAP] Swapping x2 ↔ x3, z2 ↔ z3")
        print(f"  Before: MEM[2]={hex(mem[MEM_X2])}, MEM[4]={hex(mem[MEM_X3])}")
        print(f"          MEM[3]={hex(mem[MEM_Z2])}, MEM[5]={hex(mem[MEM_Z3])}")
        
        mem[MEM_X2], mem[MEM_X3] = mem[MEM_X3], mem[MEM_X2]
        mem[MEM_Z2], mem[MEM_Z3] = mem[MEM_Z3], mem[MEM_Z2]
        
        print(f"  After:  MEM[2]={hex(mem[MEM_X2])}, MEM[4]={hex(mem[MEM_X3])}")
        print(f"          MEM[3]={hex(mem[MEM_Z2])}, MEM[5]={hex(mem[MEM_Z3])}")
    else:
        print(f"[NO FINAL SWAP] swap = 0")
    
    # ---- Step 5: Convert from projective to affine ----
    print("\n" + "=" * 80)
    print("STEP 5: CONVERT TO AFFINE COORDINATES")
    print("=" * 80)
    
    mem[MEM_Z2_INV] = mod_inv(mem[MEM_Z2])
    print(f"[INV] MEM[23] (z2_inv) ← mod_inv(MEM[3]) = {hex(mem[MEM_Z2_INV])}")
    
    mem[MEM_RESULT] = mod_mul(mem[MEM_X2], mem[MEM_Z2_INV])
    print(f"[MUL] MEM[24] (result) ← MEM[2] × MEM[23] = {hex(mem[MEM_RESULT])}")
    
    print("\n" + "=" * 80)
    print("FINAL RESULT")
    print("=" * 80)
    print(f"MEM[24] (result) = {hex(mem[MEM_RESULT])}")
    print("=" * 80 + "\n")
    
    return mem[MEM_RESULT]


# ============================================================
# Reference Implementation Using cryptography Library
# ============================================================

def scalar_multiply_reference(scalar, u):
    try:
        from cryptography.hazmat.primitives.asymmetric import x25519
    except ImportError:
        print("cryptography library not installed.")
        print("Install using: pip install cryptography")
        exit(1)

    scalar_bytes = scalar.to_bytes(32, "little")
    u_bytes = u.to_bytes(32, "little")

    private_key = x25519.X25519PrivateKey.from_private_bytes(scalar_bytes)
    public_key = x25519.X25519PublicKey.from_public_bytes(u_bytes)

    shared = private_key.exchange(public_key)

    return int.from_bytes(shared, "little")


# ============================================================
# MAIN TEST EXECUTION
# ============================================================

if __name__ == "__main__":

    print("\nRunning Test Vector...\n")

    # Test values
    scalar_test = 20
    u_test = 20

    memory_result = scalar_multiply_memory_mapped(scalar_test, u_test)
    reference_result = scalar_multiply_reference(scalar_test, u_test)

    print("=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    print(f"Memory-Mapped Result : {hex(memory_result)}")
    print(f"Reference Result     : {hex(reference_result)}")

    if memory_result == reference_result:
        print("\n✔ MATCH - Implementation is CORRECT")
    else:
        print("\n✘ MISMATCH - Something is wrong")
    print("=" * 80)