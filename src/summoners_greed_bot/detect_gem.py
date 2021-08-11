from abc import ABC
from pathlib import Path
from time import time

import cv2
from subimage import find_subimages


class Detector(ABC):
    IMAGE_TO_FIND = None
    counter = 0

    def __init__(self):
        self.image_to_find = cv2.imread(str(self.IMAGE_TO_FIND), cv2.IMREAD_GRAYSCALE)
        self._last_width_height = None

    @property
    def last_width_height(self):
        return self._last_width_height

    def _rescale(self, h, w):
        return 0, h, 0, w

    def is_present(self, inside_this_image):
        img = cv2.imread(str(inside_this_image), cv2.IMREAD_GRAYSCALE)

        self._last_width_height = img.shape

        h, w = self._last_width_height
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

        img = img[height_slice, width_slice]

        self._dump(img)

        return find_subimages(img, self.image_to_find)

    def _dump(self, img):
        Detector.counter += 1
        cv2.imwrite(f'output_{Detector.counter}.png', img)
        return img


class DetectGem(Detector):
    IMAGE_TO_FIND = 'resources/gem_icon_visible.png'

    def _rescale(self, h, w):
        # Top right part of the image
        return 0, h // 6, w - w // 4, 0


class DetectMonitor(Detector):
    IMAGE_TO_FIND = 'resources/monitor_no_thanks.png'

    def _rescale(self, h, w):
        half_of_height = h // 2
        height_of_button = half_of_height + h // 8
        half_of_width = w // 2

        return half_of_height, height_of_button, 0, half_of_width


class DetectGameFinished(Detector):
    IMAGE_TO_FIND = 'resources/game_finished.png'

    def _rescale(self, h, w):
        return h // 2,


class DetectMonsterSetup(Detector):
    IMAGE_TO_FIND = 'resources/monster_setup.png'

    def _rescale(self, h, w):
        return h - h // 8


class DetectSelectNewGame(Detector):
    IMAGE_TO_FIND = 'resources/select_new_game.png'

    def _rescale(self, h, w):
        bottom_of_image = h // 4
        height_of_button = h // 10

        new_width = int(w / 2.5)

        return h - bottom_of_image, h - bottom_of_image + height_of_button, 0, new_width


class DetectSeller(Detector):
    IMAGE_TO_FIND = 'resources/seller_no_thanks.png'

    def _rescale(self, h, w):
        half_of_height = h // 2
        height_of_button = half_of_height + h // 8
        half_of_width = w // 2

        return half_of_height, height_of_button, 0, half_of_width


class DetectSellerOkay(Detector):
    IMAGE_TO_FIND = 'resources/seller_okay.png'

    def _rescale(self, h, w):
        bottom_of_image = h // 2
        height_of_button = h // 8

        return bottom_of_image, bottom_of_image + height_of_button


if __name__ == '__main__':
    start = time()
    count = 0

    tmp = DetectSellerOkay()

    for path in Path('../../tests/').rglob('*.png'):
        if 'debug' in path.name: continue

        print(path, ' --> ', tmp.is_present(path))
        count += 1
    #
    # for path in Path('../../tests/seller/').glob('*.png'):
    #     print(path, ' --> ', tmp.is_present(path))
    #     count += 1

    print(f'Time taken: {time() - start:0.2} for {count} entries')
