from time import sleep

import cv2

from summoners_greed_bot.detectors import Detected, NoSceneFound, SceneInterpreter
from summoners_greed_bot.find_window import BlueStacksWindow

CHECK_GAME_EVERY_X_SECONDS = 3
SAVE_IMAGE_EVERY_X_SECONDS = 120


def main():
    save_counter = 0

    bluestacks_window = BlueStacksWindow()
    while True:
        sleep(CHECK_GAME_EVERY_X_SECONDS)  # Take an action every x seconds to prevent stressing the 'idle' system

        screenshot = bluestacks_window.take_screenshot()

        save_counter += 1
        if save_counter % (SAVE_IMAGE_EVERY_X_SECONDS // CHECK_GAME_EVERY_X_SECONDS) == 0:
            cv2.imwrite('output.png', screenshot)

        scene = SceneInterpreter(screenshot)

        try:
            to_do = scene.what_is_here
            if to_do in (
                Detected.Monitor,
                Detected.GameFinished,
                Detected.MonsterSetup,
                Detected.SelectNewGame,
                Detected.SellerOkay,
                Detected.Seller,
            ):
                # Click the detected button
                x, y, w, h = scene.location

                new_x = x + w / 2
                new_y = y + h / 2

                # In case of the seller: click the buy-button instead!
                if to_do == Detected.Seller:
                    new_x += 250

                bluestacks_window.click(new_x, new_y)
        except NoSceneFound:
            pass


if __name__ == '__main__':
    main()
