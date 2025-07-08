from enum import Enum

from src.imxTools.utils.columnEnum import ColumnEnum


class CommentColumns(ColumnEnum):
    object_path = "Full object path in IMX structure"
    object_puic = "PUIC (unique identifier) of the object"
    change_status = "Change status of the object"
    geometry_status = "Geometry change status"
    comment_type = (
        "Will be determinate by cell color, clickable Excel hyperlink to the comment"
    )
    header_value = "The value in the header of the column"
    value = "Current value in cell"
    comment = "Comment content"
    cell_bg_color = "Cell background color"
    comment_sheet_name = "Name of sheet with the comment"
    comment_row = "Row number of the comment"
    comment_column = "Column number of the comment"


class CommentReplacementSummaryColumns(ColumnEnum):
    status = "Placement status (Placed, Skipped, Failed)"
    sheet = "Sheet name"
    imx_path = "IMX path (header)"
    puic = "PUIC value"
    value = "Value in the cell"
    comment = "Comment content"
    reason = "Reason for placement status"


class CommentReplacementStatusEnum(str, Enum):
    PLACED = "Placed"
    SKIPPED = "Skipped"
    FAILED = "Failed"
