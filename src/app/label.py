import base64
from io import BytesIO
from math import floor
from pprint import pprint
from typing import Final, Literal, TypedDict, cast, final

import qrcode
from brother_ql import BrotherQLRaster
from brother_ql.backends import BrotherQLBackendGeneric, backend_factory
from brother_ql.brother_ql_create import create_label
from brother_ql.labels import FormFactor, LabelsManager
from brother_ql.labels import Label as LabelType
from brother_ql.models import Model, ModelsManager
from PIL import Image, ImageDraw, ImageFont

from app.fonts import Fonts

from . import backend, config, font, logger
from .halftone import halftone

labels_manager = LabelsManager()

class Label:
    @final
    class Data(TypedDict):
        label_size: str
        orientation: Literal["rotated"] | None
        margin_left: str | int
        margin_right: str | int
        margin_top: str | int
        margin_bottom: str | int
        font_size: str | int
        font_name: str
        font_spacing: float
        qr_text: str
        text: str
        qr_align: Literal["center", "right"]
        halign: Literal["center", "left", "right"]
        valign: Literal["top", "middle", "bottom"]

    data: Final[Data]
    margin_left: Final[int]
    margin_right: Final[int]
    margin_top: Final[int]
    margin_bottom: Final[int]
    label_type: Final[LabelType]
    rotated: Final[bool]
    image: Image.Image
    label: ImageDraw.ImageDraw
    font: ImageFont.FreeTypeFont
    font_path: Fonts.Font
    width: float
    height: float

    def __init__(self, data: Data, file: bool = False):
        """ creates a new label with the given settings """
        self.data = data
        logger.debug(f"Trying to print {data}...")

        label_type = cast(LabelType | None, labels_manager.get(data["label_size"]))
        if label_type is None:
            raise ValueError(
                f"Label with identifier {data['label_size']} could not be found!"
            )
        self.label_type = label_type
        logger.debug(f"Label size: {self.label_type.dots_printable}")
        self.width = label_type.dots_printable[0]
        self.height = label_type.dots_printable[1]

        if data['orientation'] == 'rotated':
            self.rotated = True
        else:
            self.rotated = False

        try:
            self.margin_left = int(self.data["margin_left"])
        except ValueError:
            self.margin_left = config["labels"]["margin"]["left"]
        try:
            self.margin_right = int(self.data["margin_right"])
        except ValueError:
            self.margin_right = config["labels"]["margin"]["right"]
        try:
            self.margin_top = int(self.data["margin_top"])
        except ValueError:
            self.margin_top = config["labels"]["margin"]["top"]
        try:
            self.margin_bottom = int(self.data["margin_bottom"])
        except ValueError:
            self.margin_bottom = config["labels"]["margin"]["bottom"]

        self.image = Image.new("L", (self.width, self.height), 255)

        self.label = ImageDraw.Draw(self.image)
        logger.debug(f"Rotated: {self.rotated}")

        if 'text' in self.data:
            try:
                self.data['font_spacing'] = int(self.data['font_spacing'])
            except ValueError:
                self.data['font_spacing'] = config['font_spacing']
            self.font_path = font.fonts[data['font_name']]
            self.font = ImageFont.truetype(font.fonts[data['font_name']]['path'], int(data['font_size']))
            self.text()
        if 'qr_text' in self.data:
            self.qr()
        if file:
            self.img(file)

    def convert_to_png(self):
        img_buf = BytesIO()
        self.image.save(img_buf, format="PNG")
        img_buf.seek(0)
        return base64.b64encode(img_buf.getbuffer())

    def scale(self, dim: tuple[int, int]):
        img_height, img_width = dim

        # set width and height
        if self.height == 0:
            label_height = dim[0]
        else:
            label_height = self.height
        label_width = self.width

        if self.rotated:
            if img_width > label_height or img_height > label_width:
                ratio = min(label_height / img_width, label_width / img_height)
                x = ratio * img_width
                y = ratio * img_height
            else:
                y = img_width
                x = img_height

        else:
            if img_width > label_width or img_height > label_height:
                ratio = min(label_width / img_width, label_height / img_height)
                x = ratio * img_width
                y = ratio * img_height
            else:
                x = img_width
                y = img_height

        ret = (int(x), int(y))

        logger.debug(f"Scaled image: {ret}")

        return ret

    def img(self, img):
        img = Image.open(img)
        logger.debug('Generating label from image.')
        logger.debug(f"Data: {self.data}")
        logger.debug(f"Image: {img}")
        logger.debug(f"Image size: {img.size}")
        imgsize = self.scale(img.size)
        logger.debug(f"Scaled image size: {imgsize}")

        # resize label
        rot_img = False
        if self.height == 0:
            if self.rotated:
                x = self.width
                y = imgsize[0]
            else:
                y = imgsize[0]
                x = self.width
        else:
            if self.rotated:
                x = self.height
                y = self.width
            else:
                x = self.width
                y = self.height

        self.image = Image.new("L", (floor(x), floor(y)), 255)

        logger.debug(f"Label dimensions: {x}, {y}")
        logger.debug(f"Scaled dimensions: {imgsize}")

        self.label = ImageDraw.Draw(self.image)

        img = halftone(img.resize(imgsize), 8, 1, 45)
        self.image.paste(img, (0, 0))

    def qr(self):
        logger.debug('Generating QR-CODE: {}'.format(self.data['qr_text']))

        # TODO: more options on qr-code (plaintext content, box size, etc)
        if 'error_correction' in self.data:
            error_correction = self.data['error_correction']
        else:
            error_correction = 0

        qr = qrcode.QRCode(version=1,
                           error_correction=error_correction,
                           box_size=10,
                           border=1
                          )

        qr.add_data(self.data['qr_text'])
        qr.make()
        qrimage = qr.make_image(fill_color="black", back_color="white").get_image()
        qrsize = self.scale(qrimage.size)

        logger.debug(f"QR Size: {qrsize}")

        # resize label
        if self.height == 0:
            if self.rotated:
                x = self.width
                y = qrsize[0]
            else:
                y = qrsize[0]
                x = self.width
        else:
            if self.rotated:
                x = self.height
                y = self.width
            else:
                x = self.width
                y = self.height

        self.image = Image.new("L", (floor(x), floor(y)), 255)
        self.label = ImageDraw.Draw(self.image)
        logger.debug(f"Label dimensions: {x}, {y}")
        logger.debug(f"Scaled dimensions: {qrsize}")
        qrimage = qrimage.resize(qrsize)

        pastex = 0
        pastey = 0
        if self.data['qr_align'] == 'center':
            pastex = int((x - qrsize[0]) / 2)
        elif self.data['qr_align'] == 'right':
            pastex = x - qrsize[0]
        self.image.paste(qrimage, (pastex, pastey))
        #self.label.text((0, 0), self.data['qr_text'], 0)

    def text(self):
        bbox = self.label.multiline_textbbox(
            (0, 0), self.data["text"], font=self.font, spacing=self.data["font_spacing"]
        )
        x = bbox[2] - bbox[0]
        y = bbox[3] - bbox[1]
        # resize label
        if self.height == 0:
            if self.rotated:
                self.height = self.width
                self.width = x + self.margin_left + self.margin_right
            else:
                self.height = y + self.margin_top + self.margin_bottom
        elif self.rotated:
            self.height, self.width = self.label_type.dots_printable
        self.image = Image.new("L", (floor(self.width), floor(self.height)), 255)
        self.label = ImageDraw.Draw(self.image)

        # horizontal alignment
        if self.data['halign'] == "center":
            x = int(self.width/2) - int(x / 2)
        elif self.data['halign'] == "left":
            x = self.margin_left
        elif self.data['halign'] == "right":
            x = self.width - (x + self.margin_right)

        # vertical alignment
        if self.data['valign'] == "middle":
            y = int(self.height / 2) - int(y / 2)
        elif self.data['valign'] == "top":
            y = 0 + self.margin_top
        elif self.data['valign'] == "bottom":
            y = self.height - (y + self.margin_bottom)
        self.label.multiline_text(
            (x, y),
            self.data["text"],
            0,
            font=self.font,
            align=self.data["halign"],
            spacing=self.data["font_spacing"],
        )

    def draw(self):
        return self.convert_to_png()

    def prt(self):
        logger.debug(f"Printing {self.label_type}")
        if self.label_type.form_factor == FormFactor.ENDLESS:
            rot = 0 if not self.rotated else 90
        else:
            rot = 'auto'

        model = cast(Model | None, ModelsManager().get(config["printer"]["model"]))
        if model is None:
            raise ValueError(f"Model {config['printer']['model']} is not supported!")

        qlr = BrotherQLRaster(model.identifier)
        if model.cutting:
            logger.debug('Printer is capable of automatic cutting.')
        else:
            logger.debug('Printer is not capable of automatic cutting.')
        create_label(
            qlr,
            self.image,
            self.data["label_size"],
            threshold=30,
            cut=model.cutting,
            rotate=rot,
        )
        try:
            backend_class = cast(
                type[BrotherQLBackendGeneric], backend_factory(backend)["backend_class"]
            )
            be = backend_class(config['printer']['device'])
            pprint(vars(be))
            be.write(qlr.data)
            be.dispose()
            del be
            # TODO better feedback from printer
            return "alert-success", "<b>Success:</b>Label printed"
        except Exception as e:
            logger.warning("unable tp print")
            logger.warning(e, exc_info=True)
            return "danger", "unable to print"

