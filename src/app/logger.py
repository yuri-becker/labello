import logging

from app.config import config

logger = logging.getLogger("labello")
logger.setLevel(config.logging.level)
_ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_ch.setFormatter(formatter)
logger.addHandler(_ch)
