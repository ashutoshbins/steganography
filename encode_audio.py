import wave

def encode_audio(input_audio_path, text, output_audio_path):
    song = wave.open(input_audio_path, mode='rb')
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))
    text += int((len(frame_bytes) - (len(text) * 8 * 8)) / 8) * '#'
    bits = list(map(int, ''.join([bin(ord(i)).lstrip('0b').rjust(8, '0') for i in text])))
    for i, bit in enumerate(bits):
        frame_bytes[i] = (frame_bytes[i] & 254) | bit
    frame_modified = bytes(frame_bytes)
    with wave.open(output_audio_path, 'wb') as fd:
        fd.setparams(song.getparams())
        fd.writeframes(frame_modified)
    song.close()
