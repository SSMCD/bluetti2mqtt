import os
import json
import time
from threading import Thread
import RPi.GPIO as GPIO

from .config import BUTTON_PIN, STATUS_LED_PIN, DELETE_STATE_FILE
from .log_utils import log

delete_enabled = True


def save_delete_state():
    with open(DELETE_STATE_FILE, 'w') as f:
        json.dump({"delete_enabled": delete_enabled}, f)


def load_delete_state():
    global delete_enabled
    if os.path.exists(DELETE_STATE_FILE):
        try:
            with open(DELETE_STATE_FILE) as f:
                state = json.load(f)
                delete_enabled = state.get("delete_enabled", True)
        except Exception:
            delete_enabled = True


def update_status_led():
    GPIO.output(STATUS_LED_PIN, GPIO.HIGH if delete_enabled else GPIO.LOW)


def monitor_button():
    global delete_enabled
    last_state = False
    while True:
        input_state = GPIO.input(BUTTON_PIN)
        if input_state and not last_state:
            delete_enabled = not delete_enabled
            update_status_led()
            save_delete_state()
            log(f"🔘 Taster gedrueckt – Loeschmodus: {'AN' if delete_enabled else 'AUS'}")
            time.sleep(0.3)
        last_state = input_state
        time.sleep(0.05)


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(STATUS_LED_PIN, GPIO.OUT)
    load_delete_state()
    update_status_led()
    Thread(target=monitor_button, daemon=True).start()


def delete_files_from_source(source_path):
    if not delete_enabled:
        log("[INFO] Loeschmodus deaktiviert – Dateien bleiben erhalten.")
        return
    for root, _, files in os.walk(source_path):
        for file in files:
            try:
                os.remove(os.path.join(root, file))
                log(f"[GELÖSCHT] {file}")
            except Exception as e:
                log(f"[FEHLER] Datei nicht geloescht: {file} – {e}")
