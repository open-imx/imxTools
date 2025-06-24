from datetime import datetime
from pathlib import Path

from imxInsights import ImxContainer, ImxMultiRepo
from imxInsights.file.singleFileImx.imxSituationEnum import ImxSituationEnum

from src.imxTools.utils.helpers import load_imxinsights_container_or_file


def write_diff_output_files(
    t1_path: Path,
    t2_path: Path,
    out_path: Path | None,
    t1_situation: ImxSituationEnum | None,
    t2_situation: ImxSituationEnum | None,
    geojson: bool,
    to_wgs: bool,
    version_safe: bool = False,
):
    out_path = Path(out_path) if out_path else Path.cwd()

    t1 = load_imxinsights_container_or_file(t1_path, t1_situation)
    if not t1:
        raise ValueError(
            "IMX T1 results in None. Is the situation present in the IMX file?"
        )

    t2_same_file = t1_path == t2_path and not isinstance(t1, ImxContainer)
    if t2_same_file:
        t2 = load_imxinsights_container_or_file(t1_path, t2_situation)
    else:
        t2 = load_imxinsights_container_or_file(t2_path, t2_situation)

    if not t2:
        raise ValueError(
            "IMX T2 results in None. Is the situation present in the IMX file?"
        )

    multi_repo = ImxMultiRepo([t1, t2], version_safe=version_safe)  # type: ignore[abstract]
    compare = multi_repo.compare(
        container_id_1=t1.container_id,
        container_id_2=t2.container_id,
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    compare.to_excel(out_path / f"{timestamp}-diff.xlsx")

    if geojson:
        compare.create_geojson_files(out_path / f"{timestamp}-geojsons", to_wgs=to_wgs)


def write_population_output_files(
    imx: Path,
    out_path: Path | None,
    imx_situation: ImxSituationEnum | None,
    geojson: bool,
    to_wgs: bool,
):
    out_path = Path(out_path) if out_path else Path.cwd()

    t1 = load_imxinsights_container_or_file(imx, imx_situation)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    t1.to_excel(out_path / f"{timestamp}-population.xlsx")

    if geojson:
        t1.create_geojson_files(out_path / f"{timestamp}-geojsons", to_wgs=to_wgs)
