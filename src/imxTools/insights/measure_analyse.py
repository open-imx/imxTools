from pathlib import Path

import pandas as pd
from imxInsights.repo.imxRepo import ImxRepo
from shapely import LineString, Point

from src.imxTools.insights.mesaure_analyse_enums import MeasureAnalyseColumns
from src.imxTools.revision.revision_enums import (
    RevisionColumns,
    RevisionOperationValues,
)
from src.imxTools.utils.measure_line import (
    MeasureLine,
    PointMeasureResult,
)
from src.imxTools.utils.helpers import create_timestamp


from loguru import logger


def _is_valid_geometry(geometry) -> bool:
    return isinstance(geometry, Point | LineString)


def _is_rail_connection_ref(ref_field: str) -> bool:
    return ref_field.endswith("@railConnectionRef")


def _get_or_create_measure_line(
    puic: str, rail_con, cache: dict[str, MeasureLine]
) -> MeasureLine:
    if puic not in cache:
        cache[puic] = MeasureLine(rail_con.geometry)
    return cache[puic]


def _extract_measure(
    ref_field: str, measure_type: str, properties: dict
) -> float | None:
    measure_field = ref_field.replace("@railConnectionRef", measure_type)
    measure = properties.get(measure_field, None)
    return float(measure) if measure else None


def _calculate_row(
    imx_object,
    ref_field,
    rail_con,
    measure_type,
    measure: float | None,
    projection_result: PointMeasureResult,
) -> dict:
    puic = rail_con.puic

    diff_3d = (
        abs(measure - projection_result.measure_3d)
        if measure is not None and projection_result.measure_3d is not None
        else None
    )

    diff_2d = (
        abs(measure - projection_result.measure_2d)
        if measure is not None and projection_result.measure_2d is not None
        else None
    )

    return {
        MeasureAnalyseColumns.object_path.name: imx_object.path,
        MeasureAnalyseColumns.object_puic.name: imx_object.puic,
        MeasureAnalyseColumns.object_name.name: imx_object.name,
        MeasureAnalyseColumns.ref_field.name: ref_field,
        MeasureAnalyseColumns.ref_field_value.name: puic,
        MeasureAnalyseColumns.ref_field_name.name: rail_con.name,
        MeasureAnalyseColumns.measure_type.name: measure_type,
        MeasureAnalyseColumns.imx_measure.name: measure,
        MeasureAnalyseColumns.calculated_measure_3d.name: round(
            projection_result.measure_3d, 3
        )
        if projection_result.measure_3d is not None
        else None,
        MeasureAnalyseColumns.abs_imx_vs_3d.name: diff_3d,
        MeasureAnalyseColumns.calculated_measure_2d.name: projection_result.measure_2d,
        MeasureAnalyseColumns.abs_imx_vs_2d.name: diff_2d,
    }


def calculate_measurements(imx: ImxRepo) -> list:
    results = []
    measure_lines: dict[str, MeasureLine] = {}

    # todo: we should do this async so we gain some speed

    for obj in imx.get_all():
        if not _is_valid_geometry(obj.geometry):
            continue

        for ref in obj.refs:
            if not _is_rail_connection_ref(ref.field):
                continue

            rail_con = ref.imx_object
            if not rail_con:
                logger.warning(
                    f"rail connection {ref.field_value} not found for {obj.puic}"
                )
                continue

            logger.info(f"calculating measure for {obj.puic} {ref.imx_object.puic}")

            measure_line = _get_or_create_measure_line(
                rail_con.puic, rail_con, measure_lines
            )

            if isinstance(obj.geometry, Point):
                projection_result = measure_line.project(obj.geometry)
                imx_measure = _extract_measure(ref.field, "@atMeasure", obj.properties)
                results.append(
                    _calculate_row(
                        obj,
                        ref.field,
                        rail_con,
                        "atMeasure",
                        imx_measure,
                        projection_result,
                    )
                )
            elif isinstance(obj.geometry, LineString):
                projection__line_result = measure_line.project_line(obj.geometry)

                # todo: geometry should be first point from and the to end point

                # FromMeasure
                imx_measure = _extract_measure(
                    ref.field, "@fromMeasure", obj.properties
                )
                results.append(
                    _calculate_row(
                        obj,
                        ref.field,
                        rail_con,
                        "fromMeasure",
                        imx_measure,
                        projection__line_result.from_result,
                    )
                )

                # ToMeasure
                imx_measure = _extract_measure(ref.field, "@toMeasure", obj.properties)
                results.append(
                    _calculate_row(
                        obj,
                        ref.field,
                        rail_con,
                        "toMeasure",
                        imx_measure,
                        projection__line_result.to_result,
                    )
                )

    return results


