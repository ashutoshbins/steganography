from flask import Flask, request, render_template, send_file, url_for
import os
from encode_image import encode_image
from decode_image import decode_image
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './static/uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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