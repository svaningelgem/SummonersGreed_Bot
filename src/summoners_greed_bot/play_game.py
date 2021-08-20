import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep
from typing import Dict

import cv2
import numpy as np

from summoners_greed_bot import logger
from summoners_greed_bot.detectors import Detected, NoSceneFound, SceneInterpreter
from summoners_greed_bot.find_window import BlueStacksWindow

CHECK_GAME_EVERY_X_SECONDS = 1.5
SAVE_IMAGE_EVERY_X_SECONDS = 120


class LastClick:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.seen = datetime.now()

last_saved_clicks: Dict[Detected, LastClick] = {}


def act_on_screenshot(bluestacks_window, screenshot):
    scene = SceneInterpreter(screenshot)

    try:
        to_do = scene.what_is_here
    except NoSceneFound:
        return

    logger.info('We detected "%s"', to_do.name)
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

        last_saved_clicks[to_do] = LastClick(new_x, new_y)

        bluestacks_window.click(new_x, new_y)


def main():
    save_counter = 0
    same_screenshot_counter = 0
    prev_screenshot = None

    bluestacks_window = BlueStacksWindow()

    def _click(e: LastClick) -> None:
        bluestacks_window.click(e.x, e.y)
        sleep(2)
        e.seen = datetime.now()

    while True:
        sleep(CHECK_GAME_EVERY_X_SECONDS)  # Take an action every x seconds to prevent stressing the 'idle' system

        screenshot = bluestacks_window.take_screenshot()

        if prev_screenshot is not None and np.allclose(prev_screenshot, screenshot):
            # Computer is locked likely... Not going to try to do anything here!
            same_screenshot_counter += 1

            if same_screenshot_counter > 5:  # 5 times the same screenshot... Let's assume we're locked.
                same_screenshot_counter = 0

                try:
                    last_game_finished = last_saved_clicks[Detected.GameFinished].seen
                    logger.info(f'last_game_finished: {last_game_finished}')
                    if last_game_finished + timedelta(minutes=35) > datetime.now():
                        continue
                except KeyError:
                    continue  # Ok, we don't even know this one yet!!

                logger.info(f'Start clicking')
                # Ok, game is likely finished. Start clicking away!
                _click(last_saved_clicks[Detected.GameFinished])
                _click(last_saved_clicks[Detected.SelectNewGame])
                _click(last_saved_clicks[Detected.MonsterSetup])
            continue

        same_screenshot_counter = 0

        prev_screenshot = screenshot

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
