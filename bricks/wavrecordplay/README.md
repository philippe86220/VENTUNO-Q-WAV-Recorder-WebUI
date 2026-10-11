# wavrecordplay — Custom Brick

`wavrecordplay` is a custom Arduino App Lab Brick for recording and playing WAV audio on the **Arduino VENTUNO Q**. It uses Linux audio facilities on the MPU.

## Features

- Start and stop microphone recording from the application.
- Play the most recent WAV recording and stop playback.
- Adjust the ALSA `Headphone` playback control.
- Query the current audio mode, playback/recording activity, volume and recording availability.
- Reuse the audio functions from Python applications through the `WavRecorder` class.

**Note:** Each new recording overwrites the previous `recording.wav` file.

## Architecture

The Brick consists of a Python interface and a dedicated audio service:

| File | Purpose |
| --- | --- |
| `__init__.py` | Defines `WavRecorder`, which sends HTTP requests to the audio service. |
| `wav_service.py` | Provides the audio endpoints and controls `arecord`, `aplay` and `amixer`. |
| `brick_config.yaml` | Declares the Brick identity (`wavrecordplay`). |
| `brick_compose.yaml` | Starts the `player` container with access to `/dev/snd` and installs `python3` and `alsa-utils`. |

The default service address in `WavRecorder` is `http://player:9000`.

## Audio configuration

The following values are defined in `wav_service.py`:

| Setting | Value |
| --- | --- |
| Capture device | `plughw:0,1` |
| Playback device | `plughw:0,0` |
| Recording format | WAV, signed 16-bit little-endian (`S16_LE`) |
| Sample rate | 44,100 Hz |
| Recording channels | 1 (mono) |
| ALSA sound card for volume | `0` |
| Mixer control | `Headphone` |
| Recording file | `recording.wav`, stored in the Brick directory |

The service uses `arecord` for capture, `aplay` for playback, and `amixer` for volume. Device indices and mixer names are specific to the tested configuration and may need adjustment on another system.

The service accepts an integer volume value from **0 to 31**. The Brick's `set_volume()` method accepts values from 0 to 100, but the service clamps them to 31; consequently, the effective mixer setting is limited to 0–31. This is the behavior of the supplied source code, not a percentage conversion.

## Using the Brick

Import `WavRecorder` in your App Lab Python application:

```python
from arduino.app_utils import App
from wavrecordplay import WavRecorder

recorder = WavRecorder()

# Example calls (normally triggered by your WebUI/API handlers):
status = recorder.status()
result = recorder.record()
# Later, after recording has started:
result = recorder.stop_record()
result = recorder.play()

App.run()
```

`record()` starts a recording that continues until stopped. To stop either recording or playback, use `stop()`; `stop_record()` is specifically for an active recording.

`WavRecorder` is a regular Python class in this project. **It is not decorated with `@brick`** and does not implement the generated Greeter example's `start()`/`loop()` lifecycle. The application imports and instantiates it directly.

### Public Python methods

| Method | Description |
| --- | --- |
| `record()` | Start recording, replacing any previous WAV file. |
| `stop_record()` | Stop the current recording and finalize the WAV file. |
| `play()` | Play the saved WAV file. |
| `stop()` | Stop recording or playback. |
| `set_volume(value)` | Request a volume change. |
| `status()` | Refresh and return the current service state. |

The methods return dictionaries with an `ok` field and additional state or error details. `status()` returns `mode`, `volume`, and `has_recording`, with the full service response in `raw`.

## Audio service endpoints

The `player` container exposes the following internal HTTP endpoints:

| Request | Purpose |
| --- | --- |
| `GET /record` | Start recording. |
| `GET /stop_record` | Stop recording. |
| `GET /play` | Start playback. |
| `GET /stop` | Stop recording or playback. |
| `GET /volume?value=16` | Set the ALSA Headphone mixer value. |
| `GET /status` | Get mode, running state, volume and recording availability. |

These are **internal service endpoints**. The main application in `python/main.py` separately exposes WebUI routes under `/api/`.

## Limitations

- Only one recording file is managed; new recordings replace it.
- Recording is mono, even if the hardware supports additional channels.
- Audio device identifiers and mixer control are currently hard-coded.
- The service uses HTTP GET requests for actions that change state.
- The supplied `brick_compose.yaml` installs its dependencies when the container starts.
- This Brick is part of the VENTUNO Q App Lab project and has not been packaged as a standalone distributable library.

## Future development

A later version of the **application** is planned to integrate the STM32 MCU and Arduino Modulino Buttons through Arduino RouterBridge, allowing physical control of recording and playback. The current MPU-only implementation provides the working audio foundation.

## Related files

For the complete application, including the WebUI and project setup, see the repository's root `README.md`.
