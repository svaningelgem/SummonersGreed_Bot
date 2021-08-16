import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(filename='summoners_greed_bot.log', mode='a'),
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger('summoners_greed_bot')
