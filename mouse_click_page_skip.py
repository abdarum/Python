from pynput import mouse
from pynput import keyboard
import logging
import time


def main():
    logging.basicConfig(filename=("mouse_log.txt"), level=logging.DEBUG,
            format='%(asctime)s: %(message)s')

    global virtual_keyboard
    virtual_keyboard = keyboard.Controller()

    global was_pressed
    was_pressed = False


    with mouse.Listener(on_move=on_move, on_click=on_click,
            on_scroll=on_scroll) as listener:
        listener.join()

def debug(msg, active=False):
    if active:
        print(msg)

def on_move(x, y):
    logging.info("Mouse moved to ({0}, {1})".format(x, y))

def on_click(x, y, button, pressed):
    if pressed:
        logging.info('Mouse clicked at ({0}, {1}) with {2}'.\
                format(x, y, button))

        debug("pressed "+str(button))
        #elif was_pressed:
        if button == mouse.Button.left:
            debug("pressed left")
            virtual_keyboard.press(keyboard.Key.right)
            virtual_keyboard.release(keyboard.Key.right)
        if button == mouse.Button.right:
            debug("pressed right")
            time.sleep(.20)
            virtual_keyboard.press(keyboard.Key.esc)
            virtual_keyboard.release(keyboard.Key.esc)
            virtual_keyboard.press(keyboard.Key.left)
            virtual_keyboard.release(keyboard.Key.left)


def on_scroll(x, y, dx, dy):
    logging.info('Mouse scrolled at ({0}, {1})({2}, {3})'.\
            format(x, y, dx, dy))


main()



