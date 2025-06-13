import speech_recognition as sr
import tempfile
import os

def transcribe_audio_from_file(audio_bytes):
    recognizer = sr.Recognizer()

    # Save bytes as a temporary WAV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(audio_bytes)
        temp_audio_path = temp_audio.name

    with sr.AudioFile(temp_audio_path) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_sphinx(audio)  # Offline recognition
        return text
    except sr.UnknownValueError:
        return "Could not understand the audio."
    except sr.RequestError as e:
        return f"Sphinx error: {e}"
    finally:
        os.remove(temp_audio_path)
