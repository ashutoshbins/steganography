from PIL import Image

def decode_image(encoded_image_path):
    # Open the encoded image
    image = Image.open(encoded_image_path, 'r')
    pixels = image.load()

    # Extract the least significant bits (LSBs)
    binary_data = ""
    for y in range(image.height):
        for x in range(image.width):
            pixel = pixels[x, y]  # Get the pixel (R, G, B)
            for i in range(3):  # Iterate over RGB channels
                binary_data += str(pixel[i] & 1)  # Collect LSB of each channel

    # Convert binary data to characters
    byte_data = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    decoded_text = ""
    for byte in byte_data:
        if len(byte) < 8:  # Incomplete byte
            continue
        char = chr(int(byte, 2))  # Convert binary to char
        if char == "\x00":  # Stop at the end marker
            break
        decoded_text += char

    return decoded_text
