import hashlib
def main():
    # -------------------------------
    # Input your blocks as HEX strings
    # -------------------------------

    # Block 1 (hex)
    block1_hex = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef" 


    # Block 2 (hex)
    block2_hex = "8000000000000000000000000000000000000000000000000000000000000000" \
                "0000000000000000000000000000000000000000000000000000000000000200"

    # Convert hex to bytes
    block1_bytes = bytes.fromhex(block1_hex)
    block2_bytes = bytes.fromhex(block2_hex)

    # Concatenate blocks
    message = block1_bytes 

    # Compute SHA-256
    digest = hashlib.sha256(message).hexdigest()

    # Print result
    print("SHA-256 digest:", digest)

if __name__ == "__main__":
    main()