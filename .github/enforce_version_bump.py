# scripts/enforce_version_bump.py
import os
import re
import subprocess
import sys
from pathlib import Path

from packaging.version import parse


def extract_version_from_pyproject(content: str) -> str:
    match = re.search(
        r'(?ms)^\[tool\.bumpversion\].*?^current_version\s*=\s*"([^"]+)"', content
    )
    if not match:
        raise ValueError("Could not find current_version in pyproject.toml")
    return match.group(1).strip()


def get_file_from_git(branch: str, path: Path) -> str:
    repo_root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    relative_path = path.relative_to(repo_root).as_posix()

    result = subprocess.run(
        ["git", "show", f"origin/{branch}:{relative_path}"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def get_current_branch() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def main():
    pyproject_path = Path(os.path.abspath(__file__)).parent.parent / "pyproject.toml"

    with open(pyproject_path, "r", encoding="utf-8") as f:
        current_version = extract_version_from_pyproject(f.read())

    base_ref = os.getenv("GITHUB_BASE_REF") or get_current_branch()

    if base_ref not in ("master", "develop"):
        print(
            f"Skipping version check: not targeting master or develop (target: {base_ref})"
        )
        return

    try:
        target_content = get_file_from_git(base_ref, pyproject_path)
        target_version = extract_version_from_pyproject(target_content)
    except Exception as e:
        print(f"Error fetching version from origin/{base_ref}: {e}")
        sys.exit(1)

    current = parse(current_version)
    target = parse(target_version)

    print(f"Current version: {current}")
    print(f"Target branch ({base_ref}) version: {target}")

    if current <= target:
        print(f"Version must be higher than in {base_ref} branch ({target})")
        sys.exit(1)

    print(f"Version bump OK: {current} > {target}")


if __name__ == "__main__":
    main()
