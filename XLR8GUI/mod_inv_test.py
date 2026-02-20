# =============================================
# mod_inv Step-by-Step Simulation
# Mimics exactly what the Verilog state machine does
# Prints every iteration for comparison with ModelSim
# =============================================

P       = 2**255 - 19
P_MINUS_2 = P - 2

def mod_mul(a, b):
    return (a * b) % P

def mod_inv_trace(a):
    print("=" * 70)
    print(f"mod_inv({a})")
    print(f"p-2 = {hex(P_MINUS_2)}")
    print("=" * 70)

    # INIT
    result      = 1
    base        = a
    exp         = P_MINUS_2
    bit_counter = 0

    print(f"\n--- INIT ---")
    print(f"  result = {result}")
    print(f"  base   = {base}")
    print(f"  exp    = {hex(exp)}")

    for i in range(256):
        current_bit = exp & 1  # LSB

        print(f"\n--- Iteration {i} ---")
        print(f"  bit        = {current_bit}")
        print(f"  result_in  = {hex(result)}")
        print(f"  base_in    = {hex(base)}")

        # Step 1: CHECK_BIT
        if current_bit == 1:
            # MUL_RESULT state
            print(f"  [MUL_RESULT] result = mod_mul(result, base)")
            result = mod_mul(result, base)
            print(f"  result_out = {hex(result)}")
        else:
            print(f"  [CHECK_BIT=0] skipping multiply")

        # Step 2: SQ_BASE state
        print(f"  [SQ_BASE] base = mod_mul(base, base)")
        base = mod_mul(base, base)
        print(f"  base_out   = {hex(base)}")

        # Step 3: shift exp
        exp = exp >> 1
        bit_counter += 1

        print(f"  next_bit   = {exp & 1}")

    print("\n" + "=" * 70)
    print(f"FINAL result = {hex(result)}")

    # Verify
    check = (a * result) % P
    print(f"VERIFY: {a} * result mod p = {check}")
    if check == 1:
        print("✓ CORRECT")
    else:
        print("✗ WRONG")
    print("=" * 70)

    return result

# Run for a = 7
mod_inv_trace(23)