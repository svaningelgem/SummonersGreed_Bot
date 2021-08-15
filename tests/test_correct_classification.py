from pathlib import Path

import pytest

from summoners_greed_bot import logger
from summoners_greed_bot.detectors import ClickOnGem, CloseGemScreen, GameFinished, Monitor, \
    MonsterSetup, SelectNewGame, Seller  # , GemsAreAvailable

logger.setLevel('DEBUG')


@pytest.mark.parametrize(
    'cls, search_in_path, ignore',
    [
        (Monitor, 'monitor', []),
        (MonsterSetup, 'monster_setup', []),
        (GameFinished, 'round_finished', []),
        (SelectNewGame, 'select_map', []),
        (Seller, 'seller', ['final_okay.png']),
        (CloseGemScreen, 'get_gems_from_achievements', ['BlueStacks-2021-08-11 12_02_45.png'])
    ]
)
def test_presence_or_not(cls, search_in_path, ignore):
    seen_paths = []
    checker = cls()
    for path in Path(search_in_path).glob('*.png'):
        seen_paths.append(path)
        if path.name in ignore:
            continue

        logger.debug("Checking '%s'", path)

        assert checker.is_present(path), f"{path} should be a {search_in_path}!"

    for path in Path('.').rglob('*.png'):
        if path in seen_paths or path.name in ignore or path.name.startswith('debug_'):
            continue

        logger.debug("Checking '%s'", path)

        assert not checker.is_present(path), f'{path} should not be classified as a {search_in_path}!'


def test_gems_present():
    checker = GemsAreAvailable()

    assert checker.is_present(Path('is_gem_icon_present/present.png')), 'The gem icon is not present but it should be?'
    assert not checker.is_present(Path('is_gem_icon_present/not_present.png')), 'The gem icon should not be present.'


@pytest.mark.parametrize('filename, amount', {
    ('BlueStacks-2021-08-13 21_00_58', 1),
    ('BlueStacks-2021-08-13 21_01_15', 2),
    ('BlueStacks-2021-08-13 21_01_32', 2),
    ('BlueStacks-2021-08-13 21_25_56', 2),
    ('rewards_available__just_1', 1),
    ('rewards_available__multiple', 2),
    ('screenshot', 1),
})
def test_click_on_gems(filename, amount):
    checker = ClickOnGem()
    path = Path(f'get_gems_from_achievements/{filename}.png')

    if amount > 0:
        assert checker.is_present(path), f'No gems present in {path}.'
    else:
        assert not checker.is_present(path), f'No gems should be present in {path}.'

    locations = list(checker.last_locations)
    assert len(locations) == amount, f'Should have {amount} locations, but got {len(locations)}: {locations}.'
