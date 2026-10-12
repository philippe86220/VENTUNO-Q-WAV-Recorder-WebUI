from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import signal
import json
import os
import urllib.parse

HOST = "0.0.0.0"
PORT = 9000

# plughw convertit le format si besoin ; adapte le numéro de carte (arecord -l / aplay -l)
RECORD_DEVICE = "plughw:0,1"
PLAY_DEVICE = "plughw:0,0"
RECORD_RATE = "44100"
RECORD_CHANNELS = "1"
VOLUME_CARD = "0"
VOLUME_CONTROL = "Headphone" 

# Un seul fichier, réécrit à chaque nouvel enregistrement
WAV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recording.wav")

audio_process = None
mode = "idle"  # idle | recording | playing

def read_volume():
    result = subprocess.run(
        ["amixer", "-c", VOLUME_CARD, "get", VOLUME_CONTROL],
        capture_output=True,
        text=True,
        check=True,
    )

    for line in result.stdout.splitlines():
        if "Front Left:" in line:
            return int(line.split()[2])

    raise RuntimeError("Volume Headphone introuvable")


volume = read_volume()


def stop_audio():
    """Arrête l'enregistrement ou la lecture en cours."""
    global audio_process, mode

    if audio_process is not None:
        if audio_process.poll() is None:
            try:
                # SIGINT : arecord finalise correctement l'en-tête du WAV
                audio_process.send_signal(signal.SIGINT)
                audio_process.wait(timeout=3)
            except Exception:
                try:
                    audio_process.kill()
                    audio_process.wait(timeout=2)
                except Exception:
                    pass
        audio_process = None

    mode = "idle"


def start_record():
    global audio_process, mode

    stop_audio()

    # Sans -d : enregistre jusqu'à l'arrêt ; le fichier existant est écrasé
    audio_process = subprocess.Popen(
        [
            "arecord",
            "-D", RECORD_DEVICE,
            "-f", "S16_LE",
            "-r", RECORD_RATE,
            "-c", RECORD_CHANNELS,
            "-t", "wav",
            WAV_FILE,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    mode = "recording"

    return {"ok": True, "mode": mode, "file": WAV_FILE}


def stop_record():
    if mode != "recording":
        return {"ok": False, "error": "Not recording", "mode": mode}

    stop_audio()
    size = os.path.getsize(WAV_FILE) if os.path.exists(WAV_FILE) else 0

    return {"ok": True, "mode": "idle", "file": WAV_FILE, "bytes": size}


def play_wav():
    global audio_process, mode

    if not os.path.exists(WAV_FILE):
        return {"ok": False, "error": "No recording"}

    stop_audio()

    audio_process = subprocess.Popen(
        ["aplay", "-D", PLAY_DEVICE, WAV_FILE],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    mode = "playing"

    return {"ok": True, "mode": mode, "file": WAV_FILE}


def set_volume(value):
    global volume

    try:
        value = int(value)
    except (TypeError, ValueError):
        return {"ok": False, "volume": volume, "error": "Valeur invalide"}

    value = max(0, min(31, value))

    r = subprocess.run(
        ["amixer", "-c", VOLUME_CARD, "sset", VOLUME_CONTROL, str(value)],
        capture_output=True,
        text=True,
    )

    if r.returncode == 0:
        volume = read_volume()
        return {"ok": True, "volume": volume}

    return {"ok": False, "volume": volume, "error": r.stderr.strip()}


def get_status():
    global mode

    running = audio_process is not None and audio_process.poll() is None

    # Lecture terminée d'elle-même, ou processus arrêté
    if not running and mode != "idle":
        mode = "idle"

    return {
        "ok": True,
        "mode": mode,
        "running": running,
        "volume": volume,
        "has_recording": os.path.exists(WAV_FILE),
    }


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, data):
        body = json.dumps(data).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.strip("/")
        query = urllib.parse.parse_qs(parsed.query)

        if path == "record":
            self._send_json(start_record())
            return

        if path == "stop_record":
            self._send_json(stop_record())
            return

        if path == "play":
            self._send_json(play_wav())
            return

        if path == "stop":
            stop_audio()
            self._send_json({"ok": True, "mode": "idle", "running": False})
            return

        if path == "status":
            self._send_json(get_status())
            return

        if path == "volume":
            value = query.get("value", ["16"])[0]
            self._send_json(set_volume(value))
            return

        self._send_json({"ok": False, "error": "Not found", "path": path})


if __name__ == "__main__":
    print("[wav_service] starting on port", PORT)
    HTTPServer((HOST, PORT), Handler).serve_forever()
