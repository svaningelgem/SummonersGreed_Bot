from abc import ABC
from enum import Enum, auto
from pathlib import Path
from time import time
from typing import Dict, Optional, Tuple

import cv2
import numpy as np
from subimage import find_subimages

from summoners_greed_bot.temp import _locateAll_opencv


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

    def __init__(self):
        self.image_to_find = _get_image(self.IMAGE_TO_FIND)
        self._last_width_height = None
        self._last_location = None

    @property
    def last_width_height(self):
        return self._last_width_height

    @property
    def last_location(self):
        return self._last_location

    def _rescale(self, h, w):
        return 0, h, 0, w

    def _get_scale_slices(self, h, w):
        tpl = self._rescale(h, w)

        if not isinstance(tpl, tuple):
            tpl = (tpl, h, 0, w)
        elif len(tpl) == 1:
            tpl = (tpl[0], h, 0, w)
        elif len(tpl) == 2:
            tpl = (*tpl, 0, w)
        elif len(tpl) == 3:
            tpl = (*tpl, w)

        height_slice = slice(tpl[0], tpl[1])
        width_slice = slice(tpl[2], tpl[3])

        return height_slice, width_slice

    def _get_scaled_image(self, img):
        img = _get_image(img)

        self._last_width_height = img.shape

        h, w = self._last_width_height
        height_slice, width_slice = self._get_scale_slices(h, w)

        img = img[height_slice, width_slice]

        self._dump(img)

        return img

    def is_present(self, inside_this_image):
        img = self._get_scaled_image(inside_this_image)

        self._last_location = find_subimages(img, self.image_to_find)
        if not self._last_location:
            self._last_location = list(_locateAll_opencv(self.image_to_find, img, confidence=0.8))

        return self.last_location

    def _dump(self, img):
        Detector.counter += 1
        # cv2.imwrite(f'output_{Detector.counter}.png', img)
        return img


# class Gem(Detector):
#     IMAGE_TO_FIND = 'resources/gem_icon_visible.png'
#
#     def _rescale(self, h, w):
#         # Top right part of the image
#         return 0, h // 6, w - w // 4, 0


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
    Gem = auto()
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
    def location(self) -> Tuple[int, int, int, int]:
        """
        This returns the average location of the button/stuff you want to find.
        Coordinates are vs the window.

        Returns: tuple(left, top, width, height)
        """
        try:
            scaling_height, scaling_width = self.last_detector._get_scale_slices(*self.img.shape[:2])
            l, t, b, r = [
                int(sum(x) / len(x))
                for x in zip(*self.last_detector.last_location)
            ]

            return (
                l + scaling_width.start,
                t + scaling_height.start,
                b - l,
                r - t,
            )
        except (AttributeError, KeyError):
            return None


if __name__ == '__main__':
    start = time()
    count = 0

    tmp = Seller()

    for path in Path('../../tests/seller').rglob('out*.png'):
        if 'debug' in path.name: continue

        print(path, ' --> ', tmp.is_present(path))
        count += 1
    #
    # for path in Path('../../tests/seller/').glob('*.png'):
    #     print(path, ' --> ', tmp.is_present(path))
    #     count += 1

    print(f'Time taken: {time() - start:0.2} for {count} entries')
