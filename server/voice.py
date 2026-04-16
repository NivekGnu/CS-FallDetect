import json
import queue
import subprocess
import time
import sounddevice as sd
from vosk import Model, KaldiRecognizer

class VoiceAssistant:
    def __init__(self):
        self.model = Model("../models/vosk-model-small-en-us-0.15")
    
    def speak(self, text):
        subprocess.run(["say", "-v", "Zoe (Premium)", text])
    
    def listen(self, timeout=8):
        q = queue.Queue()
        def callback(indata, frames, time, status):
            q.put(bytes(indata))
    
        rec = KaldiRecognizer(self.model, 16000, '["help", "family", "cancel", "[unk]"]')
    
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
            start = time.time()
            while time.time() - start < timeout:
                data = q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "")
                    if "help" in text:
                        return "emergency"
                    if "family" in text:
                        return "family"
                    if "cancel" in text:
                        return "cancel"
            return "no_response"
    
    def respond_to_fall(self):
        self.speak("Fall detected. Are you okay? Say help to call emergency, or family to contact a loved one. Say cancel to dismiss.")
        return self.listen(timeout=5)
 