import os
from typing import Any, Final, ReadOnly, TypedDict

import yaml
from attr import dataclass


class Margins(TypedDict):
    top: ReadOnly[int]
    bottom: ReadOnly[int]
    left: ReadOnly[int]
    right: ReadOnly[int]

@dataclass(frozen=True)
class Label:
    margins: Margins = Margins(top=24, bottom=24, left=24, right=24)
    feed_margin: int = 16
    """Setting to below 15 is not recommended."""
    font_spacing: int = 13

@dataclass(frozen=True)
class Logging:
    level: int = 30
    """10=debug, 20=info, 30=warning, 40=error, 50=critical."""

    def is_debug(self):
        return self.level == 10


@dataclass(frozen=True)
class Printer:
    device: str = "/dev/usb/lp0"
    model: str = "QL-500"


@dataclass(frozen=True)
class Server:
    port: int = 4242
    host: str = "0.0.0.0"


@dataclass(frozen=True)
class Website:
    html_title: str = "labello - label printer"
    title: str = "labello"
    slug: str = "print all your labels"
    bootstrap_local: bool = True
    """Whether labello should serve bootstrap itself (true) or from Bootstrap's CDN (false)."""


class Config:
    fonts: Final[list[str]]
    """Defaults to '/opt/labello/download_font' and '/opt/labello/fonts'"""
    label: Final[Label]
    logging: Final[Logging]
    printer: Final[Printer]
    server: Final[Server]
    website: Final[Website]

    def __init__(self) -> None:
        local_config_path = os.path.dirname(os.path.abspath(__file__)).split(
            os.path.sep
        )[:-1]
        local_config_path.append("config.local.yaml")
        local_config_path = os.path.sep.join(local_config_path)

        dict: dict[str, Any]
        try:
            with open(local_config_path, "r") as fh:
                dict = yaml.safe_load(fh)
        except FileNotFoundError:
            dict = {}

        self.fonts = dict.get(
            "fonts", ["/opt/labello/download_font", "/opt/labello/fonts"]
        )
        self.label = Label(**dict.get("label", {}))
        self.printer = Printer(**dict.get("printer", {}))
        self.logging = Logging(**dict.get("logging", {}))
        self.server = Server(**dict.get("server", {}))
        self.website = Website(**dict.get("website", {}))


config = Config()
