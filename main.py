#!/usr/bin/env python3
"""
Voice One-Way Translation: record audio from microphone, stream to OpenAI real-time translation API,
and display (and optionally speak) translated text in real time.
"""
import os
import sys
import json
import argparse
import asyncio
try:
    import websockets
except ImportError:
    print("Error: websockets is required. Install with 'pip install websockets'.")
    sys.exit(1)

# Optional text-to-speech
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

# Audio settings
SAMPLE_RATE = 16000
CHUNK = 1024  # frames per buffer


async def translate_stream(source_lang: str, target_lang: str, tts: bool):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set the OPENAI_API_KEY environment variable.")
        return
    # Import sounddevice for audio capture
    try:
        import sounddevice as sd
    except ImportError:
        print("Error: sounddevice is required. Install with 'pip install sounddevice'.")
        return
    except OSError:
        print("Error: PortAudio library not found. Please install PortAudio (e.g. 'apt-get install portaudio19-dev') and reinstall sounddevice.")
        return
    # Build WebSocket URL for real-time translation
    url = (
        f"wss://api.openai.com/v1/audio/streams/translate"
        f"?model=whisper-1&source_language={source_lang}&target_language={target_lang}"
    )
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        async with websockets.connect(url, extra_headers=headers, ping_interval=None) as ws:
            # Initialize TTS engine if requested
            engine = None
            if tts:
                engine = pyttsx3.init()
            print(f"Recording and translating: {source_lang} -> {target_lang}. Ctrl+C to stop.")
            # Open microphone stream
            with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=CHUNK, dtype='int16', channels=1) as stream:
                while True:
                    try:
                        data = stream.read(CHUNK)[0]
                    except Exception as e:
                        print(f"Error reading audio stream: {e}")
                        break
                    # Send raw audio bytes
                    await ws.send(data)
                    # Receive response
                    try:
                        msg = await ws.recv()
                    except websockets.ConnectionClosed:
                        print("Connection closed by server.")
                        break
                    # Parse JSON message
                    try:
                        payload = json.loads(msg)
                    except json.JSONDecodeError:
                        continue
                    text = payload.get("text")
                    if text:
                        print(text)
                        if tts and engine:
                            engine.say(text)
                            engine.runAndWait()
                    # End of translation session
                    mtype = payload.get("type", "")
                    if mtype.endswith("end"):
                        print("Translation session ended.")
                        break
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as e:
        print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="Real-time voice translation using OpenAI API")
    parser.add_argument("--source_lang", required=True, help="Source language code, e.g., en")
    parser.add_argument("--target_lang", required=True, help="Target language code, e.g., es")
    parser.add_argument("--tts", action="store_true", help="Enable text-to-speech for translations")
    args = parser.parse_args()
    if args.tts and not TTS_AVAILABLE:
        print("Text-to-speech requested but pyttsx3 is not installed.")
        print("Install with 'pip install pyttsx3' or run without --tts.")
        sys.exit(1)
    try:
        asyncio.run(translate_stream(args.source_lang, args.target_lang, args.tts))
    except KeyboardInterrupt:
        print("Exiting.")


if __name__ == "__main__":
    main()