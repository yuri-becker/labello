import os.path
import sys

from brother_ql.backends import guess_backend
from flask import Flask
from flask_bootstrap import Bootstrap

from app.config import config
from app.logger import logger

# initialize flask app
app = Flask(__name__)
app.config.update(
    DEBUG=config.logging.level == 10,
    BOOTSTRAP_SERVE_LOCAL=config.website.get("bootstrap_local", True),
    DEFAULT_PARSERS=[
        "flask.ext.api.parsers.JSONParser",
        "flask.ext.api.parsers.URLEncodedParser",
        "flask.ext.api.parsers.MultiPartParser",
    ],
)

node_path = os.path.dirname(os.path.abspath(__file__)).split(os.path.sep)[:-1]
node_path.append("node_modules")
app.config["node_path"] = os.path.sep.join(node_path)

# initialize bootstrap
bootstrap = Bootstrap(app)

# setting up printer
try:
    backend = guess_backend(config.printer["device"])
    logger.info(f"Using Backend {backend}")
except ValueError:
    logger.error("Unable to select the proper backend. Check your config")
    sys.exit(20)

from . import web  # pyright: ignore[reportUnusedImport]  # noqa: F401
