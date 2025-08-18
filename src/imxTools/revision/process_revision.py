import os
import sys
from collections.abc import Hashable
from pathlib import Path
from typing import Any

import pandas as pd
import xmlschema
from lxml import etree
from lxml.etree import _Element

from src.imxTools.revision.imx_modifier import (
    set_metadata,
    set_attribute_or_element_by_path,
    delete_attribute_if_matching,
    delete_element,
    create_element_under,
    delete_element_that_matches,
)
from src.imxTools.revision.input_validation import (
    validate_process_input,
    validate_input_excel_content,
)
from src.imxTools.revision.revision_enums import (
    RevisionColumns,
    RevisionOperationValues,
)
from src.imxTools.settings import config
from src.imxTools.utils.custom_logger import logger
from src.imxTools.utils.exceptions import ErrorList

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

IMX_XSD_PATHS = {
    "1.2.4": "data/xsd-1.2.4/IMSpoor-1.2.4-Communication.xsd",
    "12.0.0": "data/xsd-12.0.0/IMSpoor-SignalingDesign.xsd",
}
XML_NS = "{http://www.prorail.nl/IMSpoor}"
PuicIndex = dict[str | None, _Element]


def _load_xsd(version: str) -> xmlschema.XMLSchema:
    try:
        xsd_file = config.ROOT_PATH / IMX_XSD_PATHS[version]
    except KeyError:
        raise NotImplementedError(f"IMX version {version} not supported")

    schema = xmlschema.XMLSchema(xsd_file)
    logger.success(f"Loaded XSD for IMX {version}")
    return schema


def normalize_tag(tag: str | bytes | etree.QName) -> str:
    if hasattr(tag, "text"):
        tag = str(tag)
    if isinstance(tag, bytes | bytearray):
        tag = tag.decode()
    return tag.split("}")[-1]


def validate_tag(expected_type: str, element: _Element) -> None:
    expected = XML_NS + expected_type.split(".")[-1]
    actual = normalize_tag(element.tag)
    if actual != expected.split("}")[-1]:
        raise ValueError(f"Tag mismatch: expected {expected}, got {actual}")


def xsd_validate(schema: xmlschema.XMLSchema, element: _Element, change: dict) -> None:
    xml = etree.tostring(element)
    errors = list(schema.iter_errors(xml))
    if errors:
        change["status"] = change.get("status", "processed") + " – XSD invalid"
        change["xsd_errors"] = "; ".join(err.reason or "" for err in errors)
        logger.error(change["xsd_errors"])


def apply_change(
    change: dict[Hashable, Any], element: _Element, puic_index: PuicIndex
) -> None:
    operation = change.get(RevisionColumns.operation.name, "")
    handlers = {
        RevisionOperationValues.CreateAttribute.name: _handle_create_or_update_attr,
        RevisionOperationValues.UpdateAttribute.name: _handle_create_or_update_attr,
        RevisionOperationValues.DeleteAttribute.name: _handle_delete_attr,
        RevisionOperationValues.DeleteObject.name: _handle_delete_object,
        RevisionOperationValues.AddElementUnder.name: _handle_add_element,
        RevisionOperationValues.DeleteElement.name: _handle_delete_element,
    }
    handler = handlers.get(operation)
    if handler:
        handler(change, element, puic_index)
    else:
        change["status"] = f"NOT processed: {operation} is not valid"


def _finalize(
    change: dict[str, str],
    element: _Element,
    replace_metadata: bool,
    add_metadata: bool,
    metadata_source: str,
    metadata_origin: str,
    metadata_parents: bool,
    registration_time: str | None,
) -> None:
    if replace_metadata or add_metadata:
        set_metadata(
            element,
            metadata_parents,
            replace_metadata=replace_metadata,
            add_metadata=add_metadata,
            metadata_source=metadata_source,
            metadata_origin=metadata_origin,
            registration_time=registration_time,
        )
    change["status"] = change.get("status", "processed")


def _handle_create_or_update_attr(
    change: dict, element: _Element, _: PuicIndex
) -> None:
    new_val = change.get(RevisionColumns.value_new.name)
    if not new_val:
        change["status"] = "skipped"
        return

    attr_path = change.get(RevisionColumns.attribute_or_element.name, "").strip()
    old_val = change.get(RevisionColumns.value_old.name)
    is_update = (
        change.get(RevisionColumns.operation.name)
        == RevisionOperationValues.UpdateAttribute.name
    )

    set_attribute_or_element_by_path(
        element,
        attr_path,
        str(new_val),
        str(old_val) if is_update and old_val is not None else None,
    )


def _handle_delete_attr(change: dict, element: _Element, _: PuicIndex) -> None:
    delete_attribute_if_matching(
        element,
        change.get(RevisionColumns.attribute_or_element.name, "").strip(),
        str(change.get(RevisionColumns.value_old.name, "")),
    )


