import hashlib
def main():
    # -------------------------------
    # Input your blocks as HEX strings
    # -------------------------------

    # Block 1 (hex)
    block1_hex = "23b4213b4b234b234b23492347982308947908789787989789789789789788978779878978791273213543512367452136752345116567512334887878716266abdbdbbdb12821793128973897214980987897432879423891476856abdbdbdbbdbd129831892738291738921748972314589712389982198237489723489231" 


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