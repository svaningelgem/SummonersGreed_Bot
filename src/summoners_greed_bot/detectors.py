import logging
import math
from abc import ABC
from collections import namedtuple
from enum import Enum, auto
from pathlib import Path
from time import time
from typing import Dict, Generator, List, Optional, Union

import cv2
import numpy as np

from summoners_greed_bot import logger
from summoners_greed_bot.find_subimage import _locateAll_opencv

Rect = namedtuple('Rect', 'x y w h')


def _get_image(img):
    if isinstance(img, np.ndarray):
        if len(img.shape) == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img.copy()

    orig_img = img
    if isinstance(img, str):
        img = Path(img)
        if not img.exists():
            img = Path(__file__).parent / img
            if not img.exists():
                raise FileNotFoundError(orig_img)

    return cv2.imread(str(img.absolute()), cv2.IMREAD_GRAYSCALE)


class Detector(ABC):
    IMAGE_TO_FIND = None
    counter = 0
    _confidence = 0.75

    def __init__(self):
        self.image_to_find = _get_image(self.IMAGE_TO_FIND)
        self._last_width_height = None
        self._last_locations = None

    @property
    def last_width_height(self):
        return self._last_width_height

    @property
    def last_locations(self):
        return self._last_locations

    def _rescale(self, h, w):
        return 0, h, 0, w

    def _get_scale_slices(self, h, w):
        tpl = self._rescale(h, w)

        h, w = int(h), int(w)

        if not isinstance(tpl, tuple):
            tpl = (tpl, h, 0, w)
        elif len(tpl) == 1:
            tpl = (*tpl, h, 0, w)
        elif len(tpl) == 2:
            tpl = (*tpl, 0, w)
        elif len(tpl) == 3:
            tpl = (*tpl, w)

        height_slice = slice(int(tpl[0]), int(tpl[1]) or h)
        width_slice = slice(int(tpl[2]), int(tpl[3]) or w)

        return height_slice, width_slice

    def _get_scaled_image(self, img):
        img = _get_image(img)

        self._last_width_height = img.shape

        h, w = self._last_width_height
        height_slice, width_slice = self._get_scale_slices(h, w)

        img = img[height_slice, width_slice]

        self._dump(img)

        return img

    @staticmethod
    def _calc_distance(a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def _group_locations(self, locations) -> Union[List[Rect], Generator[Rect, None, None]]:
        if not locations:
            return []

        groups = {}
        for loc in locations:
            for group, lst in groups.items():
                if self._calc_distance(group, loc) < 20:
                    lst.append(loc)
                    break
            else:
                groups[loc] = [loc]

        for lst in groups.values():
            yield Rect(*[
                int(sum(x) / len(x))
                for x in zip(*lst)
            ])

    def is_present(self, inside_this_image):
        img = self._get_scaled_image(inside_this_image)

        if logger.isEnabledFor(logging.DEBUG):
            cv2.imwrite("needle.png", self.image_to_find)
            cv2.imwrite("haystack.png", img)

        self._last_locations = list(
            self._group_locations(
                _locateAll_opencv(self.image_to_find, img, confidence=self._confidence)
            )
        )

        return bool(self._last_locations)

    def _dump(self, img):
        Detector.counter += 1
        # cv2.imwrite(f'output_{Detector.counter}.png', img)
        return img


class GemsAreAvailable(Detector):
    IMAGE_TO_FIND = 'resources/gem_icon_visible.png'

    _confidence = 0.8

    def _rescale(self, h, w):
        # Top right part of the image
        return 0, h // 6, w - w // 4, 0


class ClickOnGem(Detector):
    IMAGE_TO_FIND = 'resources/gem_found.png'

    def _rescale(self, h, w):
        # Top right part of the image
        return 0, h, w // 2, 0


class CloseGemScreen(Detector):
    IMAGE_TO_FIND = 'resources/close_gem_screen.png'

    def _rescale(self, h, w):
        # Top right part of the image
        return 0, h / 7, 3 * w / 4


class Monitor(Detector):
    IMAGE_TO_FIND = 'resources/monitor_no_thanks.png'

    def _rescale(self, h, w):
        half_of_height = h // 2
        height_of_button = half_of_height + h // 8
        half_of_width = w // 2

        return half_of_height, height_of_button, 0, half_of_width


class GameFinished(Detector):
    IMAGE_TO_FIND = 'resources/game_finished.png'

    def _rescale(self, h, w):
        return h // 2,


class MonsterSetup(Detector):
    IMAGE_TO_FIND = 'resources/monster_setup.png'

    def _rescale(self, h, w):
        return h - h // 8


class SelectNewGame(Detector):
    IMAGE_TO_FIND = 'resources/select_new_game.png'

    def _rescale(self, h, w):
        bottom_of_image = h // 4
        height_of_button = h // 10

        new_width = int(w / 2.5)

        return h - bottom_of_image, h - bottom_of_image + height_of_button, 0, new_width


class Seller(Detector):
    IMAGE_TO_FIND = 'resources/seller_no_thanks.png'

    def _rescale(self, h, w):
        half_of_height = h // 2
        height_of_button = half_of_height + h // 8
        half_of_width = w // 2

        return half_of_height, height_of_button, 0, half_of_width


class SellerOkay(Detector):
    IMAGE_TO_FIND = 'resources/seller_okay.png'

    def _rescale(self, h, w):
        bottom_of_image = h // 2
        height_of_button = h // 8

        return bottom_of_image, bottom_of_image + height_of_button


class Detected(Enum):
    GemsAreAvailable = auto()
    ClickOnGem = auto()
    CloseGemScreen = auto()
    Monitor = auto()
    GameFinished = auto()
    MonsterSetup = auto()
    SelectNewGame = auto()
    Seller = auto()
    SellerOkay = auto()


class NoSceneFound(Exception):
    """No scene could be found."""


class SceneInterpreter:
    def __new__(cls, *args, **kwargs):
        cls.all_detectors: Dict[str, Detector] = {
            name: cls()
            for name, cls in globals().items()
            if isinstance(cls, type) and issubclass(cls, Detector) and cls is not Detector
        }
        # Make sure this one is always evaluated LAST!
        cls.all_detectors.pop('CloseGemScreen', None)
        cls.all_detectors['CloseGemScreen'] = CloseGemScreen()

        return super().__new__(cls)

    def __init__(self, image: np.ndarray):
        self.img = image
        self.last_detector: Optional[Detector] = None

    @property
    def what_is_here(self):
        for detector, obj in self.all_detectors.items():
            if obj.is_present(self.img):
                self.last_detector = obj
                return Detected[detector]

        self.last_detector = None
        raise NoSceneFound

    @property
    def locations(self) -> Generator[Rect, None, None]:
        """
        This returns the average location of the button/stuff you want to find.
        Coordinates are vs the window.

        Returns: tuple(left, top, width, height)
        """
        try:
            scaling_height, scaling_width = self.last_detector._get_scale_slices(*self.img.shape[:2])
            for loc in self.last_detector.last_locations:
                yield Rect(
                    loc.x + scaling_width.start,
                    loc.y + scaling_height.start,
                    loc.w,
                    loc.h,
                )
        except (AttributeError, KeyError):
            return None


if __name__ == '__main__':
    debug = True
    start = time()
    count = 0

    tmp = ClickOnGem()

    for path in Path('../../tests/get_gems_from_achievements').rglob('*.png'):
        if 'debug' in path.name: continue

        print(path, ' --> ', tmp.is_present(path), ' // ', tmp.last_locations)
        count += 1
    #
    # for path in Path('../../tests/seller/').glob('*.png'):
    #     print(path, ' --> ', tmp.is_present(path))
    #     count += 1

    print(f'Time taken: {time() - start:0.2} for {count} entries')
