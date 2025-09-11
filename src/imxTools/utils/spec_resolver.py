# src/imxTools/utils/spec_resolver.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Set


@dataclass
class NeedUserSpecChoice(Exception):
    """Exception om de UI te laten kiezen uit meerdere spec-kandidaten."""
    message: str
    candidates: List[Path]


def find_spec_candidates(imx_version: str, spec_root: Path) -> List[Path]:
    """
    Zoek alle CSV-specs voor één IMX-versie, bv:
    build_app_root/specifications/imx_12.0.0/spec-*.csv
    """
    if not imx_version:
        return []
    folder = Path(spec_root) / f"imx_{imx_version}"

    if not folder.exists():
        return []
    return sorted(folder.glob("specification-*.csv"))


def auto_pick_spec_or_raise(imx_versions: Iterable[str | None], spec_root: Path) -> Path | None:
    """
    Probeer automatisch 1 spec te kiezen:
    - Als geen versie(s) bekend: return None (geen spec toepassen).
    - Als exact één versie en exact één kandidaat: return die ene spec.
    - In alle andere gevallen: raise NeedUserSpecChoice met alle kandidaten.
    """
    versions = [v for v in imx_versions if v]
    if not versions:
        return None

    version_set = sorted(set(versions))
    all_candidates: Set[Path] = set()
    for v in version_set:
        all_candidates.update(find_spec_candidates(v, spec_root))

    candidates = sorted(all_candidates)
    if not candidates:
        return None

    if len(version_set) == 1 and len(candidates) == 1:
        return candidates[0]

    raise NeedUserSpecChoice(
        message="Er zijn meerdere mogelijke specificatiebestanden. Maak een keuze.",
        candidates=candidates,
    )
