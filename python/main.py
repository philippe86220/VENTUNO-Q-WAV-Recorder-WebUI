from arduino.app_bricks.web_ui import WebUI
from wavrecordplay import WavRecorder
from arduino.app_utils import App

ui = WebUI()
recorder = WavRecorder()


def api_record():
    return recorder.record()


def api_stop_record():
    return recorder.stop_record()


def api_play():
    return recorder.play()


def api_stop():
    return recorder.stop()


def api_volume(value="50"):
    return recorder.set_volume(value)


def api_status():
    return recorder.status()


ui.expose_api("GET", "/api/record", api_record)
ui.expose_api("GET", "/api/stop_record", api_stop_record)
ui.expose_api("GET", "/api/play", api_play)
ui.expose_api("GET", "/api/stop", api_stop)
ui.expose_api("GET", "/api/volume", api_volume)
ui.expose_api("GET", "/api/status", api_status)

App.run()
