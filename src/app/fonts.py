import subprocess
import sys
from typing import TypedDict

from app.config import Config, config
from app.logger import logger


class Font(TypedDict):
    path: str
    styles: list[str]

class Fonts:
    _fonts: dict[str, Font]

    def __init__(self, config: Config):
        self._fonts = {}
        for folder in config.fonts:
            self.add_fonts(folder)
        logger.debug(f"Detected Fonts {self.font_names()}")

    def get_fonts(self, raw: subprocess.CompletedProcess[bytes]):
        """adds the found fonts the the fonts list
        :param raw: command to be run to get the raw font list from the system
        :return: true if fonts were added false if not
        """

        if raw.returncode != 0:
            return {"error": "an error occurred while processing the fonts"}

        for line in raw.stdout.decode("utf-8").split("\n"):
            font = line.split(":")
            if len(font) < 3:
                continue
            # ignore non true type fonts
            if ".ttf" in font[0] or ".otf" in font[0]:
                fontname = font[1].replace("\\", "")
                if "," in fontname:
                    fontname = fontname.split()[0]
                if "Regular" or "Medium" in font[2][6:].strip().split(","):
                    self._fonts[fontname.strip()] = Font(
                        path=font[0].strip(),
                        styles=font[2][6:].strip().split(","),
                    )
            else:
                pass

    def global_fonts(self):
        """Get a list of all fonts that are available to the user who runs this
        :return: raw output of the command fc-list
        """
        command = ["fc-list"]
        try:
            raw = subprocess.run(command, stdout=subprocess.PIPE)
        except FileNotFoundError:
            logger.fatal("fc-list not found")
            sys.exit(2)

        self.get_fonts(raw)

    def add_fonts(self, folder):
        """Get a list of all fonts that are available to the user who runs this
        :return: raw output of the command fc-list
        """
        cmd = ["fc-scan", "--format", "%{file}:%{family}:style=%{style}\n", folder]
        try:
            raw = subprocess.run(cmd, stdout=subprocess.PIPE)
        except FileNotFoundError:
            logger.fatal("fc-list not found")
            sys.exit(2)

        self.get_fonts(raw)

    def font_names(self):
        return sorted(self._fonts, key=str.lower)

    def font(self, name: str):
        return self._fonts[name]

    def fonts_available(self):
        if len(self._fonts) == 0:
            return False
        else:
            return len(self._fonts)


fonts = Fonts(config)
