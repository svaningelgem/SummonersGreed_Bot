from pathlib import Path
from time import time

import cv2
from subimage import find_subimages


class DetectGem:
    def __init__(self):
        self.visible = cv2.imread('resources/gem_icon_visible.png', 0)
        self.nope = cv2.imread('resources/gem_icon_not_present.png', 0)

    def is_present(self, img):
        img = cv2.imread(str(img), 0)

        # Top right quadrant
        img = img[:img.shape[0]//2, img.shape[1]//2:]

        return find_subimages(img, self.visible)


class DetectMonitor:
    def __init__(self):
        self.monitors = [
            cv2.imread(str(path), 0)
            for path in Path('resources').glob('monitor*.png')
        ]

    def is_present(self, img):
        img = cv2.imread(str(img), 0)
        # Cut off the right bottom quadrant (speed up processing!)
        img = img[img.shape[0]//2:, img.shape[1]//2:]

        for x in self.monitors:
            res = find_subimages(img, x)
            if res:
                return res

        return None


if __name__ == '__main__':
    start = time()
    count = 0

    tmp = DetectMonitor()

    for path in Path('../../tests/monitor/').glob('*.png'):
        print(path, ' --> ', tmp.is_present(path))
        count += 1

    for path in Path('../../tests/seller/').glob('*.png'):
        print(path, ' --> ', tmp.is_present(path))
        count += 1

    print(f'Time taken: {time() - start:0.2} for {count} entries')
