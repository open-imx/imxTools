

import asyncio
import json
from typing import Optional

from fastapi import WebSocket
from nicegui import app, ui

qgis_ws: Optional[WebSocket] = None
browser_client = None
global_table = None
_silence_ui_selection_event = False  # Prevent loops


@ui.page("/")
def main():
    global browser_client, global_table
    browser_client = ui.context.client

    ui.label("Upload een GeoJSON bestand:")

    # --- Upload GeoJSON ---
    def on_geojson_upload(event):
        file_path = f"/tmp/{event.name}"
        with open(file_path, "wb") as f:
            f.write(event.content.read())
        send_to_qgis({"action": "load_layer", "path": file_path})
        ui.notify("GeoJSON verzonden naar QGIS")

    ui.upload(on_upload=on_geojson_upload).props("accept=.geojson")

    # --- Toolbar button to zoom to selection ---
    def zoom_to_selection():
        if not global_table or not global_table.selected:
            ui.notify("Geen selectie om op in te zoomen", color="orange")
            return
        fids = [row["fid"] for row in global_table.selected]
        send_to_qgis({"action": "zoom_to_selection", "fids": fids})

    ui.button("Zoom naar selectie", on_click=zoom_to_selection)

    # --- Placeholder table ---
    columns = [{"name": "fid", "label": "FID", "field": "fid"}]
    global_table = ui.table(
        columns=columns, rows=[], row_key="fid", selection="multiple"
    ).props("dense")

    # Add context menu
    add_context_menu(global_table)

    # --- Row selection handler ---
    def on_select(_):
        global _silence_ui_selection_event
        if _silence_ui_selection_event:
            return
        fids = [row["fid"] for row in (global_table.selected or [])]
        send_to_qgis({"action": "select_features", "fids": fids})

    global_table.on("selection", on_select)


def build_table(columns):
    """Rebuild the NiceGUI table dynamically based on QGIS schema."""
    global global_table
    if global_table:
        global_table.delete()

    all_columns = [{"name": "fid", "label": "FID", "field": "fid"}] + columns
    global_table = ui.table(
        columns=all_columns, rows=[], row_key="fid", selection="multiple"
    ).props("dense")

    add_context_menu(global_table)

    def on_select(_):
        global _silence_ui_selection_event
        if _silence_ui_selection_event:
            return
        fids = [row["fid"] for row in (global_table.selected or [])]
        send_to_qgis({"action": "select_features", "fids": fids})

    global_table.on("selection", on_select)


def add_context_menu(table):
    """Add a context menu for zooming to feature."""
    menu_row = {"row": None}

    def zoom_to_feature():
        if menu_row["row"]:
            send_to_qgis({"action": "zoom_to_feature", "fid": menu_row["row"]["fid"]})

    context = ui.context_menu()
    ui.menu_item("Zoom naar feature", on_click=zoom_to_feature)

    # Track which row was right-clicked
    table.on("row-contextmenu", lambda e: menu_row.update(row=e.args[0]))
    context.props(f"target=#{table.id}")


def send_to_qgis(payload: dict):
    if qgis_ws is None:
        if browser_client:
            with browser_client:
                ui.notify("QGIS is niet verbonden", color="negative")
        return
    asyncio.create_task(qgis_ws.send_text(json.dumps(payload)))


@app.websocket("/qgis")
async def qgis_socket(ws: WebSocket):
    global qgis_ws, global_table, _silence_ui_selection_event
    await ws.accept()
    qgis_ws = ws

    if browser_client:
        with browser_client:
            ui.notify("QGIS verbonden")

    try:
        while True:
            raw = await ws.receive_text()
            message = json.loads(raw)

            if message.get("event") == "schema":
                if browser_client:
                    with browser_client:
                        build_table(message["columns"])

            if message.get("event") == "features":
                if browser_client and global_table:
                    with browser_client:
                        _silence_ui_selection_event = True
                        try:
                            global_table.rows.clear()
                            global_table.rows.extend(message["rows"])
                            global_table.selected.clear()
                            global_table.update()
                        finally:
                            _silence_ui_selection_event = False

            if message.get("event") == "selection_changed":
                selected_ids = set(message.get("selected_ids", []))
                if browser_client and global_table:
                    with browser_client:
                        _silence_ui_selection_event = True
                        try:
                            global_table.selected.clear()
                            for row in global_table.rows:
                                if row.get("fid") in selected_ids:
                                    global_table.selected.append(row)
                            global_table.update()
                        finally:
                            _silence_ui_selection_event = False

    except Exception:
        qgis_ws = None
        if browser_client:
            with browser_client:
                ui.notify("QGIS verbinding gesloten", color="orange")


ui.run(port=8000, reload=False)