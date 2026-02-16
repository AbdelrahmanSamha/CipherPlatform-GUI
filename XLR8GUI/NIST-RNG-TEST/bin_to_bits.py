with open("NIST-RNG-TEST/trng_output.bin", "rb") as f_in, open("trng_bits.txt", "w") as f_out:
    while True:
        byte = f_in.read(1)
        if not byte:
            break
        bits = format(byte[0], "08b")
        f_out.write(bits)
