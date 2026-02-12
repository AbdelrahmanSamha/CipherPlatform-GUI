import serial
import serial.tools.list_ports

def list_com_ports():
    print("\nAvailable COM ports:")
    ports = serial.tools.list_ports.comports()
    for p in ports:
        print(f"  {p.device}  -  {p.description}")
    return [p.device for p in ports]


def open_serial_port(port):
    try:
        ser = serial.Serial(
            port=port,
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        print(f"\n✔ Connected to {port}")
        return ser
    except serial.SerialException:
        print(f"\n❌ ERROR: Could not open port {port}")
        return None


def send_and_print(ser, byte):
    ser.write(bytes([byte]))
    print(f"sent byte: {byte:02X}")


def run_stream_test(ser):
    # ---------------- fixed values ----------------
    key_hex = "2B7E151628AED2A6ABF7158809CF4F3C"
    data_hex = "6BC1BEE22E409F96E93D7E117393172A"

    key_bytes = bytes.fromhex(key_hex)
    stream_bytes = bytes.fromhex(data_hex)

    # ---------------- operation code ----------------
    stream_cmd = 0x01
    send_and_print(ser, stream_cmd)

    # ---------------- length calculation ----------------
    total_len = len(stream_bytes)

    if total_len <= 0xFF:
        length_bytes_count = 1
    elif total_len <= 0xFFFF:
        length_bytes_count = 2
    elif total_len <= 0xFFFFFF:
        length_bytes_count = 3
    else:
        length_bytes_count = 4

    # ---------------- flags ----------------
    # ECB = 000
    mode_bits = 0b000
    dir_bit = 0  # encrypt
    length_size_bits = (length_bytes_count - 1) & 0b11

    flags_val = ((length_size_bits << 4) | (dir_bit << 3) | mode_bits)
    send_and_print(ser, flags_val)

    # ---------------- send length (MSB first) ----------------
    length_bytes = total_len.to_bytes(length_bytes_count, byteorder="big")
    for byte in length_bytes:
        send_and_print(ser, byte)

    print(f"Total stream length: {total_len} bytes")

    # ---------------- send key ----------------
    print("about to send key bytes:")
    for byte in key_bytes:
        send_and_print(ser, byte)

    # ---------------- send stream data ----------------
    print("about to send data bytes:")
    for byte in stream_bytes:
        send_and_print(ser, byte)

    print("✔ Stream sent. Waiting for FPGA response...")

    # Read response (expect same length)
    result = ser.read(total_len)

    if len(result) == total_len:
        print("\n== RESULT RECEIVED ==")
        print(result.hex())
    else:
        print("\n❌ ERROR: Incorrect number of bytes received.")
        print(f"Received: {result.hex()}")


def main():
    print("=== UART AES Stream Test Tool (Python) ===")

    ports = list_com_ports()
    port = input("\nEnter COM port (e.g., COM4): ").strip()

    if port not in ports:
        print("❌ ERROR: COM port not found.")
        return

    ser = open_serial_port(port)
    if ser is None:
        return

    run_stream_test(ser)

    ser.close()
    print("\nSerial port closed.")
    print("Goodbye!")


if __name__ == "__main__":
    main()
