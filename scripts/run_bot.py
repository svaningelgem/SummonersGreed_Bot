import sys

import pywintypes

from summoners_greed_bot import logger
from summoners_greed_bot.play_game import main

try:
    main()
except (pywintypes.error, ValueError) as ex:
    logger.error(f"Got error: {ex}")
    sys.exit(1)
