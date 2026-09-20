import os
from typing import Final, NotRequired, ReadOnly, TypedDict

import yaml


class Margins(TypedDict):
    top: ReadOnly[int]
    bottom: ReadOnly[int]
    left: ReadOnly[int]
    right: ReadOnly[int]


class LabelDict(TypedDict):
    margins: ReadOnly[NotRequired[Margins]]
    """Defaults to 24 in all dimensions."""
    feed_margin: ReadOnly[NotRequired[int]]
    """Defaults to 16. Setting to below 15 is not recommended."""
    font_spacing: ReadOnly[NotRequired[int]]
    """Defaults to 13."""


class LoggingDict(TypedDict):
    level: ReadOnly[NotRequired[int]]
    """10=debug, 20=info, 30=warning, 40=error, 50=critical. Defaults to 30"""


class PrinterDict(TypedDict):
    device: ReadOnly[str]
    model: ReadOnly[str]


class ServerDict(TypedDict):
    port: ReadOnly[NotRequired[int]]
    """Defaults to 4242"""
    host: ReadOnly[NotRequired[str]]
    """Defaults to 0.0.0.0"""


class WebsiteDict(TypedDict):
    html_title: ReadOnly[NotRequired[str]]
    """Defaults to 'labello - label printer'"""
    title: ReadOnly[NotRequired[str]]
    """Defaults to labello"""
    slug: ReadOnly[NotRequired[str]]
    """Defaults to 'print all your labels'"""
    bootstrap_local: ReadOnly[NotRequired[bool]]
    """Whether labello should serve bootstrap itself (true) or from Bootstrap's CDN (false). Defaults to true."""


class ConfigDict(TypedDict):
    fonts: ReadOnly[NotRequired[list[str]]]
    """Defaults to '/opt/labello/download_font' and '/opt/labello/fonts'"""
    label: ReadOnly[NotRequired[LabelDict]]
    logging: ReadOnly[NotRequired[LoggingDict]]
    printer: ReadOnly[NotRequired[PrinterDict]]
    """Defaults to a QL-500 on /dev/usb/lp0"""
    server: ReadOnly[NotRequired[ServerDict]]
    website: ReadOnly[NotRequired[WebsiteDict]]


class Label:
    dict: LabelDict

    def __init__(self, dict: LabelDict) -> None:
        self.dict = dict

    @property
    def margins(self):
        return self.dict.get("margins", Margins(top=24, bottom=24, left=24, right=24))

    @property
    def feed_margin(self):
        return self.dict.get("feed_margin", 16)

    @property
    def font_spacing(self):
        return self.dict.get("font_spacing", 13)


class Logging:
    dict: Final[LoggingDict]

    def __init__(self, dict: LoggingDict) -> None:
        self.dict = dict

    @property
    def level(self) -> int:
        return self.dict.get("level", 30)

    def is_debug(self):
        return self.level == 10


class Server:
    dict: Final[ServerDict]

    def __init__(self, dict: ServerDict) -> None:
        self.dict = dict

    @property
    def port(self):
        return self.dict.get("port", 4242)

    @property
    def host(self):
        return self.dict.get("host", "0.0.0.0")


class Website:
    dict: Final[WebsiteDict]

    def __init__(self, dict: WebsiteDict) -> None:
        self.dict = dict

    @property
    def html_title(self):
        return self.dict.get("html_title", "labello - label printer")

    @property
    def title(self):
        return self.dict.get("title", "labello")

    @property
    def slug(self):
        return self.dict.get("slug", "print all your labels")

    @property
    def bootstrap_local(self):
        return self.dict.get("bootstrap_local", True)


class Config:
    fonts: Final[list[str]]
    label: Final[Label]
    logging: Final[Logging]
    printer: Final[PrinterDict]
    server: Final[Server]
    website: Final[Website]

    def __init__(self) -> None:
        local_config_path = os.path.dirname(os.path.abspath(__file__)).split(
            os.path.sep
        )[:-1]
        local_config_path.append("config.local.yaml")
        local_config_path = os.path.sep.join(local_config_path)

        dict: ConfigDict
        try:
            with open(local_config_path, "r") as fh:
                dict = yaml.safe_load(fh)
        except FileNotFoundError:
            dict = ConfigDict()

        self.fonts = dict.get(
            "fonts", ["/opt/labello/download_font", "/opt/labello/fonts"]
        )
        self.label = Label(dict.get("label", LabelDict()))
        self.printer = dict.get(
            "printer", PrinterDict(device="/dev/usb/lp0", model="QL-500")
        )
        self.logging = Logging(dict.get("logging", LoggingDict()))
        self.server = Server(dict.get("server", ServerDict()))
        self.website = Website(dict.get("website", WebsiteDict()))


config = Config()
