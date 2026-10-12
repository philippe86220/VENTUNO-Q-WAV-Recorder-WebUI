# 🎙️ VENTUNO Q — WAV Recorder & Player with WebUI

A simple audio recording and playback application for the **Arduino VENTUNO Q**, built with **Arduino App Lab**.

The application runs entirely on the **Linux MPU**.

It demonstrates how to combine an App Lab **custom Python brick**, a small ALSA-backed audio service, and a browser-based **WebUI**.

## Features

- Record audio to a WAV file from the VENTUNO Q audio input.
- Stop recording and finalize the WAV file.
- Play the latest recording through the configured audio output.
- Stop recording or playback from the WebUI.
- Adjust the `Headphone` mixer level with a slider (raw ALSA values **0–31**).
- Display the current state (`idle`, `recording`, or `playing`) and whether a recording is available.
- Refresh status automatically while the WebUI is open.

**Note:** Each new recording replaces the previous `recording.wav` file. Recording continues until stopped; there is no fixed duration in the current implementation.

## Tested configuration

- Board: **Arduino VENTUNO Q**
- Audio hardware: **Arduino VENTUNO Q Media Carrier**, using its microphone input and `Headphone` audio output.
- Operating system: **Ubuntu 24.04 LTS** on the VENTUNO Q
- Application environment: **Arduino App Lab**
- Audio backend: **ALSA**, using `arecord`, `aplay`, and `amixer`
- Application type: **Python + WebUI + custom brick**

The audio device identifiers below match the author's tested configuration. They may need adjustment on other systems or after changes to the ALSA device order.

## Audio configuration

The application uses the **VENTUNO Q Media Carrier** for audio capture and playback. The microphone is connected to the Media Carrier's audio input, and playback uses its `Headphone` output.

The audio service is implemented in `bricks/wavrecordplay/wav_service.py` and currently uses:

```python
RECORD_DEVICE = "plughw:0,1"
PLAY_DEVICE = "plughw:0,0"
RECORD_RATE = "44100"
RECORD_CHANNELS = "1"
VOLUME_CARD = "0"
VOLUME_CONTROL = "Headphone"
```

Recordings are **16-bit PCM, mono, 44.1 kHz**, stored as WAV.

The volume slider uses the mixer’s **raw range of 0–31**, not a percentage scale. The initial value is read from ALSA when the audio service starts.

To inspect the available devices and mixer controls on your board:

```bash
cat /proc/asound/cards
arecord -l
aplay -l
amixer -c 0 get Headphone
```

If your devices differ, edit the constants in `wav_service.py` before starting the application.

## Project structure

```text
ventuno-q-wav-brick-webui/
├── app.yaml
├── assets/
│   └── index.html                 # WebUI (HTML / JavaScript)
├── bricks/
│   └── wavrecordplay/
│       ├── __init__.py            # Python interface to the audio service
│       ├── brick_config.yaml
│       ├── brick_compose.yaml     # Player service container
│       └── wav_service.py         # ALSA recording/playback HTTP service
├── python/
│   └── main.py                    # WebUI API registration and App Lab entry point
└── LICENSE
```

The application may also create `bricks/wavrecordplay/recording.wav` at runtime.

## Getting started

1. Copy or clone this project to your VENTUNO Q.
2. Open the project in **Arduino App Lab**.
3. Check that the configured ALSA capture, playback, and mixer devices match your board.
4. Start the application in App Lab and wait for the `main` and `player` services to start.
5. The application's **WebUI** normally opens automatically when the application starts in Arduino App Lab.   
   If it does not open, check the **Python logs** in App Lab. The WebUI URL is displayed there.   
   Open the provided URL in your web browser to access the application's controls.
6. Use **Enregistrer** to start recording, **Arrêter l'enregistrement** to finish, and **Lire** to play the resulting WAV file.

The **Stop** button stops playback. The **Arrêter l'enregistrement** button stops recording. The volume slider adjusts the configured `Headphone` mixer level.

### First start

The `player` container is based on `debian:bookworm-slim`. Its startup command installs `python3` and `alsa-utils` using APT, so the first start requires access to the relevant Debian package repositories and may take longer.

## How it works

```text
Browser / WebUI
      |
      | GET /api/...
      v
Arduino App Lab (python/main.py)
      |
      v
WavRecorder custom brick
      |
      | HTTP requests to player:9000
      v
Audio service (wav_service.py)
      |
      +--> arecord --> recording.wav
      +--> aplay   <-- recording.wav
      +--> amixer  --> Headphone volume
```

The audio player runs as a dedicated Docker service, communicating with the main application over HTTP on port 9000.   
The custom brick forwards requests to a separate audio service, which manages the ALSA command-line tools.   
The WebUI communicates with Python endpoints exposed through App Lab.    

### WebUI endpoints

| Endpoint | Purpose |
| --- | --- |
| `GET /api/record` | Start recording |
| `GET /api/stop_record` | Stop recording and finalize the WAV |
| `GET /api/play` | Play the latest recording |
| `GET /api/stop` | Stop recording or playback |
| `GET /api/volume?value=16` | Set raw mixer volume (0–31) |
| `GET /api/status` | Get mode, volume, running state, and recording availability |

These endpoints are intended for the local App Lab WebUI. The current implementation uses GET requests for actions that change state.

## Current limitations

- Only one recording file is managed; starting a new recording overwrites it.
- The application does not include a download button.
- Audio device names and mixer settings are currently configured in source code.

## Notes

This is an educational App Lab project focused on integrating a custom brick with Linux audio services and a WebUI.

## Planned evolution

The next development stage is to add **physical controls** using **Arduino Modulino Buttons** connected to the VENTUNO Q's **STM32 MCU**.

Planned work includes:

- Start and stop WAV recording using Modulino buttons.
- Trigger playback from a physical button.
- Use **Arduino RouterBridge** for communication between the MCU and the Linux MPU.
- Explore button LED feedback for recording and playback states.

These are **planned features**, not part of the current release. The current WebUI will remain useful for operating the recorder independently.

## Development and acknowledgments

This project was developed and tested on the **Arduino VENTUNO Q** by its author, with assistance from **ChatGPT (OpenAI)** for technical discussions, troubleshooting, code review, and documentation.

The application has been validated through hands-on testing on the board. ChatGPT's suggestions do not replace testing on the actual hardware.

## License

See the included [`LICENSE`](LICENSE) file.
