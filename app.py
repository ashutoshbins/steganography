from flask import Flask, request, render_template, send_file, url_for
import os
from PIL import Image
from encode_image import encode_image
from decode_image import decode_image
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './static/uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
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
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/steganography/encrypt', methods=['GET', 'POST'])
def encrypt():
    if request.method == 'POST':
        file = request.files['file']
        text = request.form['text']
        file_type = request.form['type']

        # Check if a file was uploaded
        if not file:
            return render_template('result.html', message="No file uploaded.")

        # Save the uploaded file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Check file type and call the appropriate function
        if file_type == 'image':
            output_filename = f"encrypted_{file.filename.split('.')[0]}.png"  # Save with .png extension
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            encode_image(filepath, text, output_path)
            download_url = url_for('static', filename=f'uploads/{output_filename}')
            return render_template('result.html', result="Image encrypted successfully!", download_url=download_url)

        elif file_type == 'audio':
            output_filename = f"encrypted_{file.filename.split('.')[0]}.wav"  # Save with .wav extension
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            encode_audio(filepath, text, output_path)
            download_url = url_for('static', filename=f'uploads/{output_filename}')
            return render_template('result.html', result="Audio encrypted successfully!", download_url=download_url)

    return render_template('encrypt.html')


@app.route('/steganography/decrypt', methods=['GET', 'POST'])
def decrypt():
    if request.method == 'POST':
        file = request.files['file']
        file_type = request.form['type']

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        if file_type == 'image':
            try:
                hidden_text = decode_image(filepath)
                return render_template('result.html', message=f"Decrypted text: {hidden_text}")
            except Exception as e:
                return render_template('result.html', message=f"Error: {str(e)}")

        elif file_type == 'audio':
            try:
                hidden_text = decode_audio(filepath)
                return render_template('result.html', message=f"Decrypted text: {hidden_text}")
            except Exception as e:
                return render_template('result.html', message=f"Error: {str(e)}")

    return render_template('decrypt.html')

if __name__ == '__main__':
    app.run(debug=True)
