import cv2
import numpy

from summoners_greed_bot import logger


def _locateAll_opencv(needleImage, haystackImage, confidence=0.999):
    confidence = float(confidence)

    needleHeight, needleWidth = needleImage.shape[:2]

    if haystackImage.shape[0] < needleImage.shape[0] or haystackImage.shape[1] < needleImage.shape[1]:
        # avoid semi-cryptic OpenCV error below if bad size
        logger.debug(f'Wrong size (haystack %s has smaller dimensions than needle %s', haystackImage.shape, needleImage.shape)
        return

    # get all matches at once, credit: https://stackoverflow.com/questions/7670112/finding-a-subimage-inside-a-numpy-image/9253805#9253805
    result = cv2.matchTemplate(haystackImage, needleImage, cv2.TM_CCOEFF_NORMED)
    logger.debug('Highest confidence: %s', result.max())
    match_indices = numpy.arange(result.size)[(result > confidence).flatten()]
    matches = numpy.unravel_index(match_indices, result.shape)

    if len(matches[0]) == 0:
        logger.debug('No matches found.')
        return

    # use a generator for API consistency:
    matchx = matches[1]
    matchy = matches[0]
    for x, y in zip(matchx, matchy):
        yield (x, y, needleWidth, needleHeight)


if __name__ == '__main__':
    for x in _locateAll_opencv(
        cv2.imread('resources/seller_no_thanks.png', cv2.IMREAD_GRAYSCALE),
        cv2.imread('output_1.png', cv2.IMREAD_GRAYSCALE),
        confidence=0.86
    ):
        print(x)
