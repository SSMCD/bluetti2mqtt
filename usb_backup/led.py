import os
import time
import colorsys
import board
import neopixel
from threading import Thread

from .config import PIXEL_COUNT, PIN, BRIGHTNESS_FILE
from .log_utils import log

pixels = neopixel.NeoPixel(board.D18, PIXEL_COUNT, auto_write=False, brightness=0.5)
LED_ENABLED = True


def rainbow_color(pos, total):
    hue = pos / total
    r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, 1, 1)]
    return (r, g, b)


def set_led_brightness(value):
    try:
        value = float(value)
        value = max(0, min(value, 1))
        pixels.brightness = value
        with open(BRIGHTNESS_FILE, 'w') as f:
            f.write(str(value))
    except Exception as e:
        log(f"Fehler LED-Helligkeit: {e}")


def get_led_brightness():
    try:
        if os.path.exists(BRIGHTNESS_FILE):
            with open(BRIGHTNESS_FILE) as f:
                return float(f.read())
    except Exception:
        pass
    return 0.5


def set_led_enabled(onoff: bool):
    global LED_ENABLED
    LED_ENABLED = bool(onoff)
    if not LED_ENABLED:
        pixels.fill((0, 0, 0))
        pixels.show()


def blink_leds(color, times):
    if not LED_ENABLED:
        return
    for _ in range(times):
        pixels.fill(color)
        pixels.show()
        time.sleep(0.4)
        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(0.4)


class LoadingAnimation(Thread):
    def __init__(self, progress_func):
        super().__init__()
        self.progress_func = progress_func
        self.running = True

    def run(self):
        total_leds = PIXEL_COUNT
        fixed_led_index = total_leds - 1
        animation_index = 0
        while self.running and LED_ENABLED:
            progress_percent = self.progress_func()
            leds_done = int(progress_percent / 10)
            pixels.fill((0, 0, 0))
            pixels[fixed_led_index] = rainbow_color(fixed_led_index, total_leds)
            for i in range(leds_done):
                led_index = fixed_led_index - i
                pixels[led_index] = rainbow_color(led_index, total_leds)
            if progress_percent < 100 and leds_done < fixed_led_index:
                animation_range = fixed_led_index - leds_done
                animation_pos = animation_index % (animation_range + 1)
                led_index = leds_done + animation_pos
                if led_index < fixed_led_index:
                    pixels[led_index] = rainbow_color(led_index, total_leds)
                animation_index += 1
            pixels.show()
            time.sleep(0.2)
        pixels.fill((0, 0, 0))
        pixels.show()
