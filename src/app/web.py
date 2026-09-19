import logging
from typing import cast

from brother_ql.labels import LabelsManager
from flask import jsonify, render_template, request, send_from_directory

from app.config import config
from app.fonts import fonts
from app.label import Label

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


@app.route("/preview", methods=["POST"])
def preview():
    prev = Label(request.get_json(True))
    return prev.draw()


@app.route("/preview/qrcode", methods=["POST"])
def qrcode_preview():
    qr = Label(request.get_json(True))
    return qr.draw()


@app.route("/preview/image", methods=["POST"])
def image_preview():
    logger.debug(request.files["file"])
    data = cast(Label.Data, request.form.to_dict())
    logger.debug(data)
    img = Label(data, cast(bool, request.files["file"]))
    return img.draw()


@app.route("/print/text", methods=["POST"])
def prt_text():
    prt = Label(request.get_json(True))
    return jsonify(prt.prt())


@app.route("/print/qrcode", methods=["POST"])
def prt_qrcode():
    prt = Label(request.get_json(True))
    prt.prt()
    return "printed"


@app.route("/print/image", methods=["POST"])
def prt_image():
    data = cast(Label.Data, request.form.to_dict())
    img = Label(data, cast(bool, request.files["file"]))
    img.prt()
    return "printed"
