from PIL import Image

def encode_image(input_image_path, text, output_image_path):
    # Open the image
    image = Image.open(input_image_path, 'r')
    
    # Convert the text into bytes and append an end marker
    data = text.encode('utf-8') + b'\x00'
    
    # Check if the data is empty
    if len(data) == 0:
        raise ValueError('Text is empty')

    # Flatten the text data into a list of bits
    datalist = [format(byte, '08b') for byte in data]
    bitstream = ''.join(datalist)  # Combine all bits into a single stream

    # Make a copy of the image
    new_image = image.copy()
    pixels = new_image.load()

    # Check if the image can hold the data
    max_capacity = image.width * image.height * 3  # 3 channels per pixel
    if len(bitstream) > max_capacity:
        raise ValueError("Text exceeds image capacity!")

    # Embed the bits into the pixels
    bit_index = 0
    for y in range(new_image.height):
        for x in range(new_image.width):
            pixel = list(pixels[x, y])  # Get the pixel as a list (R, G, B)
            for i in range(3):  # Iterate over RGB channels
                if bit_index < len(bitstream):
                    # Modify the LSB of the channel with the next bit
                    pixel[i] = (pixel[i] & ~1) | int(bitstream[bit_index])
                    bit_index += 1
            pixels[x, y] = tuple(pixel)  # Update the pixel
            if bit_index >= len(bitstream):  # Stop when all bits are encoded
                break
        if bit_index >= len(bitstream):
            break

    # Save the new image
    new_image.save(output_image_path)
    print(f"Message encoded and saved to {output_image_path}")
