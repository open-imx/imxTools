from nicegui import ui

from apps.gui.components.widgets.imxUpload import ImxUpload

with ui.stepper().props('vertical').classes('w-full') as stepper:
    with ui.step('Input'):
        ImxUpload(
            "Upload an IMX file to fix measure discrepancies", on_change=lambda e: ui.notify(f'Uploaded: {e.name}')
        )
        ui.separator()


        with ui.card().classes("w-full"):
            ui.label('Optional').classes("font-bold")
            ui.label("Upload the Naiade GR 'werkgebieden' JSON file to flag 'context area' objects that should be excluded from processing.")
            with ui.card_section().classes("w-full"):

                uploaded_json = ui.upload(label='Naiade Geoscope JSON',
                                          auto_upload=True,
                                          on_upload=lambda e: ui.notify(f'Uploaded: {e.name}')).classes("w-full").style("flex: 1")

                flag_all_checkbox = ui.checkbox('Process all objects except those in the "context area"')

        with ui.stepper_navigation():
            ui.button('Analyse', on_click=stepper.next)
        ui.label('Running and spinning')

    with ui.step('Flag Analyse'):

        ui.label('Analyse download')
        ui.label('If geoscope context is False and all other are True, this step can be skipped.')
        ui.label('Download analyse file and set processing states to true if correction is needed')

        with ui.stepper_navigation():
            ui.button('Next', on_click=stepper.next)
            ui.button('Back', on_click=stepper.previous).props('flat')

    with ui.step('Revision processing'):
        ui.label('Apply revisions')
        ui.label('Create diff')
        ui.label('Zip content (measure analyse, revision log excel, revision imx, diff excel)')
        ui.label('Download zip')

        with ui.stepper_navigation():
            ui.button('Done', on_click=lambda: ui.notify('Yay!', type='positive'))
            ui.button('Back', on_click=stepper.previous).props('flat')

ui.run()
