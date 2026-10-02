from typing import Literal, ReadOnly, TypedDict


class Request(TypedDict):
    label_size: ReadOnly[str]
    orientation: ReadOnly[Literal["rotated"] | None]
    margin_left: ReadOnly[str | int]
    margin_right: ReadOnly[str | int]
    margin_top: ReadOnly[str | int]
    margin_bottom: ReadOnly[str | int]
    font_size: ReadOnly[str | int]
    font_name: ReadOnly[str]
    font_spacing: ReadOnly[float]
    qr_text: ReadOnly[str]
    text: ReadOnly[str]
    qr_align: ReadOnly[Literal["center", "right"]]
    halign: ReadOnly[Literal["center", "left", "right"]]
    valign: ReadOnly[Literal["top", "middle", "bottom"]]
