from PIL import Image
import os

def image_to_bmp_and_extract(input_path, bmp_output_path, data_output_path):
    # -----------------------------
    # Step 1: Open and convert image
    # -----------------------------
    img = Image.open(input_path)
    img = img.convert("RGB")  # ensure consistent format

    # -----------------------------
    # Step 2: Save as BMP
    # -----------------------------
    img.save(bmp_output_path, format="BMP")
    print(f"BMP saved at: {bmp_output_path}")

    # -----------------------------
    # Step 3: Read BMP file
    # -----------------------------
    with open(bmp_output_path, "rb") as f:
        bmp_bytes = f.read()

    # -----------------------------
    # Step 4: Get pixel data offset
    # -----------------------------
    pixel_offset = int.from_bytes(bmp_bytes[10:14], "little")
    print(f"Pixel data starts at byte: {pixel_offset}")

    # -----------------------------
    # Step 5: Extract pixel data
    # -----------------------------
    pixel_data = bmp_bytes[pixel_offset:]

    # -----------------------------
    # Step 6: Store pixel data as hex
    # -----------------------------
    with open(data_output_path, "w") as f:
        f.write(pixel_data.hex())

    print(f"Pixel data written to: {data_output_path}")
    print(f"Pixel data size: {len(pixel_data)} bytes")


# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    input_image = "test12.jpg"          # change this
    bmp_output = "converted.bmp"
    data_output = "pixel_data.txt"

    image_to_bmp_and_extract(input_image, bmp_output, data_output)
