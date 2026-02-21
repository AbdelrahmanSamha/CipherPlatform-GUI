"""
Curve25519 Key Exchange Test Script
Tests both FPGA (via UART) and Software implementations
"""

import serial
import serial.tools.list_ports
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization


# =========================================================
# CONFIGURATION - MODIFY THESE
# =========================================================

# Enable/disable tests (comment out to skip)
RUN_FPGA_TEST = True       # Test FPGA via UART
RUN_SOFTWARE_TEST = True   # Test software implementation

# COM Port (will ask if not set)
COM_PORT = None  # e.g., "COM4" or leave None to select

# Test Values (modify these!)
# NOTE: Values are in LITTLE-ENDIAN format (standard Curve25519)
# Script automatically converts to BIG-ENDIAN for FPGA

# Option 1: Generate public key from private key
TEST_PRIVATE_KEY = "07" + "00"*31
TEST_PUBLIC_INPUT = "09" + "00"*31  # Base point (little-endian: 09 at start)

# Option 2: Compute shared secret (uncomment to use)
# TEST_PRIVATE_KEY = "77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a"
# TEST_PUBLIC_INPUT = "de9edb7d7b7dc1b4d35b61c2ece435373f8343c85b78674dadfc7e146f882b4f"  # Other party's public key (little-endian)


# =========================================================
# UART HELPERS
# =========================================================

def list_com_ports():
    """List available COM ports"""
    print("\nAvailable COM ports:")
    ports = serial.tools.list_ports.comports()
    for p in ports:
        print(f"  {p.device}  -  {p.description}")
    return [p.device for p in ports]


def open_serial_port(port):
    """Open serial port with correct settings"""
    try:
        ser = serial.Serial(
            port=port,
            baudrate=921600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=2
        )
        print(f"\n✔ Connected to {port}")
        return ser
    except serial.SerialException as e:
        print(f"\n❌ ERROR: Could not open port {port}: {e}")
        return None


def send_and_print(ser, byte):
    """Send byte and print"""
    ser.write(bytes([byte]))
    print(f"sent byte: {byte:02X}")


# =========================================================
# FPGA KEYEXCHANGE TEST (via UART)
# =========================================================

