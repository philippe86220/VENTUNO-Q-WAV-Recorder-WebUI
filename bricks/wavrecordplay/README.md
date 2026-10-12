# wavrecordplay — Custom Brick

`wavrecordplay` is a custom Arduino App Lab Brick for recording and playing WAV audio on the **Arduino VENTUNO Q**. It uses ALSA audio facilities on the Linux MPU.

## Features

- Start and stop microphone recording.
- Play a WAV recording and stop playback.
- Adjust the ALSA `Headphone` mixer level.
- Retrieve the audio mode, volume, process activity and recording availability.
- Access these functions from an App Lab Python application through the `WavRecorder` class.

**Note:** Each new recording overwrites the previous `recording.wav` file.

## Architecture

The Brick provides a Python interface to a dedicated audio service running in the `player` container.

| File | Purpose |
| --- | --- |
| `__init__.py` | Defines the `WavRecorder` class, which sends HTTP requests to the audio service. |
| `wav_service.py` | Implements the HTTP endpoints and controls `arecord`, `aplay` and `amixer`. |
| `brick_config.yaml` | Declares the Brick identity (`wavrecordplay`). |
| `brick_compose.yaml` | Configures the `player` container, its access to `/dev/snd`, and installation of `python3` and `alsa-utils`. |

The default service address used by `WavRecorder` is `http://player:9000`.

## Audio configuration

The following settings are defined in `wav_service.py`:

| Setting | Value |
| --- | --- |
| Capture device | `plughw:0,1` |
| Playback device | `plughw:0,0` |
| Recording format | WAV, signed 16-bit PCM (`S16_LE`) |
| Sample rate | 44,100 Hz |
| Recording channels | 1 (mono) |
| ALSA card for volume | `0` |
| Mixer control | `Headphone` |
| Recording file | `recording.wav` in the Brick directory |

The service uses `arecord` to record, `aplay` to play audio and `amixer` to read or set the volume. Device numbers and mixer controls may differ on other systems.

The volume control uses **integer mixer values from 0 to 31**, not percentages. The `WavRecorder.set_volume()` method and the audio service both clamp values to this range. 

To inspect your audio configuration:

```bash
cat /proc/asound/cards
arecord -l
aplay -l
amixer -c 0 get Headphone
```

## Using the Brick

Import and instantiate `WavRecorder` in your App Lab Python application:

```python
from arduino.app_utils import App
from wavrecordplay import WavRecorder

recorder = WavRecorder()

# Call these methods from your application's handlers as needed:
# recorder.record()
# recorder.stop_record()
# recorder.play()
# recorder.stop()
# recorder.set_volume(16)
# recorder.status()

App.run()
```

`WavRecorder` is a Python class providing an interface to the audio service. The application imports and instantiates it directly.

### Public Python methods

| Method | Description |
| --- | --- |
| `record()` | Start recording to `recording.wav`. |
| `stop_record()` | Stop the active recording and finalize the WAV file. |
| `play()` | Play the saved WAV recording. |
| `stop()` | Stop recording or playback. |
| `set_volume(value)` | Set the `Headphone` mixer level (0–31). |
| `status()` | Refresh the current service state. |

These methods return dictionaries indicating success or failure. 

The `status()` result includes `ok`, `mode`, `volume`, `has_recording` and the complete service response under `raw`. The service response also includes `running`.

## Audio service endpoints

The `player` container handles these internal HTTP requests in `wav_service.py`:

| Request | Purpose |
| --- | --- |
| `GET /record` | Start recording. |
| `GET /stop_record` | Stop the active recording. |
| `GET /play` | Start WAV playback. |
| `GET /stop` | Stop recording or playback. |
| `GET /volume?value=<value>` | Set the ALSA `Headphone` mixer level (0–31). |
| `GET /status` | Retrieve the current audio state and recording availability. |

These are **internal service endpoints**, distinct from the `/api/` routes exposed by the application's `python/main.py` for its WebUI.

## Limitations

- Recording is currently configured for mono audio (one channel). Stereo recording has not been tested.
- ALSA device identifiers and the mixer control are configured directly in `wav_service.py`.
- The service uses HTTP GET requests for operations that change state.
- The supplied container configuration installs dependencies when the container starts; the first start may require access to package repositories.
- The Brick is included in this App Lab project; it is not distributed as a separate Python package.

## Related files

For the complete application, WebUI controls and setup instructions, see the repository's root [`README.md`](../../README.md).
