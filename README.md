# Voice-First Telugu Agent — Government Scheme Assistant

Overview
- A voice-first, agentic assistant that speaks Telugu end-to-end (STT → LLM → TTS).
- Planner–Executor–Evaluator loop, rule-based eligibility tool, mock submission API, simple retrieval over local scheme data, and persistent memory across turns.

Quick setup (Windows PowerShell)
1. Create and activate a Python environment (recommended):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

2. System dependencies
- `ffmpeg` is required for audio playback with `pydub`. Install ffmpeg and ensure it's in `PATH`.
- Whisper model weights will be downloaded automatically on first run (if `whisper` is used). This can be large.

Run demo (microphone required)

```powershell
python main.py
```

Notes
- By default the agent uses OpenAI if you set `OPENAI_API_KEY` in environment variables. If not present, it runs using local fallback logic but still maintains Telugu prompts and responses.
 - Optionally integrate a free LLM: the project includes an `LLMClient` which will use the Hugging Face Inference API when `HF_API_TOKEN` (or `HUGGINGFACE_API_TOKEN`) is set. If no token is set and `transformers` is installed, it will attempt to load `google/flan-t5-small` locally (CPU). See `llm_client.py`.
- If you cannot record microphone audio, the system will fall back to typed input for testing.

LLM setup (optional)
- To use the Hugging Face Inference API (recommended if you don't want to download model weights): set `HF_API_TOKEN` environment variable to your token. The `LLMClient` will call `google/flan-t5-small`.
- To use a local model, install `transformers` and `torch` (CPU). This will download `google/flan-t5-small` on first run and may take time and disk space.


Files
- `main.py`: entrypoint and runtime loop
- `stt.py`: microphone recording and transcription (Whisper fallback)
- `tts.py`: TTS using `gTTS` (Telugu `te`)
- `agent.py`: Planner–Executor–Evaluator loop
- `tools/eligibility.py`: simple eligibility rules
- `tools/mock_api.py`: mock submission API
- `memory.py`: persistent conversation memory
- `schemes/data_te.json`: sample Telugu schemes

If you want me to run the demo here, tell me and I'll attempt to run a short end-to-end test (I may need network and model downloads).