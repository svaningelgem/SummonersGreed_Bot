from time import sleep

import cv2

from summoners_greed_bot.detectors import Detected, NoSceneFound, SceneInterpreter
from summoners_greed_bot.find_window import find_window_with_title

SLEEP_X_SECONDS = 5
SLEEP_X_SECONDS = 1

def main():
    bluestacks_window = find_window_with_title('BlueStacks')
    while True:
        sleep(SLEEP_X_SECONDS)  # Take an action every x seconds to prevent stressing the 'idle' system

        screenshot = bluestacks_window.take_screenshot()
        cv2.imwrite('output.png', screenshot)

        scene = SceneInterpreter(screenshot)

        try:
            to_do = scene.what_is_here
            if to_do in (
                Detected.Monitor,
                Detected.GameFinished,
                Detected.MonsterSetup,
                Detected.SelectNewGame,
                Detected.SellerOkay
            ):
                # Click the detected button
                button = scene.location[0]

                x = button[0]
                y = button[1]
                w = button[2] - button[0]
                h = button[3] - button[1]

                bluestacks_window.click(x + w / 2, y + h / 2)
            elif to_do == Detected.Seller:
                a = 1
        except NoSceneFound:
            pass


if __name__ == '__main__':
    main()
