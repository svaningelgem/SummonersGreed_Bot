from pathlib import Path

import pytest

from summoners_greed_bot.detectors import GameFinished, Monitor, MonsterSetup, SelectNewGame, Seller


@pytest.mark.parametrize(
    'cls, search_in_path, ignore',
    [
        (Monitor, 'monitor', []),
        (MonsterSetup, 'monster_setup', []),
        (GameFinished, 'round_finished', []),
        (SelectNewGame, 'select_map', []),
        (Seller, 'seller', ['final_okay.png']),
    ]
)
def test_monitor(cls, search_in_path, ignore):
    seen_paths = []
    checker = cls()
    for path in Path(search_in_path).glob('*.png'):
        seen_paths.append(path)
        if path.name in ignore:
            continue

        assert checker.is_present(path), f"{path} should be a {search_in_path}!"

    for path in Path('.').rglob('*.png'):
        if path in seen_paths:
            continue

        assert not checker.is_present(path), f'{path} should not be classified as a {search_in_path}!'
