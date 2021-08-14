import logging
import time
from datetime import datetime
from pathlib import Path
from time import sleep

import cv2

from summoners_greed_bot import logger
from summoners_greed_bot.detectors import Detected, NoSceneFound, SceneInterpreter
from summoners_greed_bot.find_window import BlueStacksWindow

CHECK_GAME_EVERY_X_SECONDS = 1.5
SAVE_IMAGE_EVERY_X_SECONDS = 120


def act_on_screenshot(bluestacks_window, screenshot):
    scene = SceneInterpreter(screenshot)

    try:
        to_do = scene.what_is_here

        logger.debug('We detected "%s"', to_do.name)
        if logger.isEnabledFor(logging.DEBUG):
            cv2.imwrite("debug_screenshot.png", screenshot)

        # Click the detected button
        for idx, (x, y, w, h) in enumerate(scene.locations):
            if idx > 0:
                time.sleep(0.3)

            new_x = x + w / 2
            new_y = y + h / 2

            # In case of the seller: click the buy-button instead!
            if to_do == Detected.Seller:
                new_x += 250

            bluestacks_window.click(new_x, new_y)
    except NoSceneFound:
        pass


def main():
    save_counter = 0

    bluestacks_window = BlueStacksWindow()
    while True:
        sleep(CHECK_GAME_EVERY_X_SECONDS)  # Take an action every x seconds to prevent stressing the 'idle' system

        screenshot = bluestacks_window.take_screenshot()

        save_counter += 1
        if (
            # logger.isEnabledFor(logging.DEBUG) and
            save_counter % (SAVE_IMAGE_EVERY_X_SECONDS // CHECK_GAME_EVERY_X_SECONDS) == 0
        ):
            output = Path(__file__).parent / datetime.now().strftime('screenshots/%Y%m%d/%H/%M%S.png')
            output.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(output), screenshot)

        act_on_screenshot(bluestacks_window, screenshot)


if __name__ == '__main__':
    act_on_screenshot(
        None,
        cv2.imread('../../tests/monitor/BlueStacks-2021-08-13 06_54_45.png')
    )
