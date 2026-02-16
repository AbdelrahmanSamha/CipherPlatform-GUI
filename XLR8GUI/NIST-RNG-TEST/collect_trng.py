import serial
import time

# -----------------------------
# USER CONFIG
# -----------------------------
PORT = "COM3"          # Change to your UART port
BAUDRATE = 912600      # Match your FPGA UART
OUTPUT_FILE = "NIST-RNG-TEST/trng_output.bin"

TARGET_BYTES = 100_000_000  # 100 MB = 800 million bits
PACKET_SIZE = 64            # 512 bits = 64 bytes

# RNG command (00000100)
RNG_CMD = bytes([0x04])


def main():
    total_received = 0
    runs = 0
    start_time = time.time()

    print("Opening serial port...")
    ser = serial.Serial(PORT, BAUDRATE, timeout=1)

    with open(OUTPUT_FILE, "wb") as f:
        print(f"Starting TRNG collection... Target: {TARGET_BYTES:,} bytes ({TARGET_BYTES/1_000_000:.1f} MB)")
        while total_received < TARGET_BYTES:
            # Send RNG command
            ser.write(RNG_CMD)

            # Read 64 bytes
            data = ser.read(PACKET_SIZE)

            if len(data) != PACKET_SIZE:
                print("Incomplete packet, retrying...")
                continue

            # Write to file
            f.write(data)

            total_received += PACKET_SIZE
            runs += 1

            # Progress update every 10,000 packets (~640 KB)
            if runs % 10000 == 0:
                elapsed = time.time() - start_time
                rate = total_received / elapsed / 1_000_000  # MB/s
                progress = (total_received / TARGET_BYTES) * 100
                print(f"Progress: {progress:.1f}% | {total_received/1_000_000:.1f} MB | Rate: {rate:.2f} MB/s")

    ser.close()
    elapsed = time.time() - start_time
    
    print("\n" + "="*50)
    print("Collection Complete!")
    print("="*50)
    print(f"Total runs: {runs:,}")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Total bytes: {total_received:,} ({total_received/1_000_000:.1f} MB)")
    print(f"Total bits: {total_received * 8:,}")
    print(f"Time elapsed: {elapsed:.1f} seconds")
    print(f"Average rate: {total_received / elapsed / 1_000_000:.2f} MB/s")


if __name__ == "__main__":
    main()