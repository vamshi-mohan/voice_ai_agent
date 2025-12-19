import os
import tempfile
from gtts import gTTS
import subprocess

def speak(text: str, lang: str = "te"):
    try:
        tts = gTTS(text=text, lang=lang)
        tmp = os.path.join(tempfile.gettempdir(), "voice_ai_out.mp3")
        tts.save(tmp)
        # Prefer OS default player on Windows
        if os.name == 'nt':
            os.startfile(tmp)
        else:
            # Try ffplay if available
            subprocess.run(["ffplay", "-nodisp", "-autoexit", tmp], check=False)
    except Exception:
        print(text)

if __name__ == "__main__":
    speak("నమస్తే! నేను మీకు సహాయం చేయడానికి సిద్ధంగా ఉన్నాను.")