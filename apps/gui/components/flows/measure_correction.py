import asyncio
import shutil
import tempfile
from pathlib import Path

from imxInsights.file.singleFileImx.imxSituationEnum import ImxSituationEnum
from nicegui import ui

from apps.gui.helpers.io import spooled_file_to_temp_file
from insights.diff_and_population import write_diff_output_files
from insights.measure_analyse import generate_measure_excel
from revision.input_validation import validate_process_input
from revision.process_revision import process_imx_revisions
from utils.helpers import load_imxinsights_container_or_file


class MeasureCorrectionTool:
    def __init__(self, container):
        with container:
            # Upload widgets
            self.imx_upload_widget = None
            self.gr_json_upload_widget = None
            self.revisions_excel_upload_widget = None

            # Input controls
            self.threshold_input_field = None
            self.exclude_context_checkbox = None

            # Control buttons
            self.analyze_measures_button = None

            # Internal state
            self.imx_file_path = None
            self.loaded_imx_data = None
            self.measure_excel_file = None
            self.revision_log_zip = None

            with ui.stepper().props('vertical').classes('w-full') as self.stepper:
                self._build_upload_step()
                self._build_review_step()
                self._build_check_result_step()
                self._build_diff_step()
                # self._build_download_step()

    def _build_upload_step(self):
        with ui.step('Upload Required and Optional Files').classes('font-bold'):
            ui.label("Required:")
            with ui.card().classes("w-full"):
                ui.label('The IMX file you want to analyze and correct.')

                self.imx_upload_widget = ui.upload(
                    label="Upload IMX file.",
                    auto_upload=True,
                    on_upload=self._on_imx_upload,
                ).classes("w-full").style("flex: 1") \
                    .on("removed", lambda _: self._clear_imx_data())

                ui.label('If a single IMX project file is uploaded, only the "NewSituation" will be corrected.') \
                    .classes('text-sm italic text-gray-500')

                self.threshold_input_field = ui.number(label="Threshold (meters)", value=0.015).classes("w-full")

            ui.separator()

            ui.label("Optional").classes("italic").visible = False
            with ui.card().classes("w-full") as json_card:
                json_card.visible = False
                ui.label("The Naiade JSON file to exclude 'context area' objects.")
                ui.label(
                    "When this file is uploaded only 'work area', 'user area', and 'new' objects will be flagged to be corrected."
                ).classes('text-sm italic text-gray-500')

                self.gr_json_upload_widget = ui.upload(
                    label="Upload the JSON file (GR_xxxxx.json)",
                    auto_upload=True,
                    on_upload=self._on_json_upload
                ).classes("w-full").style("flex: 1") \
                    .on("removed", lambda _: self._clear_gr_json())

                self.exclude_context_checkbox = ui.checkbox(
                    "Flag all 'work area', 'user area', and 'new' objects (only excluding 'context area')."
                )
                self.exclude_context_checkbox.disable()

            with ui.stepper_navigation():
                self.analyze_measures_button = ui.button(
                    'Analyse Measures',
                    on_click=self.run_measure_check
                )
                self.analyze_measures_button.disable()

    def _build_review_step(self):
        with ui.step('Review and Flag Revisions').classes('font-bold'):
            ui.label('The uploaded IMX file has been analyzed.').classes('text-xl font-semibold text-primary')
            ui.label('You can now download the analyse (Excel) and review detected discrepancies in the "revisions" sheet.') \
                .classes('text-sm')
            ui.label('If a correction is needed, set the value in the "processing required" column to `True`.') \
                .classes('text-sm')
            ui.label(
                'If you uploaded a GR_xxxxx.json file and enabled "Process all other objects", '
                'this step can be skipped — all files will be processed automatically. However, you can still make adjustments if needed.'
            ).classes('text-sm italic text-gray-500')

            ui.button('Download Revisions File', icon='download', on_click=self._on_download_revisions).props('outline')

            ui.space()

            ui.label('After reviewing and correcting the revisions, upload the file to proceed with processing.')

            self.revisions_excel_upload_widget = ui.upload(
                label="Upload the flagged revisions excel file",
                auto_upload=True,
                on_upload=self._on_revision_upload
            ).classes("w-full").style("flex: 1")

            with ui.stepper_navigation():
                ui.button('Process Revisions', on_click=self._process_revisions)
                ui.button('Back', on_click=self.stepper.previous).props('flat')

    def _build_check_result_step(self):
        with ui.step('Check Revision Results').classes('font-bold'):
            ui.label('The IMX file has been updated.').classes('text-xl font-semibold text-primary')

            ui.button('Download revision log', icon='download', on_click=self._on_download_log).props('outline')

            ui.label('Check if all revisions have been processed. If not, you can make adjustments and reprocess by going one step back.') \
                .classes('text-sm')

            with ui.stepper_navigation():
                ui.button('Next', on_click=self.stepper.next)
                ui.button('Back', on_click=self.stepper.previous).props('flat')

    def _build_diff_step(self):
        with ui.step('Optional: generate a diff report to review the changes.').classes('font-bold'):
            ui.button('Create Diff Report', icon='download', on_click=self._on_generate_diff).props('outline')

            with ui.stepper_navigation():
                ui.button('Next', on_click=self.stepper.next)
                ui.button('Back', on_click=self.stepper.previous).props('flat')

    def _build_download_step(self):
        with ui.step('Download results').classes('font-bold'):
            ui.label('The ZIP file includes: measure analysis, revision log, revised IMX file, and optionally the diff report.')

            with ui.stepper_navigation():
                ui.button('Done', on_click=lambda: ui.notify('Yay!', type='positive'))
                ui.button('Back', on_click=self.stepper.previous).props('flat')

    def _on_imx_upload(self, event):
        ui.notify(f'Uploaded IMX: {event.name}')
        self.analyze_measures_button.enable()
        self.imx_file_path = spooled_file_to_temp_file(event)

    def _on_json_upload(self, event):
        ui.notify(f'Uploaded JSON: {event.name}')
        self.exclude_context_checkbox.enable()

    def _on_revision_upload(self, event):
        self.revisions_excel_upload_widget = spooled_file_to_temp_file(event)
        ui.notify(f'Uploaded revisions Excel: {event.name}')

    def _on_download_revisions(self):
        ui.download(self.measure_excel_file, filename=self.measure_excel_file.name)
        ui.notify("Download started (revisions)")

    def _on_download_log(self):
        ui.download(self.revision_log_zip, filename=self.revision_log_zip.name)
        ui.notify("Download started (revision log)")

    def _on_generate_diff(self):
        # todo
        ui.notify("Download started (diff)")

    async def run_measure_check(self):
        threshold = self.threshold_input_field.value

        self.loaded_imx_data = await asyncio.to_thread(
            load_imxinsights_container_or_file, self.imx_file_path, ImxSituationEnum.NewSituation
        )
        self.measure_excel_file = (
            Path(tempfile.gettempdir()) / f"measure_output_{self.imx_file_path.stem}.xlsx"
        )
        if self.measure_excel_file.exists():
            self.measure_excel_file.unlink()

        await asyncio.to_thread(
            generate_measure_excel,
            self.loaded_imx_data,
            self.measure_excel_file,
            threshold if threshold else None,
        )
        self.stepper.next()

    async def _process_revisions(self):
        tmpdir = tempfile.TemporaryDirectory()
        out_path = Path(tmpdir.name)

        await asyncio.to_thread(
            process_imx_revisions, self.loaded_imx_data.path, self.revisions_excel_upload_widget, out_path
        )

        zip_path = out_path.with_suffix(".zip")
        shutil.make_archive(zip_path.with_suffix(""), "zip", out_path)
        ui.notify("Revisions applied successfully!", type="positive")
        self.revision_log_zip = zip_path

        self.stepper.next()

    def _clear_imx_data(self):
        self.analyze_measures_button.disable()
        self.loaded_imx_data = None
        self.measure_excel_file = None

    def _clear_gr_json(self):
        self.gr_json_upload_widget = None



with ui.column().classes("w-full"):
    MeasureCorrectionTool(container=ui.card().classes("p-4 w-full"))
ui.run()
