# app_build_helpers.py
import shutil
import time
import zipfile
from datetime import date
from pathlib import Path

from imxInsights import __version__ as imxInsights_version

from imxTools import __version__ as imxTools_version


def insert_readable_metadata(file_path: Path, app_name: str):
    metadata = (
        f"# **{app_name}** \n"
        f"**Build**: v{imxTools_version}  \n"
        f"**Build Date**: {date.today().isoformat()}  \n"
        f"**imxInsights Version**: {imxInsights_version}  \n\n"
        f"---\n\n"
        f"## MIT License\n\n"
        "Copyright (c) 2023–present Open-IMX. All rights reserved.\n\n"
        "Permission is hereby granted, free of charge, to any person obtaining a copy "
        'of this software and associated documentation files (the "Software"), to deal '
        "in the Software without restriction, including without limitation the rights "
        "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell "
        "copies of the Software, and to permit persons to whom the Software is "
        "furnished to do so, subject to the following conditions:  \n\n"
        "The above copyright notice and this permission notice shall be included "
        "in all copies or substantial portions of the Software.  \n\n"
        'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR '
        "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, "
        "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE "
        "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER "
        "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, "
        "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE "
        "SOFTWARE.  \n\n"
        "---\n\n"
    )
    original = file_path.read_text(encoding="utf-8") if file_path.exists() else ""
    file_path.write_text(metadata + original, encoding="utf-8")


def zip_result(
    folder_path: Path, version: str, system: str, app_name: str, dist_root: Path
):
    zip_name = f"{app_name}-{version}-{system}.zip"
    zip_path = dist_root / zip_name
    print(f"📦 Creating ZIP: {zip_path}")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in folder_path.rglob("*"):
            zipf.write(file, arcname=file.relative_to(folder_path))

    print(f"✅ Packaged: {zip_path}")


def remove_folder_safely(path: Path, retries=3, delay=1):
    for i in range(retries):
        try:
            if path.exists():
                shutil.rmtree(path)
            else:
                return
        except Exception as e:
            print(f"⚠️ Attempt {i + 1}: Failed to remove {path}: {e}")
            time.sleep(delay)
    print(f"❌ Giving up on deleting {path}")