def generate_analyse_df(imx: ImxRepo) -> pd.DataFrame:
    results = calculate_measurements(imx)
    df_analyse = pd.DataFrame(results)
    return df_analyse


def convert_analyse_to_issue_list(
    df_analyse: pd.DataFrame, threshold: float = 0.001
) -> pd.DataFrame:
    revision_columns = [
        RevisionColumns.object_path.name,
        RevisionColumns.object_puic.name,
        RevisionColumns.issue_comment.name,
        RevisionColumns.issue_cause.name,
        RevisionColumns.attribute_or_element.name,
        RevisionColumns.operation.name,
        RevisionColumns.value_old.name,
        RevisionColumns.value_new.name,
        RevisionColumns.will_be_processed.name,
        RevisionColumns.revision_reasoning.name,
    ]

    df_issue_list = df_analyse[
        [
            MeasureAnalyseColumns.object_path.name,
            MeasureAnalyseColumns.object_puic.name,
            MeasureAnalyseColumns.imx_measure.name,
            MeasureAnalyseColumns.calculated_measure_3d.name,
        ]
    ].copy()

    df_issue_list = df_issue_list.rename(
        columns={
            MeasureAnalyseColumns.object_path.name: RevisionColumns.object_path.name,
            MeasureAnalyseColumns.object_puic.name: RevisionColumns.object_puic.name,
            MeasureAnalyseColumns.imx_measure.name: RevisionColumns.value_old.name,
            MeasureAnalyseColumns.calculated_measure_3d.name: RevisionColumns.value_new.name,
        }
    )

    df_issue_list[RevisionColumns.operation.name] = (
        RevisionOperationValues.UpdateAttribute.name
    )

    df_issue_list[RevisionColumns.attribute_or_element.name] = df_analyse.apply(
        lambda row: row[MeasureAnalyseColumns.ref_field.name].replace(
            "@railConnectionRef", f"@{row[MeasureAnalyseColumns.measure_type.name]}"
        )
        if isinstance(row[MeasureAnalyseColumns.ref_field.name], str)
        else row[MeasureAnalyseColumns.ref_field.name],
        axis=1,
    )

    df_issue_list = df_issue_list[
        (
            df_issue_list[RevisionColumns.value_old.name]
            - df_issue_list[RevisionColumns.value_new.name]
        ).abs()
        > threshold
    ]

    df_issue_list[RevisionColumns.issue_comment.name] = (
        f"Absolute delta between calculated and IMX measures exceeds the threshold of {threshold}m."
    )

    for col in revision_columns:
        if col not in df_issue_list.columns:
            df_issue_list[col] = None

    return df_issue_list[revision_columns]


def generate_measure_excel(
    imx: ImxRepo, output_path: str | Path, threshold: float = 0.015
):
    if isinstance(output_path, str):
        output_path = Path(output_path)
    if output_path.is_dir():
        output_path = output_path / f"measure_check-{create_timestamp()}.xlsx"

    df_analyse = generate_analyse_df(imx)
    df_issue_list = convert_analyse_to_issue_list(df_analyse, threshold)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df_analyse.to_excel(writer, index=False, sheet_name="measure_check")
        df_issue_list.to_excel(writer, index=False, sheet_name="revisions")
