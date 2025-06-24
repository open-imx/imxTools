import re
import uuid
from pathlib import Path

import pandas as pd

from src.imxTools.revision.revision_enums import (
    RevisionColumns,
    RevisionOperationValues,
)
from src.imxTools.utils.exceptions import ErrorList


def validate_process_input(
    imx_input: Path, excel_input: Path, out_path: Path
) -> tuple[Path, Path]:
    input_errors = []

    if not imx_input.exists():
        input_errors.append(f"❌ imx_input does not exist: {imx_input}")
    elif imx_input.suffix.lower() != ".xml":
        input_errors.append(f"❌ imx_input is not an xml file: {imx_input}")

    if not excel_input.exists():
        input_errors.append(f"❌ excel_input does not exist: {excel_input}")
    elif excel_input.suffix.lower() not in [".xlsx", ".xlsm"]:
        input_errors.append(f"❌ excel_input is not a valid Excel file: {excel_input}")

    imx_output = out_path / f"{imx_input.stem}-processed{imx_input.suffix}"
    excel_output = out_path / f"{excel_input.stem}-processed{excel_input.suffix}"

    if imx_output.exists():
        input_errors.append(f"❌ imx_output already exists: {imx_output}")
    if excel_output.exists():
        input_errors.append(f"❌ excel_output already exists: {excel_output}")

    if input_errors:
        raise ErrorList(input_errors)

    return imx_output, excel_output


GML_COORD_REGEX_POINT_AND_LINE = re.compile(
    r"^"
    r"-?\d+(?:\.\d+)?,-?\d+(?:\.\d+)?(?:,-?\d+(?:\.\d+)?)?"  # First point
    r"(?: -?\d+(?:\.\d+)?,-?\d+(?:\.\d+)?(?:,-?\d+(?:\.\d+)?)?)*"  # More points (exactly one space)
    r"$"
)


def validate_gml_coordinates(coord_str: str) -> bool:
    """
    Validates a GML coordinate string as either a 2D or 3D Point or LineString.
    Enforces:
    - No leading or trailing spaces
    - No spaces around commas
    - Each coordinate is x,y or x,y,z
    - All coordinate tuples must have the same dimensionality
    """
    if not coord_str:
        return False

    if not GML_COORD_REGEX_POINT_AND_LINE.fullmatch(coord_str):
        return False

    # Check dimensional consistency
    tuples = coord_str.split(" ")
    dims = None
    for t in tuples:
        parts = t.split(",")
        if dims is None:
            dims = len(parts)
            if dims not in (2, 3):
                return False
        elif len(parts) != dims:
            return False

    return True


def validate_ref_list(refs_str: str) -> bool:
    if not refs_str.strip():
        return False

    refs = refs_str.strip().split()
    for ref in refs:
        try:
            val = uuid.UUID(ref, version=4)
            if str(val) != ref:
                return False  # string must match exactly
        except ValueError:
            return False
    return True


def validate_input_excel_content(df: pd.DataFrame):
    errors: list[str] = []

    df["unique_key"] = (
        df[RevisionColumns.object_puic.name]
        + "_"
        + df[RevisionColumns.attribute_or_element.name]
    )
    df_filtered = df[
        df[RevisionColumns.attribute_or_element.name].notna()
        & (df[RevisionColumns.attribute_or_element.name] != "")
        & (
            df[RevisionColumns.operation.name]
            != RevisionOperationValues.AddElementUnder.name
        )
    ]

    df_filtered.loc[:, "unique_key"] = (
        df_filtered[RevisionColumns.object_puic.name]
        + "_"
        + df_filtered[RevisionColumns.attribute_or_element.name]
    )

    # duplicates = df_filtered[
    #     df_filtered["unique_key"].duplicated(keep=False)
    # ].sort_values(by=RevisionColumns.object_puic.name)
    #
    # if not duplicates.empty:
    #     for idx, row in duplicates.iterrows():
    #         errors.append(
    #             f"Row {idx}: Duplicate unique_key '{row[RevisionColumns.attribute_or_element.name]}' for object_puic '{row[RevisionColumns.object_puic.name]}'"
    #         )

    mask_coords = df[RevisionColumns.attribute_or_element.name].str.endswith(
        (
            "gml:LineString.gml:coordinates",
            "LineString.coordinates",
            "gml:Point.gml:coordinates",
            "Point.coordinates",
        )
    )
    for idx, row in df[mask_coords].iterrows():
        coord_str = row[RevisionColumns.value_new.name]
        if coord_str == "":
            pass
        elif not validate_gml_coordinates(f"{coord_str}"):
            errors.append(
                f"Row {idx}: Invalid GML coordinates for '{row[RevisionColumns.attribute_or_element.name]}': “{coord_str}”"
            )

    mask_refs = df[RevisionColumns.attribute_or_element.name].str.endswith("Refs")
    for idx, row in df[mask_refs].iterrows():
        refs_str = row[RevisionColumns.value_new.name]
        if not validate_ref_list(f"{refs_str}"):
            errors.append(
                f"Row {idx}: Invalid UUID refs for '{row[RevisionColumns.attribute_or_element.name]}': “{refs_str}”"
            )

    if errors:
        raise ErrorList(errors)

    return True
