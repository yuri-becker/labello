import os.path
import sys

from brother_ql.backends import guess_backend
from flask import Flask

from labello.config import config
from labello.logger import logger

# initialize flask app
app = Flask(__name__)
app.config.update(
    DEBUG=config.logging.level == 10,
    DEFAULT_PARSERS=[
        "flask.ext.api.parsers.URLEncodedParser",
        "flask.ext.api.parsers.MultiPartParser",
    ],
)

node_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "node_modules")
app.config["node_path"] = node_path

try:
    backend = guess_backend(config.printer.device)
    logger.info(f"Using Backend {backend}")
except ValueError:
    logger.error("Unable to select the proper backend. Check your config")
    sys.exit(20)

from . import web  # pyright: ignore[reportUnusedImport]  # noqa: F401
