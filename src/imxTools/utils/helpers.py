import zipfile
from datetime import datetime, timezone
from pathlib import Path

from imxInsights import ImxContainer, ImxSingleFile
from imxInsights.file.singleFileImx.imxSituationEnum import ImxSituationEnum
from lxml import etree


def clear_directory(directory: Path) -> None:
    if directory.exists() and directory.is_dir():
        for item in directory.iterdir():
            if item.is_file() and item.name != "generated.content":
                item.unlink()
            elif item.is_dir():
                clear_directory(item)
                item.rmdir()


def load_imxinsights_container_or_file(path: Path, situation: ImxSituationEnum | None):
    if path.suffix == ".zip":
        return ImxContainer(path)
    elif path.suffix == ".xml":
        if not situation:
            raise ValueError(f"Situation must be specified for single IMX file: {path}")
        imx = ImxSingleFile(path)
        return {
            ImxSituationEnum.InitialSituation: imx.initial_situation,
            ImxSituationEnum.NewSituation: imx.new_situation,
            ImxSituationEnum.Situation: imx.situation,
        }.get(situation)
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")


def zip_folder(folder: Path, output_zip: Path) -> None:
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in folder.rglob("*"):
            zipf.write(file_path, file_path.relative_to(folder))


def create_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ensure_paths(*args):
    return [Path(a) if isinstance(a, str) else a for a in args]


def get_situations(xml_path: Path) -> list[ImxSituationEnum]:
    tree = etree.parse(xml_path)
    root = tree.getroot()
    ns = {"ims": "http://www.prorail.nl/IMSpoor"}
    tag_enum_map = {
        "Situation": ImxSituationEnum.Situation,
        "InitialSituation": ImxSituationEnum.InitialSituation,
        "NewSituation": ImxSituationEnum.NewSituation,
    }

    found_situations = []
    for local_tag, enum_value in tag_enum_map.items():
        found = root.findall(f".//ims:{local_tag}", namespaces=ns)
        if len(found) == 1:
            found_situations.append(enum_value)
        elif len(found) > 1:
            raise ValueError(f"Found multiple <{local_tag}> tags in a single IMX file.")

    return found_situations
