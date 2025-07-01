import asyncio
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

from imxInsights.file.singleFileImx.imxSituationEnum import ImxSituationEnum
from nicegui import ui
from openpyxl import load_workbook

from apps.gui.helpers.io import spooled_file_to_temp_file
from insights.diff_and_population import write_diff_output_files
from insights.measure_analyse import generate_measure_excel
from revision.input_validation import validate_process_input
from revision.process_revision import process_imx_revisions
from utils.helpers import load_imxinsights_container_or_file, create_timestamp


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

            ui.label("Optional").classes("italic").visible = True
            with ui.card().classes("w-full") as json_card:
                json_card.visible = True
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

                self.upload_spinner = ui.spinner(size='lg').classes()
                self.upload_spinner.visible = False


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
                self.process_revisions_button = ui.button('Process Revisions', on_click=self._process_revisions)
                self.process_revisions_back = ui.button('Back', on_click=self.stepper.previous).props('flat')
                self.review_spinner = ui.spinner(size='lg').classes()
                self.review_spinner.visible = False

    def _build_check_result_step(self):
        with ui.step('Check Revision Results').classes('font-bold'):
            ui.label('The IMX file has been updated.').classes('text-xl font-semibold text-primary')

            ui.button('Download revision zip', icon='download', on_click=self._on_download_log).props('outline')
            with ui.row():
                self.diff_button = ui.button('Create Diff Report', icon='download', on_click=self._on_generate_diff).props('outline')
                self.diff_spinner = ui.spinner(size='lg').classes()
                self.diff_spinner.visible = False

            with ui.stepper_navigation():
                ui.button('Finish', on_click=self._on_finish).props('flat')
                ui.button('Back', on_click=self.stepper.previous).props('flat')

    def end_and_reset_stepper(self) -> None:
        self.stepper.set_value('Upload Required and Optional Files')
        self.imx_upload_widget.reset()
        self.gr_json_upload_widget.reset()
        self.exclude_context_checkbox = False
        self.gr_json_upload_widget = None
        self.revisions_excel_upload_widget = None
        self.imx_file_path = None
        self.loaded_imx_data = None
        self.measure_excel_file = None
        self.revision_log_zip = None


    def _on_finish(self):
        self.end_and_reset_stepper()
        ui.notify('Process has been reset.', type='positive')

    def _on_imx_upload(self, event):
        ui.notify(f'Uploaded IMX: {event.name}')
        self.analyze_measures_button.enable()
        self.imx_file_path = spooled_file_to_temp_file(event)

    def _on_json_upload(self, event):
        ui.notify(f'Uploaded JSON: {event.name}')
        self.gr_json_file_path = spooled_file_to_temp_file(event)
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

    async def _on_generate_diff(self):
        self.diff_button.disable()
        self.diff_spinner.visible = True
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                output_path = Path(temp_dir) / "output"
                output_path.mkdir(parents=True, exist_ok=True)

                # we should only do input and processed file!!

                await asyncio.to_thread(
                    write_diff_output_files,
                    self.loaded_imx_data.path,
                    self.processed_imx,
                    output_path,
                    ImxSituationEnum.NewSituation,
                    ImxSituationEnum.NewSituation,
                    False,
                    False,
                )

                zip_name = f"diff_{create_timestamp()}.zip"
                zip_path = Path(tempfile.gettempdir()) / zip_name
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for file in output_path.rglob("*"):
                        zipf.write(file, file.relative_to(output_path))

                ui.download(zip_path, filename=zip_name)
                ui.notify("Diff report ready!", type="positive")
                ui.notify("Download started (diff)")
        finally:
            self.diff_spinner.visible = False
            self.diff_button.enable()

    async def run_measure_check(self):
        self.upload_spinner.visible = True
        self.analyze_measures_button.disable()
        try:
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

            if self.gr_json_file_path:
                puics_false = []
                puics_true = []

                with open(self.gr_json_file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    print()
                    for item in data['ContextArea']:
                        puics_false.append(item["Puic"])

                    if self.exclude_context_checkbox.value:
                        for item in data['WorkArea']:
                            puics_true.append(item["Puic"])
                        for item in data['UserArea']:
                            puics_true.append(item["Puic"])

                # process
                wb = load_workbook(self.measure_excel_file)
                ws = wb["revisions"]
                header = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                object_puic_col = header.index("object_puic") + 1
                will_be_processed_col = header.index("will_be_processed") + 1
                revision_reasoning_col = header.index("revision_reasoning") + 1

                for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
                    puic_value = row[object_puic_col - 1].value
                    if puic_value in puics_true:
                        row[will_be_processed_col - 1].value = True
                        row[revision_reasoning_col - 1].value = "Not a ContextArea object"
                    elif puic_value in puics_false:
                        row[will_be_processed_col - 1].value = False
                        row[revision_reasoning_col - 1].value = "ContextArea objects can be corrected"
                wb.save(self.measure_excel_file)

            self.stepper.next()

        finally:
            self.upload_spinner.visible = False
            self.analyze_measures_button.enable()

    async def _process_revisions(self):
        self.review_spinner.visible = True
        self.process_revisions_button.disable()
        self.process_revisions_back.disable()

        try:
            tmpdir = tempfile.TemporaryDirectory()
            out_path = Path(tmpdir.name)

            await asyncio.to_thread(
                process_imx_revisions, self.loaded_imx_data.path, self.revisions_excel_upload_widget, out_path
            )
            path_to_get_from_zip = self.imx_file_path

            zip_path = out_path.with_suffix(".zip")
            shutil.make_archive(zip_path.with_suffix(""), "zip", out_path)

            with zipfile.ZipFile(zip_path) as zf:

                p = Path(path_to_get_from_zip.name)
                internal_name = p.with_name(f"{p.stem}-processed{p.suffix}")

                if internal_name.name in zf.namelist():
                    temp_dir = tempfile.mkdtemp()
                    self._temp_dir = temp_dir  # store so you can clean it up later if needed
                    zf.extract(f"{internal_name}", path=temp_dir)
                    extracted_file = Path(temp_dir) / internal_name
                    self.processed_imx = extracted_file.resolve()
                else:
                    raise FileNotFoundError(f"{internal_name} not found in {zip_path}")

            ui.notify("Revisions applied successfully!", type="positive")
            self.revision_log_zip = zip_path

            self.stepper.next()

        finally:
            self.review_spinner.visible = False
            self.process_revisions_button.enable()
            self.process_revisions_back.enable()

    def _clear_imx_data(self):
        self.analyze_measures_button.disable()
        self.loaded_imx_data = None
        self.measure_excel_file = None

    def _clear_gr_json(self):
        self.gr_json_upload_widget = None



with ui.column().classes("w-full"):
    MeasureCorrectionTool(container=ui.card().classes("p-4 w-full"))

ui.run()
