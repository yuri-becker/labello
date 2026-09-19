import os
from typing import TypedDict

import yaml


class Server(TypedDict):
    port: int
    host: str


class Logging(TypedDict):
    level: int


class Website(TypedDict):
    html_title: str
    title: str
    slug: str
    bootstrap_local: bool


class Margins(TypedDict):
    top: int
    bottom: int
    left: int
    right: int


class Label(TypedDict):
    margins: Margins
    feed_margin: int
    font_spacing: int


class Printer(TypedDict):
    device: str
    model: str


class Config(TypedDict):
    server: Server
    logging: Logging
    website: Website
    label: Label
    printer: Printer
    fonts: list[str]


def load_config() -> Config:
    local_config_path = os.path.dirname(os.path.abspath(__file__)).split(os.path.sep)[
        :-1
    ]
    local_config_path.append("config.local.yaml")
    local_config_path = os.path.sep.join(local_config_path)
    config_path = os.path.dirname(os.path.abspath(__file__)).split(os.path.sep)[:-1]
    config_path.append("config.yaml")
    config_path = os.path.sep.join(config_path)

    try:
        with open(local_config_path, "r") as fh:
            return yaml.safe_load(fh)

    except FileNotFoundError:
        with open(config_path, "r") as fh:
            return yaml.safe_load(fh)
