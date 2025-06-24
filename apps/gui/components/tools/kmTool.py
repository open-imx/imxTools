import asyncio
import re
from nicegui import ui
from nicegui.element import Element
from shapely.geometry import Point

from apps.gui.helpers.io import delete_later


# Dummy resolver for demonstration; replace with your actual resolver logic
async def resolve_km_from_point(point: Point):
    return [
        {"km": round(point.x + point.y, 3), "lint_name": "LINT-123"},
        {"km": round(point.x - point.y, 3), "lint_name": "LINT-456"},
    ]


class KmTool:
    def __init__(self, container: Element):
        with container:
            ui.label("Enter Coordinates:").classes("text-md font-bold")

            with ui.row():
                self.x_input = ui.number(label="X Coordinate")
                self.y_input = ui.number(label="Y Coordinate")

            ui.label("OR input coordinate pair (e.g. 456654.212,644646.222)").classes("text-sm italic text-gray-500")
            self.xy_input = ui.input(label="X,Y Pair").classes("w-full")

            ui.label("OR input GML Point (<gml:coordinates>...</gml:coordinates>)").classes("text-sm italic text-gray-500")
            self.gml_input = ui.input(label="GML Coordinates").classes("w-full")

            ui.button("Resolve KM", on_click=self.run_km_lookup).classes("btn-primary mt-2")
            self.status_label = ui.label().classes("text-sm italic")
            self.result_area = ui.column().classes("mt-4")

    def parse_decimal(self, value: str) -> float:
        value = value.strip()
        if value.count(",") == 1 and value.count(".") == 0:
            return float(value.replace(",", "."))  # European
        if value.count(".") == 1 and value.count(",") == 0:
            return float(value)  # US
        if value.count(",") == 2 and value.count(".") == 0:
            # Possibly 3D coord with commas only
            return float(value.replace(",", ".", 1).replace(",", ""))
        if value.count(",") == 1 and value.count(".") == 1:
            return float(value.replace(".", "").replace(",", "."))
        return float(value)

    def parse_input(self) -> Point | None:
        # 1. Try GML coordinates
        if self.gml_input.value:
            try:
                match = re.search(r"<gml:coordinates>(.*?)</gml:coordinates>", self.gml_input.value)
                if match:
                    coords = match.group(1).strip().split(",")
                    if len(coords) >= 2:
                        x = self.parse_decimal(coords[0])
                        y = self.parse_decimal(coords[1])
                        return Point(x, y)
            except Exception as e:
                ui.notify(f"Invalid GML coordinates: {e}", type="negative")

        # 2. Try "x,y" raw input
        if self.xy_input.value:
            try:
                x_str, y_str = self.xy_input.value.strip().split(",")
                x = self.parse_decimal(x_str)
                y = self.parse_decimal(y_str)
                return Point(x, y)
            except Exception as e:
                ui.notify(f"Invalid coordinate pair: {e}", type="negative")

        # 3. Try separate number fields
        if self.x_input.value is not None and self.y_input.value is not None:
            return Point(self.x_input.value, self.y_input.value)

        return None

    async def run_km_lookup(self):
        self.result_area.clear()
        point = self.parse_input()
        if not point:
            ui.notify("Please provide valid coordinates or GML input", type="warning")
            return

        self.status_label.text = "Resolving KM value..."

        try:
            results = await resolve_km_from_point(point)
            if not results:
                with self.result_area:
                    ui.label("No KM values found.")
                self.status_label.text = "❌ No result found"
            else:
                with self.result_area:
                    for res in results:
                        ui.label(f"KM: {res['km']} | Line: {res['lint_name']}")
                self.status_label.text = "✅ KM values resolved."
                ui.notify("KM values resolved!", type="positive")
        except Exception as e:
            self.status_label.text = "❌ Failed"
            ui.notify(f"Error: {e}", type="negative")
