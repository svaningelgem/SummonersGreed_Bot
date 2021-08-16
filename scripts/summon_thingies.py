from time import sleep

from summoners_greed_bot.find_window import BlueStacksWindow

bluestacks = BlueStacksWindow()


SUMMON_STONES_AVAILABLE = 314
# SUMMON_STONES_AVAILABLE = int(input('Please enter how many summon stones you have: '))
SLEEP_TIME = 0.15

# Click summon button
bluestacks.click(44, 213)

for _ in range(1, SUMMON_STONES_AVAILABLE, 10):
    # Click 10-cost button
    bluestacks.click(102, 1049)
    sleep(SLEEP_TIME)
    # Click somewhere else...
    bluestacks.click(102, 1049)
    sleep(SLEEP_TIME)
    # Click "Okay" button
    bluestacks.click(294, 684)
    sleep(SLEEP_TIME)
