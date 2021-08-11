from pathlib import Path
from time import time

import cv2

counter = 0
def find_match(small_image, large_image):
    global counter

    method = cv2.TM_SQDIFF_NORMED

    # Read the images from the file
    small_img = cv2.imread(str(small_image))
    large_img = cv2.imread(str(large_image))
    large_img = large_img[large_img.shape[0]//2:, large_img.shape[1]//2:]

    result = cv2.matchTemplate(small_img, large_img, method)

    # We want the minimum squared difference
    mn,_,mnLoc,_ = cv2.minMaxLoc(result)
    if mn >= 0.5:
        return None

    print(f'output{counter}.png', small_image, large_image, mn, mnLoc, sep="\t")
    # Draw the rectangle:
    # Extract the coordinates of our best match
    MPx,MPy = mnLoc

    # Step 2: Get the size of the template. This is the same size as the match.
    trows,tcols = small_img.shape[:2]

    # Step 3: Draw the rectangle on large_image
    cv2.rectangle(large_img, (MPx,MPy),(MPx+tcols,MPy+trows),(0,0,255),2)

    # Display the original image with the rectangle around the match.
    cv2.imwrite(f'output{counter}.png',large_img)
    counter += 1


if __name__ == '__main__':
    start = time()
    count = 0

    for large in Path('../../tests/').rglob('*.png'):
        for small in Path('resources').glob('monitor*.png'):
            find_match(small, large)
        count += 1

    print(f'Time taken: {time() - start:0.2} for {count} entries')
