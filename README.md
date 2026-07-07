# VoiceAgent (Kokoro-82M Local TTS Server)

A high-performance, local Text-to-Speech (TTS) server built for the **AIRacer Unity** project. It leverages Python and the lightweight **Kokoro-v1.0** ONNX model to deliver real-time, low-latency audio synthesis for game commentary.

This server acts as a drop-in replacement for legacy TTS tools (like KittenTTS), automatically mapping legacy voice profiles to modern Kokoro equivalents.

## 🚀 Features

- **Unity-Ready:** Exposes a seamless POST endpoint tailored for `CommentaryEngine.cs`.
- **Legacy Voice Mapping:** Backward compatible with classic voice profiles (e.g., *Jasper*, *Bruno*) mapped directly to high-quality Kokoro models (`am_puck`, `bm_george`, etc.).
- **Fast Local Inference:** Utilizes ONNX Runtime for ultra-low latency playback inside the game loop.

## 📁 Repository Structure

```text
VoiceAgent/
├── .vscode/               # Workspace settings
├── models/                # [Ignored by Git] Local model & voice binaries
│   ├── kokoro-v1.0.onnx   
│   └── voices-v1.0.bin    
├── main.py                # FastAPI server, routing, and legacy voice mappings
├── .gitignore             # Excludes large binaries from version control
└── README.md              # Project documentation
🛠️ PrerequisitesPython 3.9 or higherUnity Project (AIRacer with CommentaryEngine.cs integrated)📦 Getting Started1. Clone the RepositoryBashgit clone [https://github.com/SahilSidhu7/VoiceAgent.git](https://github.com/SahilSidhu7/VoiceAgent.git)
cd VoiceAgent
2. Download the Model WeightsBecause model files are heavy, they are excluded via .gitignore. You must fetch them manually before launching the server.Create a models/ directory in the root folder and download these two asset files into it:kokoro-v1.0.onnx (~310 MB)voices-v1.0.bin3. Install DependenciesSet up your virtual environment and install the required packages:Bashpython -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install fastapi uvicorn onnxruntime numpy
4. Run the ServerLaunch the server before pressing Play in the Unity Editor:Bashpython main.py
The server will initialize on http://localhost:5050.🎮 Integration with UnityThe Unity CommentaryEngine.cs script communicates directly with this API out-of-the-box.API EndpointURL: http://localhost:5050/speakMethod: POSTVoice ProfilesThe server processes both native Kokoro voice identifiers (am_puck, bm_george, af_heart) and legacy client strings passed by Unity:Legacy Voice (Unity Input)Mapped Kokoro VoiceJasperAutomatically RemappedBrunoAutomatically Remapped📝 LicenseThis project is open-source and available under the MIT License.
