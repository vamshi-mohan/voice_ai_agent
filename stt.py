import os
import tempfile
import sys

try:
    import sounddevice as sd
    from scipy.io.wavfile import write
except Exception:
    sd = None

def record_audio(path: str, duration: int = 6, fs: int = 16000):
    if sd is None:
        raise RuntimeError("sounddevice not available; fallback to typed input")
    print(f"Recording {duration}s — speak now...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    write(path, fs, recording)
    print(f"Saved recording to {path}")

def transcribe(audio_path: str, language: str = "te") -> dict:
    # Try whisper if available
    try:
        import whisper
        model = whisper.load_model("small")
        result = model.transcribe(audio_path, language=language)
        return {"text": result.get("text", "").strip(), "confidence": None}
    except Exception:
        # fallback: ask user to type (useful for testing without models)
        txt = input("(Fallback) Please type what the user said in Telugu: ")
        return {"text": txt.strip(), "confidence": None}

if __name__ == "__main__":
    # quick test
    tmp = os.path.join(tempfile.gettempdir(), "voice_ai_input.wav")
    try:
        record_audio(tmp, duration=5)
        print(transcribe(tmp))
    except RuntimeError as e:
        print(str(e))