import os
from typing import Final, NotRequired, ReadOnly, TypedDict

import yaml


class ServerDict(TypedDict):
    port: ReadOnly[NotRequired[int]]
    host: ReadOnly[NotRequired[str]]


class Server:
    dict: Final[ServerDict]

    def __init__(self, dict: ServerDict) -> None:
        self.dict = dict

    @property
    def port(self):
        return self.dict.get("port", 5000)

    @property
    def host(self):
        return self.dict.get("host", "::1")


class LoggingDict(TypedDict):
    level: ReadOnly[NotRequired[int]]


class Logging:
    dict: Final[LoggingDict]

    def __init__(self, dict: LoggingDict) -> None:
        self.dict = dict

    @property
    def level(self) -> int:
        return self.dict.get("level", 20)


class Website(TypedDict):
    html_title: ReadOnly[str]
    title: ReadOnly[str]
    slug: ReadOnly[str]
    bootstrap_local: ReadOnly[NotRequired[bool]]


class Margins(TypedDict):
    top: ReadOnly[int]
    bottom: ReadOnly[int]
    left: ReadOnly[int]
    right: ReadOnly[int]


class LabelDict(TypedDict):
    margins: ReadOnly[NotRequired[Margins]]
    feed_margin: ReadOnly[int]
    font_spacing: ReadOnly[NotRequired[int]]


class Label:
    dict: LabelDict

    def __init__(self, dict: LabelDict) -> None:
        self.dict = dict

    @property
    def margins(self):
        return self.dict.get("margins", Margins(top=24, bottom=24, left=24, right=24))

    @property
    def feed_margin(self):
        return self.dict["feed_margin"]

    @property
    def font_spacing(self):
        return self.dict.get("font_spacing", 13)


class Printer(TypedDict):
    device: ReadOnly[str]
    model: ReadOnly[str]


class ConfigDict(TypedDict):
    server: NotRequired[ReadOnly[ServerDict]]
    logging: ReadOnly[LoggingDict]
    website: ReadOnly[Website]
    label: ReadOnly[LabelDict]
    printer: ReadOnly[Printer]
    fonts: ReadOnly[list[str]]


class Config:
    dict: Final[ConfigDict]

    def __init__(self) -> None:
        local_config_path = os.path.dirname(os.path.abspath(__file__)).split(
            os.path.sep
        )[:-1]
        local_config_path.append("config.local.yaml")
        local_config_path = os.path.sep.join(local_config_path)
        config_path = os.path.dirname(os.path.abspath(__file__)).split(os.path.sep)[:-1]
        config_path.append("config.yaml")
        config_path = os.path.sep.join(config_path)
        try:
            with open(local_config_path, "r") as fh:
                self.dict = yaml.safe_load(fh)
        except FileNotFoundError:
            with open(config_path, "r") as fh:
                self.dict = yaml.safe_load(fh)

    @property
    def fonts(self):
        return self.dict["fonts"]

    @property
    def logging(self) -> Logging:
        return Logging(self.dict["logging"])

    @property
    def label(self) -> Label:
        return Label(self.dict["label"])

    @property
    def printer(self) -> Printer:
        return self.dict["printer"]

    @property
    def server(self) -> Server:
        return Server(self.dict.get("server", ServerDict()))

    @property
    def website(self) -> Website:
        return self.dict["website"]


config = Config()