def run_fpga_keyexchange_test(ser, private_key_hex, public_input_hex):
    """
    Send Curve25519 operation to FPGA via UART
    
    Args:
        ser: Serial port object
        private_key_hex: Private key as hex string (64 chars = 32 bytes, little-endian)
        public_input_hex: Public input as hex string (64 chars = 32 bytes, little-endian)
    
    Returns:
        bytes: 32-byte result from FPGA (big-endian, will be converted back to little-endian)
    """
    print("\n" + "="*60)
    print("FPGA CURVE25519 OPERATION (via UART)")
    print("="*60)
    
    # Convert hex strings to bytes (little-endian input)
    private_key_le = bytes.fromhex(private_key_hex)
    public_input_le = bytes.fromhex(public_input_hex)
    
    # Validate lengths
    if len(private_key_le) != 32:
        print(f"❌ ERROR: Private key must be 32 bytes, got {len(private_key_le)}")
        return None
    
    if len(public_input_le) != 32:
        print(f"❌ ERROR: Public input must be 32 bytes, got {len(public_input_le)}")
        return None
    
    print(f"Private key (LE): {private_key_le.hex().upper()}")
    print(f"Public input (LE): {public_input_le.hex().upper()}")
    
    # IMPORTANT: FPGA uses BIG-ENDIAN, so REVERSE the bytes!
    private_key_be = bytes(reversed(private_key_le))
    public_input_be = bytes(reversed(public_input_le))
    
    print(f"\n[BYTE ORDER CONVERSION]")
    print(f"Private key (BE): {private_key_be.hex().upper()}")
    print(f"Public input (BE): {public_input_be.hex().upper()}")
    
    # Determine operation type (check little-endian format)
    is_public_key_gen = (public_input_le == b'\x09' + b'\x00'*31)
    if is_public_key_gen:
        print("\n[OPERATION] Generating public key (scalar × base_point)")
    else:
        print("\n[OPERATION] Computing shared secret (my_private × their_public)")
    
    # Clear any old data
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    
    # Send command byte (0x06 for keyexchange)
    kx_cmd = 0x06
    print("\n[UART] Sending command byte...")
    send_and_print(ser, kx_cmd)
    
    # Send private key (32 bytes, BIG-ENDIAN for FPGA)
    print("\n[UART] Sending private key (32 bytes, BIG-ENDIAN)...")
    for byte in private_key_be:
        send_and_print(ser, byte)
    
    # Send public input (32 bytes, BIG-ENDIAN for FPGA)
    print("\n[UART] Sending public input (32 bytes, BIG-ENDIAN)...")
    for byte in public_input_be:
        send_and_print(ser, byte)
    
    print("\n[UART] ✔ All bytes sent. Waiting for FPGA response...")
    
    # Read response (expect 32 bytes in BIG-ENDIAN)
    result_be = ser.read(32)
    
    if len(result_be) == 32:
        # Convert result back to LITTLE-ENDIAN for comparison with software
        result_le = bytes(reversed(result_be))
        
        print("\n[FPGA RESULT] ✅ Received 32 bytes:")
        print(f"Result (BE from FPGA): {result_be.hex().upper()}")
        print(f"Result (LE converted):  {result_le.hex().upper()}")
        print("="*60 + "\n")
        return result_le  # Return in little-endian for comparison
    else:
        print(f"\n❌ ERROR: Expected 32 bytes, got {len(result_be)}")
        if result_be:
            print(f"Received: {result_be.hex().upper()}")
        print("="*60 + "\n")
        return None


# =========================================================
# SOFTWARE KEYEXCHANGE TEST
# =========================================================

def run_software_keyexchange_test(private_key_hex, public_input_hex):
    """
    Perform Curve25519 scalar multiplication in software.
    
    Args:
        private_key_hex: Private key as hex string (64 chars = 32 bytes)
        public_input_hex: Public input as hex string (64 chars = 32 bytes)
    
    Returns:
        bytes: 32-byte result
    """
    print("\n" + "="*60)
    print("SOFTWARE CURVE25519 OPERATION")
    print("="*60)
    
    # Convert hex strings to bytes
    scalar = bytes.fromhex(private_key_hex)
    u_coordinate = bytes.fromhex(public_input_hex)
    
    # Validate inputs
    if len(scalar) != 32:
        print(f"❌ Invalid scalar: must be 32 bytes, got {len(scalar)}")
        return None
    
    if len(u_coordinate) != 32:
        print(f"❌ Invalid u_coordinate: must be 32 bytes, got {len(u_coordinate)}")
        return None
    
    print(f"Scalar (private key): {scalar.hex().upper()}")
    print(f"U-coordinate (point): {u_coordinate.hex().upper()}")
    
    # Check if this is public key generation (base point = 9)
    is_public_key_gen = (u_coordinate == b'\x09' + b'\x00'*31)
    
    if is_public_key_gen:
        print("\n[OPERATION] Generating public key from private key")
        print("            (scalar × base_point)")
    else:
        print("\n[OPERATION] Computing shared secret")
        print("            (my_private × their_public)")
    
    try:
        # Create private key object from scalar bytes
        private_key = x25519.X25519PrivateKey.from_private_bytes(scalar)
        
        if is_public_key_gen:
            # Generate public key
            public_key = private_key.public_key()
            
            # Serialize to raw bytes (32 bytes, little-endian)
            result = public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
            
            print(f"\n[SOFTWARE RESULT] ✅ Public key generated:")
            print(f"Result: {result.hex().upper()}")
        
        else:
            # Compute shared secret
            their_public_key = x25519.X25519PublicKey.from_public_bytes(u_coordinate)
            
            # Perform key exchange (scalar multiplication)
            shared_secret = private_key.exchange(their_public_key)
            
            result = shared_secret
            
            print(f"\n[SOFTWARE RESULT] ✅ Shared secret computed:")
            print(f"Result: {result.hex().upper()}")
        
        print("="*60 + "\n")
        return result
    
    except Exception as e:
        print(f"\n❌ Curve25519 operation failed: {e}")
        import traceback
        traceback.print_exc()
        print("="*60 + "\n")
        return None


