# src/imxTools/insights/diff_and_population.py
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Literal, Union

from imxInsights import ImxContainer, ImxMultiRepo
from imxInsights.utils.headerAnnotator import HeaderSpec
from imxInsights.file.singleFileImx.imxSituationEnum import ImxSituationEnum

from src.imxTools.utils.helpers import load_imxinsights_container_or_file
from src.imxTools.utils.spec_resolver import auto_pick_spec_or_raise

SpecArg = Union[Path, None, Literal["AUTO"]]


def _header_spec_from(spec_file: Path | None) -> HeaderSpec | None:
    return HeaderSpec(str(spec_file)) if isinstance(spec_file, Path) else None


def write_diff_output_files(
    t1_path: Path,
    t2_path: Path,
    out_path: Path | None,
    t1_situation: ImxSituationEnum | None,
    t2_situation: ImxSituationEnum | None,
    geojson: bool,
    to_wgs: bool,
    version_safe: bool = False,
    spec_file: SpecArg = None,
    specs_location: Path = None,

):
    out_path = Path(out_path) if out_path else Path.cwd()

    t1 = load_imxinsights_container_or_file(t1_path, t1_situation)
    if not t1:
        raise ValueError("IMX T1 results in None. Is de situatie aanwezig in het IMX-bestand?")

    t2_same_file = t1_path == t2_path and not isinstance(t1, ImxContainer)
    if t2_same_file:
        t2 = load_imxinsights_container_or_file(t1_path, t2_situation)
    else:
        t2 = load_imxinsights_container_or_file(t2_path, t2_situation)

    if not t2:
        raise ValueError("IMX T2 results in None. Is de situatie aanwezig in het IMX-bestand?")

    # AUTO-resolutie van spec (kan NeedUserSpecChoice raisen; UI vangt dat af)
    if spec_file == "AUTO":
        resolved_spec = auto_pick_spec_or_raise([
            getattr(t1, "imx_version", None),
            getattr(t2, "imx_version", None),
        ], specs_location)
    elif isinstance(spec_file, Path):
        resolved_spec = spec_file
    else:
        resolved_spec = None

    multi_repo = ImxMultiRepo([t1, t2], version_safe=version_safe)  # type: ignore[abstract]
    compare = multi_repo.compare(container_id_1=t1.container_id, container_id_2=t2.container_id)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    compare.to_excel(out_path / f"{timestamp}-diff.xlsx",
                     header_spec=_header_spec_from(resolved_spec))

    if geojson:
        compare.create_geojson_files(out_path / f"{timestamp}-geojsons", to_wgs=to_wgs)


def write_population_output_files(
    imx: Path,
    out_path: Path | None,
    imx_situation: ImxSituationEnum | None,
    geojson: bool,
    to_wgs: bool,
    spec_file: SpecArg | None = None,
    specs_location: Path | None = None,
):
    out_path = Path(out_path) if out_path else Path.cwd()

    t1 = load_imxinsights_container_or_file(imx, imx_situation)

    # AUTO-resolutie (kan NeedUserSpecChoice raisen; UI vangt dat)
    if spec_file == "AUTO":
        resolved_spec = auto_pick_spec_or_raise([getattr(t1, "imx_version", None)], specs_location)
    elif isinstance(spec_file, Path):
        resolved_spec = spec_file
    else:
        resolved_spec = None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    t1.to_excel(out_path / f"{timestamp}-population.xlsx",
                header_spec=_header_spec_from(resolved_spec))

    if geojson:
        t1.create_geojson_files(out_path / f"{timestamp}-geojsons", to_wgs=to_wgs)
