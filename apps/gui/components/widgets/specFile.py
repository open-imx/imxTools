# apps/gui/components/widgets/spec_file_picker.py
from pathlib import Path
from typing import Callable, Optional
from nicegui import ui
from apps.gui.components.widgets.uploadFile import UploadFile


class SpecFilePicker:
    def __init__(
        self,
        label: str = "Upload IMX Spec (.csv)",
        *,
        on_change: Optional[Callable[[Path | None], None]] = None,
        docs_url: str = (
            "https://open-imx.github.io/imxInsights/reference/utils/"
            "header_annotator/#imxInsights.utils.headerAnnotator.HeaderSpec--specification-csv"
        ),
        show_hint: bool = True,
        outlined: bool = True,
        classes: str = "w-full",
        accept: str = ".csv",
    ) -> None:
        self._on_change = on_change
        self._value: Path | None = None
        self._container = ui.column().classes(classes)

        with self._container:
            if show_hint:
                ui.separator()
                with ui.row().classes("items-center gap-2"):
                    ui.label("Upload IMX Spec file (Optional)").classes("italic")
                    if docs_url:
                        ui.link("See docs for more information", docs_url, new_tab=True)

            # uploader row
            with ui.row().classes("w-full items-center gap-2") as row:
                self._uploader = UploadFile(
                    label,
                    on_change=self._handle_upload_change,
                    accept=accept,
                )
                if outlined:
                    pass

            # checkbox for automatic selection
            self.auto_checkbox = ui.checkbox(
                "Automatically select spec file from app folder", value=False
            ).on_value_change(self._handle_auto_toggle)

    # ---------- event plumbing ----------

    @staticmethod
    def _notify_uploaded(p: Path | None) -> None:
        if p:
            ui.notify(f"Uploaded spec: {p.name}")
        else:
            ui.notify("Cleared spec file")

    def _handle_auto_toggle(self, e) -> None:
        """When auto is ON, disable uploader (and clear any uploaded file).
        When auto is OFF, re-enable uploader."""
        is_auto = bool(e.value)

        if is_auto:
            # forbid uploading: disable the uploader widget
            if hasattr(self._uploader, "disable"):
                self._uploader.disable()
            # if a file was already uploaded, clear it so value is None
            if self._uploader.get_value() is not None:
                # this triggers _handle_upload_change(None) via UploadFile.clear()
                self._uploader.clear()
            else:
                # ensure our own state reflects None and notify caller
                self._value = None
                if self._on_change:
                    try:
                        self._on_change(None)
                    except Exception as exc:
                        ui.notify(f"Spec on_change error: {exc}", type="negative")
        else:
            # allow uploading again
            if hasattr(self._uploader, "enable"):
                self._uploader.enable()

    def _handle_upload_change(self, file_path: Path | None) -> None:
        self._value = file_path
        self._notify_uploaded(file_path)

        if file_path:
            # A file is uploaded → uncheck & disable the auto-checkbox
            self.auto_checkbox.set_value(False)
            self.auto_checkbox.disable()
        else:
            # File cleared/unloaded → re-enable the auto-checkbox
            self.auto_checkbox.enable()

        if self._on_change:
            try:
                self._on_change(file_path)
            except Exception as e:
                ui.notify(f"Spec on_change error: {e}", type="negative")

    # ---------- public API ----------

    def get_value(self) -> Path | None:
        """Return the selected spec file path (or None)."""
        # If auto is on, we don't allow manual upload; return None here.
        if self.auto_checkbox.value:
            return None
        return self._value or self._uploader.get_value()

    def set_value(self, path: Path | None) -> None:
        if hasattr(self._uploader, "set_value"):
            self._uploader.set_value(path)
        self._value = path

        if path:
            self.auto_checkbox.set_value(False)
            self.auto_checkbox.disable()
            if hasattr(self._uploader, "enable"):
                self._uploader.enable()
        else:
            self.auto_checkbox.enable()
            # Only enable uploader if auto mode is OFF
            if not self.auto_checkbox.value and hasattr(self._uploader, "enable"):
                self._uploader.enable()

    def set_visibility(self, visible: bool) -> None:
        self._container.visible = visible

    def disable(self) -> None:
        if hasattr(self._uploader, "disable"):
            self._uploader.disable()
        self.auto_checkbox.disable()

    def enable(self) -> None:
        # Only enable uploader if auto is OFF
        if not self.auto_checkbox.value and hasattr(self._uploader, "enable"):
            self._uploader.enable()
        self.auto_checkbox.enable()
