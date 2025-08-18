# import asyncio
# import json
# from typing import Optional
#
# from fastapi import WebSocket
# from nicegui import app, ui, events
#
# qgis_ws: Optional[WebSocket] = None
# browser_client = None
# global_table = None
# _silence_ui_selection_event = False  # Prevent loops
# current_selected_ids: set[int] = set()  # Track selection state
#
#
# @ui.page("/")
# def main():
#     global browser_client, global_table
#     browser_client = ui.context.client
#
#     ui.label("Upload een GeoJSON bestand:")
#
#     # --- Upload GeoJSON ---
#     def on_geojson_upload(event):
#         file_path = f"/tmp/{event.name}"
#         with open(file_path, "wb") as f:
#             f.write(event.content.read())
#         send_to_qgis({"action": "load_layer", "path": file_path})
#         ui.notify("GeoJSON verzonden naar QGIS")
#
#     ui.upload(on_upload=on_geojson_upload).props("accept=.geojson")
#
#     # --- Zoom to selected features ---
#     def zoom_to_selection():
#         if not global_table:
#             ui.notify("Tabel nog niet beschikbaar", color="orange")
#             return
#
#         selected_rows = [
#             row for row in global_table.options.get("rowData", [])
#             if row.get("_selected")
#         ]
#         if not selected_rows:
#             ui.notify("Geen selectie om op in te zoomen", color="orange")
#             return
#         fids = [row["fid"] for row in selected_rows]
#         send_to_qgis({"action": "zoom_to_selection", "fids": fids})
#
#     ui.button("Zoom naar selectie", on_click=zoom_to_selection)
#
#     # --- Initial empty table ---
#     create_aggrid(columns=[{"label": "FID", "field": "fid"}])
#
#
# def create_aggrid(columns):
#     global global_table
#
#     column_defs = [{"headerName": "FID", "field": "fid", "checkboxSelection": True}]
#     column_defs += [
#         {"headerName": col["label"], "field": col["field"]}
#         for col in columns if col["field"] != "fid"
#     ]
#
#     if global_table:
#         global_table.delete()
#
#     global_table = ui.aggrid({
#         "columnDefs": column_defs,
#         "rowData": [],
#         "rowSelection": "multiple",
#         "defaultColDef": {"resizable": True, "sortable": True, "filter": True},
#         "suppressRowClickSelection": True,
#         "getRowNodeId": "data => data.fid",
#     }).classes("h-80")
#
#     add_context_menu(global_table)
#
#     async def on_select(e: events.GenericEventArguments):
#         global _silence_ui_selection_event, current_selected_ids
#         if _silence_ui_selection_event:
#             return
#
#         rows = await e.sender.get_selected_rows()
#         new_selected_ids = {row["fid"] for row in rows}
#
#         if new_selected_ids != current_selected_ids:
#             current_selected_ids = new_selected_ids
#             send_to_qgis({"action": "select_features", "fids": list(new_selected_ids)})
#
#     global_table.on("selectionChanged", on_select)
#
#
# def add_context_menu(grid):
#     menu_row = {"row": None}
#
#     def zoom_to_feature():
#         if menu_row["row"]:
#             send_to_qgis({"action": "zoom_to_feature", "fid": menu_row["row"]["fid"]})
#
#     context = ui.context_menu()
#     ui.menu_item("Zoom naar feature", on_click=zoom_to_feature)
#
#     def on_cell_context_menu(e: events.GenericEventArguments):
#         menu_row["row"] = e.args.get("data")
#
#     grid.on("cellContextMenu", on_cell_context_menu)
#
#
# def build_table(columns):
#     # Add extra columns from data rows if not already in the schema
#     defined_fields = {col["field"] for col in columns}
#     extra_fields = set()
#
#     if global_table:
#         for row in global_table.options.get("rowData", []):
#             extra_fields.update(row.keys())
#
#     for field in extra_fields - defined_fields - {"_selected"}:
#         columns.append({"label": field.capitalize(), "field": field})
#
#     create_aggrid(columns)
#
#
# def send_to_qgis(payload: dict):
#     if qgis_ws is None:
#         if browser_client:
#             with browser_client:
#                 ui.notify("QGIS is niet verbonden", color="negative")
#         return
#
#     async def safe_send():
#         global qgis_ws
#         try:
#             await qgis_ws.send_text(json.dumps(payload))
#         except Exception as e:
#             qgis_ws = None
#             if browser_client:
#                 with browser_client:
#                     ui.notify(f"Verbinding met QGIS is verbroken: {e}", color="negative")
#
#     asyncio.create_task(safe_send())
#
#
# @app.websocket("/qgis")
# async def qgis_socket(ws: WebSocket):
#     global qgis_ws, global_table, _silence_ui_selection_event, current_selected_ids
#     await ws.accept()
#     qgis_ws = ws
#
#     if browser_client:
#         with browser_client:
#             ui.notify("QGIS verbonden")
#
#     try:
#         while True:
#             raw = await ws.receive_text()
#             message = json.loads(raw)
#
#             if message.get("event") == "schema":
#                 if browser_client:
#                     with browser_client:
#                         build_table(message["columns"])
#
#             elif message.get("event") == "features":
#                 if browser_client and global_table:
#                     with browser_client:
#                         _silence_ui_selection_event = True
#                         try:
#                             for row in message["rows"]:
#                                 row["_selected"] = False
#                             global_table.options["rowData"] = message["rows"]
#                             global_table.update()
#                             global_table.run_grid_method("sizeColumnsToFit")
#                         finally:
#                             _silence_ui_selection_event = False
#
#             elif message.get("event") == "selection_changed":
#
#
#                 # TODO: we can use selected IDS,
#                 #  we should use selected puics i guess.... looks like fid is not the selected rows but indexes!!!!
#
#                 selected_ids = set(message.get("selected_ids", []))
#                 if browser_client and global_table:
#                     row_data = global_table.options.get("rowData", [])
#                     selected_puics = [
#                         row.get("@puic") for i, row in enumerate(row_data)
#                         if i in selected_ids and "@puic" in row
#                     ]
#
#                     with browser_client:
#                         _silence_ui_selection_event = True
#                         try:
#                             current_puics = {
#                                 row["@puic"]
#                                 for row in global_table.options.get("rowData", [])
#                                 if row.get("_selected")
#                             }
#                             if selected_puics != current_puics:
#                                 current_selected_ids = selected_ids
#                                 for row in row_data:
#                                     row["_selected"] = row["fid"] in selected_ids
#
#                                 sorted_data = sorted(row_data, key=lambda x: not x.get("_selected", False))
#                                 global_table.options["rowData"] = sorted_data
#                                 global_table.update()
#
#                                 for fid in selected_ids:
#                                     global_table.run_row_method(fid, "setSelected", True)
#                         finally:
#                             _silence_ui_selection_event = False
#
#     except Exception:
#         qgis_ws = None
#         if browser_client:
#             with browser_client:
#                 ui.notify("QGIS verbinding gesloten", color="orange")
#
#
# ui.run(port=8000, reload=False)
