from dataclasses import dataclass


@dataclass
class CommentEntry:
    sheet_name: str
    header_value: str
    cell_value: str
    comment: str
    cell_address: str
    bg_color: str | None
    row: int
    column: int
    puic: str
    path: str
    status: str
    geometry_status: str | None = None
