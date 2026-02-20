# =============================================
# MAU Verification Script
# Computes all 4 operations and prints expected
# results to compare against Verilog simulation
# =============================================

# Curve25519 prime
P = 2**255 - 19

def mod_add(a, b):
    return (a + b) % P

def mod_sub(a, b):
    return (a - b) % P

def mod_mul(a, b):
    return (a * b) % P

def mod_inv(a):
    # Fermat's little theorem: a^(p-2) mod p
    return pow(a, P - 2, P)

def verify(operation, a, b=None):
    print("=" * 60)
    print(f"Operation : {operation}")
    print(f"a         : {hex(a)}")
    if b is not None:
        print(f"b         : {hex(b)}")
    
    if operation == "ADD":
        result = mod_add(a, b)
    elif operation == "SUB":
        result = mod_sub(a, b)
    elif operation == "MUL":
        result = mod_mul(a, b)
    elif operation == "INV":
        result = mod_inv(a)
        # Sanity check: a * a^(-1) should equal 1
        check = mod_mul(a, result)
        print(f"Sanity    : a * inv(a) mod p = {check} (should be 1)")
    
    print(f"Result    : {hex(result)}")
    print(f"Result dec: {result}")
    print("=" * 60)
    return result

# =============================================
# Same test cases as your testbench
# =============================================

# Test 1: Addition
#verify("ADD", 12345, 67890)

# Test 2: Subtraction
#verify("SUB", 100000, 30000)

# Test 3: Subtraction with borrow (a < b)
#verify("SUB", 10, 50)

# Test 4: Multiplication
#verify("MUL", 1234, 5678)

# Test 5: Inverse
#verify("INV", 7)

# =============================================
# Additional edge cases
# =============================================

# Addition near overflow
a_large = 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF0
verify("ADD", a_large, 100)

# Multiplication with large numbers
verify("MUL", 
    0x1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF,
    0xFEDCBA9876543210FEDCBA9876543210FEDCBA9876543210FEDCBA9876543210)

# =============================================
# Helper: Paste your Verilog result here
# =============================================

def check_result(operation, a, b, verilog_result):
    """
    Paste your Verilog simulation result here to verify
    """
    if operation == "ADD":
        expected = mod_add(a, b)
    elif operation == "SUB":
        expected = mod_sub(a, b)
    elif operation == "MUL":
        expected = mod_mul(a, b)
    elif operation == "INV":
        expected = mod_inv(a)
    
    print(f"\nVerifying {operation}:")
    print(f"  Expected : {hex(expected)}")
    print(f"  Got      : {hex(verilog_result)}")
    
    if expected == verilog_result:
        print(f"  ✓ PASS")
    else:
        print(f"  ✗ FAIL")
        print(f"  Diff     : {hex(expected ^ verilog_result)}")

# Example: paste your Verilog output here
#check_result("ADD", 12345, 67890, 80235)
#check_result("SUB", 100000, 30000, 70000)
#check_result("MUL", 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFE, 0x02, 34)
check_result("INV", 7, None, 0x777ad92122f0c4b6bd5a86bb376238e9359044bc8180c3c136c22b004f3fbc74)