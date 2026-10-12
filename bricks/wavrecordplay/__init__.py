import json
import time
from urllib.request import urlopen
from urllib.error import URLError, HTTPError


class WavRecorder:
    def __init__(self, host="http://player:9000"):
        self.host = host
        self.mode = "idle"  # idle | recording | playing
        self.volume = 16

    def _get_json(self, path):
        try:
            # timeout un peu plus long : l'arrêt de arecord peut prendre quelques secondes
            with urlopen(self.host + path, timeout=5) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as e:
            return {"ok": False, "error": "HTTP error", "code": e.code}
        except URLError as e:
            return {"ok": False, "error": "URL error", "details": str(e)}
        except Exception as e:
            return {"ok": False, "error": "Unexpected error", "details": str(e)}

    def record(self):
        """Démarre l'enregistrement (sans limite de durée, écrase le WAV existant)."""
        result = self._get_json("/record")

        if result.get("ok"):
            self.mode = "recording"

        return {
            "ok": result.get("ok", False),
            "mode": self.mode,
            "raw": result
        }

    def stop_record(self):
        """Arrête l'enregistrement en cours."""
        result = self._get_json("/stop_record")

        if result.get("ok"):
            self.mode = "idle"

        return {
            "ok": result.get("ok", False),
            "mode": self.mode,
            "raw": result
        }

    def play(self):
        """Lit le fichier WAV."""
        result = self._get_json("/play")

        if result.get("ok"):
            self.mode = "playing"

        return {
            "ok": result.get("ok", False),
            "mode": self.mode,
            "raw": result
        }

    def stop(self):
        """Arrête l'enregistrement ou la lecture en cours."""
        result = self._get_json("/stop")

        if result.get("ok"):
            self.mode = "idle"

        return {
            "ok": result.get("ok", False),
            "mode": self.mode,
            "raw": result
        }

    def set_volume(self, value):
        try:
            value = int(value)
        except Exception:
            value = 16

        value = max(0, min(31, value))

        result = self._get_json("/volume?value=" + str(value))

        if result.get("ok"):
            self.volume = value

        return {
            "ok": result.get("ok", False),
            "volume": self.volume,
            "raw": result
        }

    def status(self):
        """Interroge le service : la lecture se termine d'elle-même, l'état local peut être périmé."""
        result = self._get_json("/status")

        if result.get("ok"):
            self.mode = result.get("mode", self.mode)
            self.volume = result.get("volume", self.volume)

        return {
            "ok": result.get("ok", False),
            "mode": self.mode,
            "volume": self.volume,
            "has_recording": result.get("has_recording", False),
            "raw": result
        }

    def run(self):
        print("[WavRecorder brick] App running")
        while True:
            time.sleep(1)

