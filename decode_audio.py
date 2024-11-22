import wave

def decode_audio(input_audio_path):
    song = wave.open(input_audio_path, mode='rb')
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))
    extracted = [frame_bytes[i] & 1 for i in range(len(frame_bytes))]
    string = "".join(chr(int("".join(map(str, extracted[i:i + 8])), 2)) for i in range(0, len(extracted), 8))
    decoded = string.split("###")[0]
    song.close()
    return decoded
