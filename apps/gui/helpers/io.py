import asyncio
import shutil
import tempfile
from pathlib import Path
from nicegui.elements.upload import MultiUploadEventArguments


def spooled_file_to_temp_file(e: MultiUploadEventArguments) -> Path:
    original_filename = e.name
    temp_dir = Path(tempfile.gettempdir())
    temp_path = temp_dir / original_filename
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(e.content, f)
    return temp_path


async def delete_later(path: Path, delay: float = 30.0):
    await asyncio.sleep(delay)
    try:
        if path.exists():
            path.unlink()
    except Exception as e:
        print(f"Error deleting ZIP file: {e}")


def load_markdown(relative_file_path: str) -> str:
    base_path = Path(__file__).parent  # folder of this file
    md_path = (base_path / relative_file_path).resolve()
    return md_path.read_text(encoding="utf-8")
