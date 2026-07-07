"""
Kokoro-82M Local TTS Server for AIRacer Unity project.
Run this BEFORE pressing Play in Unity.

Usage:
    python main.py

Then in Unity, CommentaryEngine.cs sends POST requests to:
    http://localhost:5050/speak

Model files (downloaded once into ./models/):
    kokoro-v1.0.onnx   https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
    voices-v1.0.bin    https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin

Unity keeps sending the old KittenTTS voice names ("Jasper", "Bruno") —
they are mapped to Kokoro voices below. Raw Kokoro names (am_puck, bm_george,
af_heart, ...) also work directly.
"""

import io
import json

import onnxruntime as ort
import soundfile as sf
from flask import Flask, request, Response
from kokoro_onnx import Kokoro

app = Flask(__name__)

MODEL_PATH  = "models/kokoro-v1.0.onnx"
VOICES_PATH = "models/voices-v1.0.bin"

# Old KittenTTS names → Kokoro voices, so Unity needs no changes.
VOICE_MAP = {
    "Jasper": "am_puck",    # play-by-play: male, energetic
    "Bruno":  "bm_george",  # analyst: male, deeper, British
}

# ── Load model once at startup ─────────────────────────────────────────────────
# Cap ONNX threads so TTS doesn't starve the other heavy tasks on this machine.
print(f"[Kokoro Server] Loading model: {MODEL_PATH}")
sess_opts = ort.SessionOptions()
sess_opts.intra_op_num_threads = 4
session = ort.InferenceSession(MODEL_PATH, sess_options=sess_opts,
                               providers=["CPUExecutionProvider"])
tts = Kokoro.from_session(session, VOICES_PATH)
print(f"[Kokoro Server] Model loaded. Voices: {sorted(tts.get_voices())}")
print("[Kokoro Server] Listening on http://localhost:5050")
print("[Kokoro Server] Press Ctrl+C to stop.")

# ── Endpoint: POST /speak ──────────────────────────────────────────────────────
# Body (JSON): { "text": "...", "voice": "Jasper", "speed": 1.05 }
# Response:    raw WAV bytes (Unity reads these into an AudioClip)
@app.route("/speak", methods=["POST"])
def speak():
    data  = request.get_json(force=True)
    text  = data.get("text", "")
    voice = data.get("voice", "Jasper")
    speed = float(data.get("speed", 1.05))
    voice = VOICE_MAP.get(voice, voice)

    if not text:
        return Response("No text provided", status=400)

    print(f"[Kokoro] [{voice}] {text[:80]}{'...' if len(text) > 80 else ''}")

    samples, sample_rate = tts.create(text, voice=voice, speed=speed, lang="en-us")

    # Convert numpy array → WAV bytes in memory (no temp files)
    buffer = io.BytesIO()
    sf.write(buffer, samples, samplerate=sample_rate, format="WAV", subtype="PCM_16")
    buffer.seek(0)
    wav_bytes = buffer.read()

    return Response(
        wav_bytes,
        status=200,
        mimetype="audio/wav",
        headers={"Content-Length": str(len(wav_bytes))}
    )

# ── Endpoint: GET /health ──────────────────────────────────────────────────────
# Unity checks this on Start() to confirm the server is up before racing begins.
@app.route("/health", methods=["GET"])
def health():
    return Response("OK", status=200)

# ── Endpoint: GET /voices ──────────────────────────────────────────────────────
@app.route("/voices", methods=["GET"])
def voices():
    return Response(json.dumps(sorted(tts.get_voices())), mimetype="application/json")


if __name__ == "__main__":
    # threaded=False keeps audio generation sequential so lines don't overlap
    app.run(host="127.0.0.1", port=5050, threaded=False)