def _handle_delete_object(
    change: dict, element: _Element, puic_index: PuicIndex
) -> None:
    delete_element(element)
    puic_index.pop(change.get(RevisionColumns.object_puic.name), None)


def _handle_add_element(change: dict, element: _Element, _: PuicIndex) -> None:
    create_element_under(
        element,
        change.get(RevisionColumns.attribute_or_element.name, ""),
        str(change.get(RevisionColumns.value_new.name, "")),
    )


def _handle_delete_element(change: dict, element: _Element, _: PuicIndex) -> None:
    delete_element_that_matches(
        element,
        change.get(RevisionColumns.attribute_or_element.name, ""),
    )


def _process_changes(
    changes: list[dict[Hashable, Any]],
    puic_index: PuicIndex,
    schema: xmlschema.XMLSchema,
    replace_metadata: bool,
    add_metadata: bool,
    metadata_source: str,
    metadata_origin: str,
    metadata_parents: bool,
    registration_time: str | None,
) -> None:
    for change in changes:
        if not change.get(RevisionColumns.will_be_processed.name):
            continue

        puic = change.get(RevisionColumns.object_puic.name)
        element = puic_index.get(puic)
        if element is None:
            change["status"] = f"object not present: {puic}"
            continue

        try:
            validate_tag(change.get(RevisionColumns.object_path.name, ""), element)
            apply_change(change, element, puic_index)
            _finalize(
                change,
                element,
                replace_metadata=replace_metadata,
                add_metadata=add_metadata,
                metadata_source=metadata_source,
                metadata_origin=metadata_origin,
                metadata_parents=metadata_parents,
                registration_time=registration_time,
            )
        except Exception as e:
            logger.error(e)
            change["status"] = f"Error: {e}"
        finally:
            xsd_validate(schema, element, change)

        logger.success(f"Processed change for PUIC {puic}")


def process_imx_revisions(
    input_imx: str | Path,
    input_excel: str | Path,
    out_path: str | Path,
    replace_metadata: bool = False,
    add_metadata: bool = False,
    metadata_source: str = "DV",
    metadata_origin: str = "Other",
    metadata_parents: bool = False,
    registration_time: str | None = None,
    verbose: bool = True,
) -> pd.DataFrame:
    input_imx, input_excel, out_path = _prepare_paths(input_imx, input_excel, out_path)

    try:
        imx_file, log_file = validate_process_input(input_imx, input_excel, out_path)
    except ErrorList as e:
        raise ValueError("Invalid input:\n" + "\n".join(e.errors))

    out_path.mkdir(parents=True, exist_ok=True)
    if verbose:
        print(f"✔ Created output dir: {out_path}")

    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(input_imx, parser)
    root = tree.getroot()

    schema = _load_xsd(root.attrib.get("imxVersion", ""))
    puic_index = {
        el.get("puic"): el for el in tree.findall(".//*[@puic]") if el.get("puic")
    }

    df = _prepare_dataframe(input_excel)
    changes = df.to_dict(orient="records")

    _process_changes(
        changes,
        puic_index,
        schema,
        replace_metadata=replace_metadata,
        add_metadata=add_metadata,
        metadata_source=metadata_source,
        metadata_origin=metadata_origin,
        metadata_parents=metadata_parents,
        registration_time=registration_time,
    )

    tree.write(imx_file, encoding="UTF-8", pretty_print=True)

    out_df = pd.DataFrame(changes)
    _save_results(out_df, log_file)
    return out_df


def _prepare_paths(
    in_imx: str | Path, in_excel: str | Path, out_dir: str | Path
) -> tuple[Path, Path, Path]:
    return Path(in_imx), Path(in_excel), Path(out_dir)


def _prepare_dataframe(excel_path: Path) -> pd.DataFrame:
    df = pd.read_excel(
        excel_path,
        sheet_name="revisions",
        na_values="",
        keep_default_na=False,
        dtype=str,
    )

    df = df.apply(
        lambda col: col.map(lambda v: v.strip() if isinstance(v, str) else "")
    )

    header_map = RevisionColumns.description_to_header()
    df.rename(columns=header_map, inplace=True)

    proc_col = RevisionColumns.will_be_processed.name
    df[proc_col] = df[proc_col].map({"True": True, "False": False, "": False})

    validate_input_excel_content(df)

    missing = set(RevisionColumns.headers()) - set(df.columns)
    if missing:
        raise ValueError(f"Missing template headers: {', '.join(sorted(missing))}")
    return df


def _save_results(df: pd.DataFrame, output: Path) -> None:
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="process-log")
        ws = writer.sheets["process-log"]
        for idx, col in enumerate(df.columns):
            width = max(df[col].astype(str).map(len).max(), len(col)) + 2
            ws.set_column(idx, idx, width)
        ws.freeze_panes(1, 0)
        ws.autofilter(0, 0, 0, len(df.columns) - 1)
