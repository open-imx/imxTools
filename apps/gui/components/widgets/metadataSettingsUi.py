from dataclasses import dataclass
from nicegui import ui
from apps.gui.components.widgets.isoTimePicker import IsoTimePicker


@dataclass
class MetadataSettings:
    set_metadata: bool
    add_metadata: bool
    source: str
    origin: str
    set_parents: bool
    registration_time: str | None


class MetadataSettingsUI:
    def __init__(self):
        with ui.row().classes("w-full items-center gap-4"):
            self.select = ui.select(
                ["Do not adjust Metadata", "Add to Metadata", "Set Metadata"],
                value="Do not adjust Metadata",
            ).props("inline").classes("basis-1/3 py-4")

            self.source_input = ui.input(label="Metadata.Source").classes("basis-1/4 font-bold")
            self.origin_dropdown = ui.select(["Other", "Unknown"], label="Metadata.Origin").classes("basis-1/5 font-bold")
            self.set_parents_switch = ui.switch("set metadata parent", value=False).classes("p-0 m-0")

        self.source_input.set_visibility(False)
        self.origin_dropdown.set_visibility(False)
        self.set_parents_switch.set_visibility(False)

        def on_meta_change(_):
            visible = self.select.value != "Do not adjust Metadata"
            self.source_input.set_visibility(visible)
            self.origin_dropdown.set_visibility(visible)
            self.set_parents_switch.set_visibility(visible)

        self.select.on("update:model-value", on_meta_change)

        with ui.row().classes("w-full items-center gap-4"):
            self.time_select = ui.select(
                ["Do not adjust RegistrationTime", "RegistrationTime by Input"],
                value="Do not adjust RegistrationTime",
            ).props("inline").classes("basis-1/3 py-4")

            self.time_picker = IsoTimePicker(label="RegistrationTime (ISO)")
            self.time_picker.set_visibility(False)

            def on_time_change(_):
                self.time_picker.set_visibility(self.time_select.value != "Do not adjust RegistrationTime")

            self.time_select.on("update:model-value", on_time_change)

    def get_metadata_settings(self) -> MetadataSettings:
        return MetadataSettings(
            set_metadata=self.select.value == "Set Metadata",
            add_metadata=self.select.value == "Add to Metadata",
            source=self.source_input.value,
            origin=self.origin_dropdown.value,
            set_parents=self.set_parents_switch.value,
            registration_time=self.time_picker.value if self.time_select.value == "RegistrationTime by Input" else None,
        )
