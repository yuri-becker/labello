import logging
from typing import cast

from brother_ql.labels import LabelsManager
from flask import render_template, request, send_from_directory

from app.config import config
from app.fonts import fonts
from app.label import Label
from app.request import Request

from . import app

logger = logging.getLogger(__name__)
labels_manager = LabelsManager()


@app.route("/")
def root():
    return render_template(
        "main.jinja2",
        website=config.website,
        fonts=fonts.font_names(),
        margins=config.label.margins,
        spacing=config.label.font_spacing,
        labels=labels_manager.elements,
    )


@app.errorhandler(404)
def error_404(e):
    return f'api endpoint "{request.path}" not found', 404


@app.route("/node_modules/<path:filename>", methods=["GET"])
def node_module(filename):
    logger.debug(filename)
    return send_from_directory(app.config["node_path"], filename)


@app.post("/preview")
def preview():
    form = request.form.to_dict()
    prev = Label(cast(Request, form))
    return prev.draw()


@app.route("/preview/image", methods=["POST"])
def preview_image():
    data = cast(Request, request.form.to_dict())
    label = Label(data, cast(bool, request.files["file"]))
    return label.draw()


@app.route("/print", methods=["POST"])
def print():
    try:
        Label(
            cast(Request, request.form.to_dict()), cast(bool, "file" in request.files)
        ).print()
        return "Created", 201
    except Exception:
        logger.exception("")
        return "", 500


@app.route("/print/image", methods=["POST"])
def print_image():
    Label(
        cast(Request, request.form.to_dict()), cast(bool, request.files["file"])
    ).print()
    return "printed"
