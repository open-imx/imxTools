import os
import shutil
import subprocess
import sys
from pathlib import Path

import nicegui

from apps.build_helpers import (
    insert_readable_metadata,
    zip_result,
    remove_folder_safely,
)
from imxTools import __version__ as imxTools_version

# App constants
EXECUTABLE_NAME = "imx-tools-gui"
APP_FOLDER_NAME = f"{EXECUTABLE_NAME}-{imxTools_version}-windows"
ENTRY_FILE = "apps/gui/main.py"

# PathsDATA_FOLDER = Path("data")
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
    print(f'🚀 Building NiceGUI app "{EXECUTABLE_NAME}" in isolated temp environment...')

    remove_folder_safely(BUILD_FOLDER)
    BUILD_FOLDER.mkdir(parents=True, exist_ok=True)

    entry_path = Path(ENTRY_FILE).resolve()

    process = subprocess.Popen(
        [
            sys.executable, "-m", "nicegui.scripts.pack",
            "--name", EXECUTABLE_NAME,
            str(entry_path)
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
        print(line, end="")

    process.wait()

    if process.returncode != 0:
        print(f"\n❌ Build failed with exit code {process.returncode}")
        sys.exit(process.returncode)

    print("✅ Build complete.")

    # Locate built app
    dist_path = BUILD_FOLDER / "dist"
    candidates = list(dist_path.glob(f"{EXECUTABLE_NAME}*"))
    if not candidates:
        print(f"❌ Could not find built app in {dist_path}")
        sys.exit(1)

    built_path = candidates[0]

    FINAL_APP_FOLDER.parent.mkdir(parents=True, exist_ok=True)
    remove_folder_safely(FINAL_APP_FOLDER)
    shutil.move(str(built_path), str(FINAL_APP_FOLDER))
    print(f"📁 App moved to: {FINAL_APP_FOLDER}")


def patch_static_assets():
    if not STATIC_SRC.exists():
        print(f"❌ Could not find NiceGUI static files at {STATIC_SRC}")
        sys.exit(1)
    print(f"⚖️ Copying static files from {STATIC_SRC} to {STATIC_DST}")
    STATIC_DST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(STATIC_SRC, STATIC_DST, dirs_exist_ok=True)
    print("✅ Static files copied.")


def write_readme():
    readme_path = FINAL_APP_FOLDER / "README.md"
    insert_readable_metadata(readme_path, APP_FOLDER_NAME)
    print(f"📘 Added metadata to README: {readme_path}")


def main():
    build_nicegui_app()
    patch_static_assets()
    write_readme()
    zip_result(FINAL_APP_FOLDER, imxTools_version, "windows", EXECUTABLE_NAME, DIST_ROOT)
    print(f"🎉 App ready at {FINAL_APP_FOLDER}")


if __name__ == "__main__":
    main()

    if CLEANUP and BUILD_FOLDER.exists():
        shutil.rmtree(BUILD_FOLDER)
