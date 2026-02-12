"""
AES Test File - Test different modes and key sizes without launching GUI
"""

from aes import AES

def test_aes():
    """
    Modify these variables to test different configurations
    """
    
    # ========================================
    # CONFIGURATION - CHANGE THESE TO TEST
    # ========================================
    
    # Test case selection
    KEY_SIZE = 128  # Options: 128, 192, 256
    MODE = "ECB"    # Options: "ECB", "CBC", "CFB", "OFB", "CTR"
    DIRECTION = "enc"  # Options: "enc", "dec"
    
    # Test data (all hex strings)
    TEST_BLOCK = "6BC1BEE22E409F96E93D7E117393172A"  # 128-bit block
    
    # Keys for different sizes
    KEY_128 = "2B7E151628AED2A6ABF7158809CF4F3C"                          # 128-bit
    KEY_192 = "000102030405060708090a0b0c0d0e0f1011121314151617"          # 192-bit
    KEY_256 = "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f"  # 256-bit
    
    # IV/Counter (required for CBC, CFB, OFB, CTR)
    IV = "00000000000000000000000000000000"
    
    # ========================================
    # SELECT KEY BASED ON KEY_SIZE
    # ========================================
    if KEY_SIZE == 128:
        key = KEY_128
    elif KEY_SIZE == 192:
        key = KEY_192
    elif KEY_SIZE == 256:
        key = KEY_256
    else:
        print(f"Invalid key size: {KEY_SIZE}")
        return
    
    # ========================================
    # RUN TEST
    # ========================================
    print("\n" + "="*70)
    print(f"AES TEST")
    print("="*70)
    print(f"Key Size:   {KEY_SIZE} bits")
    print(f"Mode:       {MODE}")
    print(f"Direction:  {'Encryption' if DIRECTION == 'enc' else 'Decryption'}")
    print(f"Block:      {TEST_BLOCK}")
    print(f"Key:        {key}")
    if MODE != "ECB":
        print(f"IV:         {IV}")
    print("="*70)
    
    # Create AES instance
    aes = AES(key)
    
    # Perform operation
    if DIRECTION == "enc":
        result = aes.encrypt_block_mode(TEST_BLOCK, MODE, IV if MODE != "ECB" else None)
    else:
        result = aes.decrypt_block_mode(TEST_BLOCK, MODE, IV if MODE != "ECB" else None)
    
    # ========================================
    # DISPLAY RESULTS
    # ========================================
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    print(f"\nTotal rounds tracked: {len(result['rounds'])}")
    
    for i, round_result in enumerate(result['rounds']):
        if i == 0:
            print(f"\nRound 0 (Init):  {round_result}")
        else:
            print(f"Round {i}:        {round_result}")
    
    print(f"\nFinal Output:    {result['final']}")
    print("\n" + "="*70)
    
    # Return result for further inspection if needed
    return result


def test_multiple_configs():
    """
    Run multiple test configurations in sequence
    Useful for quick validation across different settings
    """
    configs = [
        {"key_size": 128, "mode": "ECB", "direction": "enc"},
        {"key_size": 192, "mode": "ECB", "direction": "enc"},
        {"key_size": 256, "mode": "ECB", "direction": "enc"},
        {"key_size": 128, "mode": "CBC", "direction": "enc"},
        {"key_size": 128, "mode": "CFB", "direction": "enc"},
    ]
    
    print("\n" + "#"*70)
    print("RUNNING MULTIPLE TEST CONFIGURATIONS")
    print("#"*70)
    
    for i, config in enumerate(configs, 1):
        print(f"\n\n{'#'*70}")
        print(f"TEST {i}/{len(configs)}")
        print(f"{'#'*70}")
        
        # Modify globals temporarily
        globals()["KEY_SIZE"] = config["key_size"]
        globals()["MODE"] = config["mode"]
        globals()["DIRECTION"] = config["direction"]
        
        test_aes()
        
        input("\nPress Enter to continue to next test...")


if __name__ == "__main__":
    # ========================================
    # CHOOSE TEST MODE
    # ========================================
    
    # Option 1: Single test (modify variables at top of test_aes())
    result = test_aes()
    
    # Option 2: Multiple tests (uncomment below)
    # test_multiple_configs()
    
    # Option 3: Custom test
    # Uncomment and customize:
    # aes = AES("000102030405060708090a0b0c0d0e0f")
    # result = aes.encrypt_block_mode("00112233445566778899aabbccddeeff", "ECB")
    # print(f"Result: {result}")