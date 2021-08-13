from pathlib import Path

import pytest

from summoners_greed_bot.detectors import CloseGemScreen, GameFinished, GemsAreAvailable, Monitor, MonsterSetup, \
    SelectNewGame, Seller


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

        assert checker.is_present(path), f"{path} should be a {search_in_path}!"

    for path in Path('.').rglob('*.png'):
        if path in seen_paths or path.name in ignore:
            continue

        assert not checker.is_present(path), f'{path} should not be classified as a {search_in_path}!'


def test_gems_present():
    checker = GemsAreAvailable()

    assert checker.is_present(Path('is_gem_icon_present/present.png')), 'The gem icon is not present but it should be?'
    assert not checker.is_present(Path('is_gem_icon_present/not_present.png')), 'The gem icon should not be present.'

