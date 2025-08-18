# # qgis_bridge.py
#
# import json
# from PyQt5.QtCore import QUrl, QObject
# from PyQt5.QtWebSockets import QWebSocket
# from qgis.utils import iface
# from qgis.core import QgsVectorLayer, QgsProject, QgsFeatureRequest
#
#
# class NiceGUIBridge(QObject):
#     def __init__(self):
#         super().__init__()
#         self.ws = QWebSocket()
#         self.layer = None
#
#         self.ws.textMessageReceived.connect(self.on_message)
#         self.ws.open(QUrl("ws://localhost:8000/qgis"))
#
#     # ----------------------------
#     # WebSocket handlers
#     # ----------------------------
#     def on_message(self, msg: str):
#         data = json.loads(msg)
#         action = data.get('action')
#
#         if action == 'load_layer':
#             self.load_geojson_layer(data['path'])
#         elif action == 'select_features':
#             self.select_features(data.get('fids', []))
#         elif action == 'zoom_to_feature':
#             self.zoom_to_feature(data.get('fid'))
#         elif action == 'zoom_to_selection':
#             self.zoom_to_selection(data.get('fids', []))
#
#     def send(self, data: dict):
#         """Send JSON to NiceGUI, making sure everything is serializable."""
#         # default=str is a last-resort fallback; we still convert values ourselves
#         self.ws.sendTextMessage(json.dumps(data, default=str))
#
#     # ----------------------------
#     # Layer loading & data shipping
#     # ----------------------------
#     def load_geojson_layer(self, path: str):
#         layer = QgsVectorLayer(path, "Uploaded GeoJSON", "ogr")
#         if not layer or not layer.isValid():
#             iface.messageBar().pushWarning("NiceGUI", "Layer kon niet geladen worden.")
#             return
#
#         QgsProject.instance().addMapLayer(layer)
#         self.layer = layer
#
#         # signals
#         layer.selectionChanged.connect(self.on_qgis_selection)
#
#         # send schema (all attribute fields)
#         columns = [{'name': f.name(), 'label': f.name(), 'field': f.name()} for f in layer.fields()]
#         self.send({'event': 'schema', 'columns': columns})
#
#         # send all features
#         rows = [self._feature_to_row(f) for f in layer.getFeatures()]
#         self.send({'event': 'features', 'rows': rows})
#
#     def _feature_to_row(self, feature):
#         """Return a dict (JSON safe) for a feature row."""
#         def convert(value):
#             if value is None:
#                 return None
#             # Primitive Python types are fine
#             if isinstance(value, (int, float, str, bool)):
#                 return value
#             # Some QGIS/Qt types stringify nicely
#             return str(value)
#
#         row = {field.name(): convert(feature[field.name()]) for field in self.layer.fields()}
#         row['fid'] = int(feature.id())
#         return row
#
#     # ----------------------------
#     # Selection sync
#     # ----------------------------
#     def on_qgis_selection(self):
#         if not self.layer:
#             return
#         selected_ids = self.layer.selectedFeatureIds()
#         self.send({"event": "selection_changed", "selected_ids": list(selected_ids)})
#
#     def select_features(self, fids):
#         if not self.layer:
#             return
#         self.layer.selectByIds(fids or [])
#
#     # ----------------------------
#     # Zoom helpers
#     # ----------------------------
#     def zoom_to_feature(self, fid):
#         if not self.layer or fid is None:
#             return
#         iface.mapCanvas().zoomToFeatureIds(self.layer, [fid])
#
#     def zoom_to_selection(self, fids):
#         if not self.layer:
#             return
#         ids = fids or self.layer.selectedFeatureIds()
#         if not ids:
#             return
#         iface.mapCanvas().zoomToFeatureIds(self.layer, ids)
#
#
# # Instantiate once (e.g. run this file in the QGIS Python console or from your plugin init)
# bridge = NiceGUIBridge()
