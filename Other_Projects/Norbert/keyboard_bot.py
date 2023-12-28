import datetime
import time

# https://stackoverflow.com/a/69659472 in case of pip install problems
import pyautogui  # pip install PyAutoGUI

pyautogui.FAILSAFE = False


class PressKey:
    def __init__(
            self,
            key_to_press,
            msec_delay_between_presses=150
    ) -> None:
        """
        Args:
            key_to_press: Key that should be pressed: https://pyautogui.readthedocs.io/en/latest/keyboard.html#keyboard-keys
            msec_delay_between_presses : Defines time between presses. Defaults to 150 ms.
        """
        self.key_to_press = key_to_press
        self.msec_delay_between_presses = msec_delay_between_presses
        self.last_press = None

    def handle(self):
        if self.last_press is None:
            pyautogui.press(self.key_to_press)
            self.last_press = datetime.datetime.now()

        # press if enougth time have been spend
        time_delta = datetime.datetime.now() - self.last_press
        if time_delta > datetime.timedelta(milliseconds=self.msec_delay_between_presses):
            pyautogui.press(self.key_to_press)
            self.last_press = datetime.datetime.now()


if __name__ == '__main__':
    z_key = PressKey('z', 2000)  # every 2 sec
    f2_key = PressKey('f2', 2000)  # every 2 sec
    space_key = PressKey('space')

    while True:
        z_key.handle()
        f2_key.handle()
        space_key.handle()
        time.sleep(0.05)  # 50msec delay not to overload cpu
