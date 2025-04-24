# Voice One-Way Translation App

This is a simple Python command-line application that records audio from your microphone,
streams it to the OpenAI real-time translation API, and prints (and optionally speaks)
the translated text in real time.

Features:
- Record audio from the default microphone
- Stream audio to OpenAI's real-time translation API (Whisper)
- Display partial and final translations as they arrive
- Optional text-to-speech playback of translations using `pyttsx3`

## Requirements
- Python 3.7 or higher
- A working microphone
- An OpenAI API key with access to the real-time speech translation API

## Installation
1. Clone this repository or copy the files to your local machine.
2. Create and activate a Python virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set your OpenAI API key as an environment variable:
   ```bash
   export OPENAI_API_KEY="your_api_key_here"  # On Windows: set OPENAI_API_KEY=your_api_key_here
   ```

## Usage
Run the application with the source and target language codes:
```bash
python main.py --source_lang en --target_lang es
```

To enable text-to-speech playback of the translated text, add the `--tts` flag (requires `pyttsx3`):
```bash
python main.py --source_lang en --target_lang es --tts
```

Press `Ctrl+C` to stop the translation session.

## Web Interface

A web-based voice translation interface is included. It records audio from your browser and displays
speech transcription and translation in real time, copying translations to your clipboard.

### Setup

1. Ensure your OpenAI API key is set in the environment (use the same key as this session):
   ```bash
   export OPENAI_API_KEY="your_api_key_here"
   ```
2. Install dependencies (if not already done):
   ```bash
   pip install -r requirements.txt
   ```
3. Start the FastAPI server:
   ```bash
   uvicorn app:app --reload
   ```
4. In your browser, navigate to `http://localhost:8000` to use the voice translation UI.
   The page will attempt to open itself in a new window sized 500×624 px. If your browser blocks this popup, please resize the window manually or launch with your browser’s
   `--window-size=500,624` (e.g. `chromium --app=http://localhost:8000 --window-size=500,624`).

**Note:** All translations are performed via the OpenAI GPT-4 Mini model for best accuracy.

### Editing Transcriptions

You can manually edit the **Speech Transcription** field. When this field loses focus (on blur), the app will re-translate your updated text into English, update the **Translation** field (and copy it to the clipboard), and then remove the `redone` attribute from the transcription field.

## License
This project is released under the MIT License.