# =========================================================
# COMPARISON
# =========================================================

def compare_results(fpga_result, software_result):
    """Compare FPGA and software results"""
    print("\n" + "="*60)
    print("COMPARISON")
    print("="*60)
    
    if fpga_result is None and software_result is None:
        print("❌ Both operations failed")
        return
    
    if fpga_result is None:
        print("⚠️ FPGA operation failed, cannot compare")
        print(f"Software result: {software_result.hex().upper()}")
        return
    
    if software_result is None:
        print("⚠️ Software operation failed, cannot compare")
        print(f"FPGA result: {fpga_result.hex().upper()}")
        return
    
    print(f"FPGA result:     {fpga_result.hex().upper()}")
    print(f"Software result: {software_result.hex().upper()}")
    
    if fpga_result == software_result:
        print("\n✅ RESULTS MATCH! Both implementations produce identical output.")
    else:
        print("\n❌ RESULTS DO NOT MATCH!")
        
        # Find first difference
        for i in range(min(len(fpga_result), len(software_result))):
            if fpga_result[i] != software_result[i]:
                print(f"First difference at byte {i}: FPGA=0x{fpga_result[i]:02X} vs Software=0x{software_result[i]:02X}")
                break
    
    print("="*60 + "\n")


# =========================================================
# MAIN
# =========================================================

def main():
    print("="*60)
    print("CURVE25519 KEY EXCHANGE TEST TOOL")
    print("="*60)
    
    # Show configuration
    print("\nConfiguration:")
    print(f"  FPGA Test: {'ENABLED' if RUN_FPGA_TEST else 'DISABLED'}")
    print(f"  Software Test: {'ENABLED' if RUN_SOFTWARE_TEST else 'DISABLED'}")
    print(f"\nTest Values:")
    print(f"  Private Key:  {TEST_PRIVATE_KEY}")
    print(f"  Public Input: {TEST_PUBLIC_INPUT}")
    
    # Determine operation type
    if TEST_PUBLIC_INPUT == "09" + "00"*31:
        print(f"  Operation: Generate PUBLIC KEY")
    else:
        print(f"  Operation: Compute SHARED SECRET")
    
    # Variables to store results
    fpga_result = None
    software_result = None
    
    # Run FPGA test
    if RUN_FPGA_TEST:
        # Get COM port
        if COM_PORT:
            port = COM_PORT
        else:
            ports = list_com_ports()
            port = input("\nEnter COM port (e.g., COM4): ").strip()
            
            if port not in ports:
                print("❌ ERROR: COM port not found.")
                return
        
        # Open serial port
        ser = open_serial_port(port)
        if ser is None:
            return
        
        # Run test
        try:
            fpga_result = run_fpga_keyexchange_test(ser, TEST_PRIVATE_KEY, TEST_PUBLIC_INPUT)
        finally:
            ser.close()
            print("Serial port closed.\n")
    
    # Run software test
    if RUN_SOFTWARE_TEST:
        software_result = run_software_keyexchange_test(TEST_PRIVATE_KEY, TEST_PUBLIC_INPUT)
    
    # Compare results if both ran
    if RUN_FPGA_TEST and RUN_SOFTWARE_TEST:
        compare_results(fpga_result, software_result)
    
    print("\nTest complete!")


if __name__ == "__main__":
    main()