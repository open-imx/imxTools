import os
import shutil
import subprocess
import sys
from pathlib import Path

import nicegui

from apps.build_helpers import (
    insert_readable_metadata,
    zip_result,
    remove_folder_safely, print_unicode_safe,
)
from imxTools import __version__ as imxTools_version


# App constants
EXECUTABLE_NAME = "imx-tools-gui"
APP_FOLDER_NAME = f"{EXECUTABLE_NAME}-{imxTools_version}-windows"
ENTRY_FILE = "apps/gui/main.py"

DIST_ROOT = Path("dist")
FINAL_APP_FOLDER = DIST_ROOT / APP_FOLDER_NAME
BUILD_FOLDER = Path(".build_gui_app")

STATIC_SRC = Path(nicegui.__path__[0]) / "static"
STATIC_DST = FINAL_APP_FOLDER / "_internal" / "nicegui" / "static"

# Cleanup flags
CLEAN_BUILD_FOLDER = True
CLEANUP = True

if CLEAN_BUILD_FOLDER and BUILD_FOLDER.exists():
    shutil.rmtree(BUILD_FOLDER)


def build_nicegui_app():
    print_unicode_safe(f'Building NiceGUI app "{EXECUTABLE_NAME}" in isolated temp environment...')

    remove_folder_safely(BUILD_FOLDER)
    BUILD_FOLDER.mkdir(parents=True, exist_ok=True)

    entry_path = Path(ENTRY_FILE).resolve()

    # Paths to include
    add_data_args = []
    paths_to_include = [
        (Path("src/data").resolve(), "src/data"),
        (Path("apps/gui/data").resolve(), "apps\\gui\\data\\"),
    ]

    for source, target in paths_to_include:
        add_data_args.extend(["--add-data", f"{source}{os.pathsep}{target}"])

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "nicegui.scripts.pack",
            "--name",
            EXECUTABLE_NAME,
            *add_data_args,
            str(entry_path),
        ],
        cwd=BUILD_FOLDER,
        env={**os.environ, "NICEGUI_AUTOSTART": "0"},
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )

    for line in process.stdout:
        print_unicode_safe(line.rstrip())

    process.wait()

    if process.returncode != 0:
        print_unicode_safe(f"\nBuild failed with exit code {process.returncode}")
        sys.exit(process.returncode)

    print_unicode_safe("Build complete.")

    # Locate built app
    dist_path = BUILD_FOLDER / "dist"
    candidates = list(dist_path.glob(f"{EXECUTABLE_NAME}*"))
    if not candidates:
        print_unicode_safe(f"Could not find built app in {dist_path}")
        sys.exit(1)

    built_path = candidates[0]

    FINAL_APP_FOLDER.parent.mkdir(parents=True, exist_ok=True)
    remove_folder_safely(FINAL_APP_FOLDER)
    shutil.move(str(built_path), str(FINAL_APP_FOLDER))
    print_unicode_safe(f"App moved to: {FINAL_APP_FOLDER}")


def patch_static_assets():
    if not STATIC_SRC.exists():
        print_unicode_safe(f"Could not find NiceGUI static files at {STATIC_SRC}")
        sys.exit(1)
    print_unicode_safe(f"Copying static files from {STATIC_SRC} to {STATIC_DST}")
    STATIC_DST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(STATIC_SRC, STATIC_DST, dirs_exist_ok=True)
    print_unicode_safe("Static files copied.")


def write_readme():
    readme_path = FINAL_APP_FOLDER / "README.md"
    insert_readable_metadata(readme_path, APP_FOLDER_NAME)
    print_unicode_safe(f"Added metadata to README: {readme_path}")


def main():
    build_nicegui_app()
    patch_static_assets()
    write_readme()
    zip_result(
        FINAL_APP_FOLDER, imxTools_version, "windows", EXECUTABLE_NAME, DIST_ROOT
    )
    print_unicode_safe(f"App ready at {FINAL_APP_FOLDER}")


if __name__ == "__main__":
    main()

    if CLEANUP and BUILD_FOLDER.exists():
        shutil.rmtree(BUILD_FOLDER)
