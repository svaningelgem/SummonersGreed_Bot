from pathlib import Path

from subimage import find_subimages

for large_image in [
    Path('../../tests/is_gem_icon_present/not_present.png'),
    Path('../../tests/is_gem_icon_present/present.png'),
]:
    print(f'### {large_image.name}')

    for smaller_image in [
        Path('resources/gem_icon_visible.png'),
        Path('resources/gem_icon_not_present.png'),
    ]:
        try:
            print(f'    #### {smaller_image.name}')

            res = find_subimages(large_image, smaller_image)
            print(f'        {res}')

        except Exception as ex:
            print(f'            !!! {ex}')
