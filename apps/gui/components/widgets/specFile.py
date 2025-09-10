# apps/gui/components/widgets/spec_file_picker.py
from pathlib import Path
from typing import Callable, Optional, Literal
from nicegui import ui
from apps.gui.components.widgets.uploadFile import UploadFile

Mode = Literal["auto", "pick", "none"]

# NiceGUI radio uses the label as the value; map labels <-> internal modes
LABEL_TO_MODE: dict[str, Mode] = {"None": "none", "Auto": "auto", "Pick": "pick"}
MODE_TO_LABEL: dict[Mode, str] = {v: k for k, v in LABEL_TO_MODE.items()}

# Versions offered for Auto mode; keep "None" for detection
AUTO_VERSION_LABELS = ["Detect automatically", "1.2.4", "5.0.0", "12.0.0"]
AUTO_VERSION_NONE_LABEL = AUTO_VERSION_LABELS[0]


class SpecFilePicker:
    def __init__(
        self,
        label: str = "Upload IMX Spec (.csv)",
        *,
        on_change: Optional[Callable[[Path | None], None]] = None,
        show_hint: bool = True,
        outlined: bool = True,
        classes: str = "w-full",
        expanded: bool = False,
        default_mode: Mode = "none",
    ) -> None:
        self._on_change = on_change
        self._value: Path | None = None
        self._mode: Mode = default_mode
        self._prev_mode: Mode = default_mode  # remember last non-pick mode
        self._auto_version: str | None = None  # None means detect

        self._container = ui.column().classes(classes)
        with self._container:
            # Row 1: label (left) + radio options directly after it (inline)
            with ui.row().classes("w-full items-center gap-3 flex-nowrap"):
                ui.label("Specifications options").classes("text-base font-medium")
                self.mode_radio = (
                    ui.radio(
                        options=list(LABEL_TO_MODE.keys()),  # "None", "Auto", "Pick"
                        value=MODE_TO_LABEL.get(default_mode, "None"),
                    )
                    .props("inline dense")   # horizontal & compact
                    .classes("flex-none")    # sit right after the label
                    .on_value_change(self._handle_mode_change)
                )

                # Auto-mode version dropdown (shown only when mode == "auto")
                self._auto_version_select = (
                    ui.select(
                        options=AUTO_VERSION_LABELS,
                        value=AUTO_VERSION_NONE_LABEL,
                        label="Auto version",
                    )
                    .props("outlined dense")
                    .classes("min-w-[220px]")
                    .on_value_change(self._handle_auto_version_change)
                )

            # Row 2: the expansion BELOW the first row
            self._expansion = (
                ui.expansion(
                    "Upload IMX Spec",
                    value=expanded if default_mode == "pick" else False,
                    icon="upload_file",
                )
                .on_value_change(self._handle_expansion_toggle)
                .classes("w-full")
            )

            # Content of expansion
            with self._expansion:
                with ui.row().classes("w-full items-center gap-2"):
                    self._uploader = UploadFile(
                        label,
                        on_change=self._handle_upload_change,
                        accept=".csv",
                        max_files=1,
                    )
                    if outlined:
                        pass  # hook for outlined styling

                if show_hint:
                    with ui.row().classes("items-center gap-2"):
                        ui.label("Upload IMX Spec file (Optional)").classes("italic")
                        docs_url = (
                            "https://open-imx.github.io/imxInsights/reference/utils/header_annotator/"
                            "#imxInsights.utils.headerAnnotator.HeaderSpec--specification-csv"
                        )
                        ui.link("See docs for more information", docs_url, new_tab=True)

        # enforce initial mode state
        self._apply_mode(self._mode, initial=True)

    # ---------- helpers ----------

    @staticmethod
    def _notify_uploaded(p: Path | None) -> None:
        if p:
            ui.notify(f"Uploaded spec: {p.name}")
        else:
            ui.notify("Cleared spec file")

    def _apply_mode(self, mode: Mode, *, initial: bool = False) -> None:
        """Apply UI state for the given mode."""
        self._mode = mode
        is_pick = mode == "pick"
        is_auto = mode == "auto"
        is_none = mode == "none"

        # Keep track of the last non-pick mode so we can restore it
        if not is_pick:
            self._prev_mode = mode

        # Expansion is only meaningful in 'pick' mode
        try:
            if is_pick:
                self._expansion.set_value(self._expansion.value if initial else True)
            else:
                self._expansion.set_value(False)
        except Exception:
            pass

        # Uploader interactivity
        if hasattr(self._uploader, "enable") and is_pick:
            self._uploader.enable()
        if hasattr(self._uploader, "disable") and not is_pick:
            self._uploader.disable()

        # Show/hide auto version dropdown
        self._auto_version_select.set_visibility(is_auto)

        # In auto/none we want no file; clear any uploaded file
        if (is_auto or is_none) and self._uploader.get_value() is not None:
            self._uploader.clear()
        elif is_auto or is_none:
            self._value = None
            if not initial and self._on_change:
                try:
                    self._on_change(None)
                except Exception as exc:
                    ui.notify(f"Spec on_change error: {exc}", type="negative")

    # ---------- event handlers ----------

    def _handle_mode_change(self, e) -> None:
        """Radio changed: convert label to internal mode and apply."""
        label = e.value  # "None" | "Auto" | "Pick"
        new_mode: Mode = LABEL_TO_MODE.get(label, "none")
        self._apply_mode(new_mode)

    def _handle_expansion_toggle(self, e) -> None:
        """Switch to pick mode when expanded, restore previous mode when collapsed."""
        if e.value:  # expansion opened
            if self._mode != "pick":
                # remember current non-pick mode, then switch to pick
                self._prev_mode = self._mode
            self.set_mode("pick")
        else:  # expansion closed
            # restore the last non-pick mode, if any
            if self._prev_mode in ("none", "auto"):
                self.set_mode(self._prev_mode)

    def _handle_auto_version_change(self, e) -> None:
        """Track selected version in Auto mode."""
        label = e.value or AUTO_VERSION_NONE_LABEL
        if label == AUTO_VERSION_NONE_LABEL:
            self._auto_version = None
        else:
            self._auto_version = label  # store the version string, e.g. "5.0.0"

    def _handle_upload_change(self, file_path: Path | None) -> None:
        """Uploader changed: keep value only in Pick mode."""
        self._value = file_path if self._mode == "pick" else None
        self._notify_uploaded(self._value)

        if self._on_change:
            try:
                self._on_change(self._value)
            except Exception as exc:
                ui.notify(f"Spec on_change error: {exc}", type="negative")

    # ---------- public API ----------

    def get_value(self) -> Path | None:
        """Return the selected spec file path (or None)."""
        if self._mode != "pick":
            return None
        return self._value or self._uploader.get_value()

    def set_value(self, path: Path | None) -> None:
        """Set an uploaded value programmatically."""
        if path is not None and self._mode != "pick":
            self.mode_radio.set_value(MODE_TO_LABEL["pick"])
            self._apply_mode("pick")

        if hasattr(self._uploader, "set_value"):
            self._uploader.set_value(path)
        self._value = path

    def set_mode(self, mode: Mode) -> None:
        """Programmatically switch mode."""
        if mode not in ("auto", "pick", "none"):
            ui.notify(f"Unknown mode: {mode}", type="negative")
            return
        # radio expects label
        self.mode_radio.set_value(MODE_TO_LABEL[mode])
        self._apply_mode(mode)

    def get_mode(self) -> Mode:
        return self._mode

    def get_auto_version(self) -> str | None:
        """Return the selected version for Auto mode or None for detection."""
        return self._auto_version

    def set_visibility(self, visible: bool) -> None:
        self._container.visible = visible

    def disable(self) -> None:
        if hasattr(self._uploader, "disable"):
            self._uploader.disable()
        self.mode_radio.disable()
        self._auto_version_select.disable()

    def enable(self) -> None:
        if self._mode == "pick" and hasattr(self._uploader, "enable"):
            self._uploader.enable()
        self.mode_radio.enable()
        if self._mode == "auto":
            self._auto_version_select.enable()
