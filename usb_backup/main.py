from threading import Thread

from .led import set_led_brightness, get_led_brightness
from .button import setup as setup_button
from .backup import backup_loop
from .webapp import app


def main():
    set_led_brightness(get_led_brightness())
    setup_button()
    Thread(target=backup_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=8000, debug=False)


if __name__ == '__main__':
    main()
