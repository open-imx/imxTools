from nicegui import ui
from datetime import datetime, timezone


class IsoTimePicker:
    def __init__(self, label="ISO DateTime", default_utc=True):
        now = datetime.now(timezone.utc)
        current_date = now.strftime("%Y-%m-%d")
        current_time = "00:00"

        self.iso_input = ui.input(
            label=label, value=f"{current_date}T{current_time}:00Z"
        )
        self.date_input = ui.input(label="Date", value=current_date)
        self.time_input = ui.input(label="Time", value=current_time)

        self.error_state = False  # Track validity

        with self.date_input.add_slot("append"):
            with ui.menu() as date_menu:
                self.date_picker = ui.date(value=current_date)
                self.date_picker.bind_value(self.date_input)
                self.date_picker.on("update:model-value", self._sync_from_parts)
                with ui.row().classes("justify-end"):
                    ui.button("Close", on_click=date_menu.close).props("flat")
            ui.icon("edit_calendar").on("click", date_menu.open).classes(
                "cursor-pointer"
            )

        with self.time_input.add_slot("append"):
            with ui.menu() as time_menu:
                self.time_picker = ui.time(value=current_time)
                self.time_picker.bind_value(self.time_input)
                self.time_picker.on("update:model-value", self._sync_from_parts)
                with ui.row().classes("justify-end"):
                    ui.button("Close", on_click=time_menu.close).props("flat")
            ui.icon("access_time").on("click", time_menu.open).classes("cursor-pointer")

        self.iso_input.on("blur", self._validate_and_sync_from_iso)
        self.date_input.on("update:model-value", self._sync_from_parts)
        self.time_input.on("update:model-value", self._sync_from_parts)

    @property
    def value(self):
        return self.iso_input.value

    def set_value(self, iso_string: str):
        self.iso_input.value = iso_string
        self._validate_and_sync_from_iso(None)

    def set_visibility(self, visible: bool):
        self.iso_input.set_visibility(visible)
        self.date_input.set_visibility(visible)
        self.time_input.set_visibility(visible)

    def is_valid(self):
        """Returns True if ISO input is valid"""
        try:
            datetime.strptime(self.iso_input.value, "%Y-%m-%dT%H:%M:%SZ")
            return True
        except ValueError:
            return False

    def _validate_and_sync_from_iso(self, _):
        """Validate ISO and sync pickers if valid"""
        if self.is_valid():
            self.iso_input.error = None
            self.error_state = False
            self._sync_from_iso(_)
        else:
            self.iso_input.error = "Invalid ISO format"
            self.error_state = True
            ui.notify("Invalid ISO format. Use YYYY-MM-DDTHH:MM:SSZ", type="warning")

    def _sync_from_iso(self, _):
        """Update date/time pickers from ISO"""
        try:
            dt = datetime.strptime(self.iso_input.value, "%Y-%m-%dT%H:%M:%SZ")
            self.date_input.value = dt.strftime("%Y-%m-%d")
            self.time_input.value = dt.strftime("%H:%M")
        except Exception:
            pass

    def _sync_from_parts(self, _=None):
        """Update ISO input from date/time pickers"""
        if not self.date_input.value or not self.time_input.value:
            return
        self.iso_input.value = f"{self.date_input.value}T{self.time_input.value}:00Z"
        self._validate_and_sync_from_iso(None)
