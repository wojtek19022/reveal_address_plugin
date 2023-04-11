from qgis.core import QgsNetworkAccessManager, QgsPointXY
from qgis.gui import QgsMapToolEmitPoint, QgsMapTool, QgsMapCanvas
from qgis.core import QgsCoordinateTransform, QgsCoordinateReferenceSystem
from qgis.PyQt.QtWidgets import QMessageBox, QAction
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply
from qgis.PyQt.QtCore import QUrl
import json

class RevealAddressMapTool(QgsMapToolEmitPoint):
    def __init__(self, canvas):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)

        # Create a coordinate transform object to transform the coordinates from the canvas CRS to WGS 84
        self.coord_transform = QgsCoordinateTransform(canvas.mapSettings().destinationCrs(), QgsCoordinateReferenceSystem(4326), canvas.mapSettings().transformContext())

        # Create a QgsNetworkAccessManager object
        self.nam = QgsNetworkAccessManager.instance()

    def canvasReleaseEvent(self, event):
        # Get the click coordinates
        click_coords = self.toMapCoordinates(event.pos())

        # Transform the coordinates from the canvas CRS to WGS 84
        click_coords_4326 = self.coord_transform.transform(click_coords)

        # Create a GET request to the Nominatim API with the lat and lon of the click
        url = "https://nominatim.openstreetmap.org/reverse?format=json&lat={}&lon={}".format(click_coords_4326.y(), click_coords_4326.x())
        req = QNetworkRequest(QUrl(url))

        # Send the GET request and connect the finished signal to the self.handleResult() method
        reply = self.nam.get(req)
        reply.finished.connect(self.handleResult)

    def handleResult(self):
        reply = self.sender()
        if reply.error() != QNetworkReply.NoError:
            print("Request error: ", reply.error())
            return
        address_json = json.loads(str(reply.readAll(), 'utf-8'))
        if "display_name" in address_json:
            address = address_json["display_name"]
        else:
            address = "No address found"


        # Show the address in a message box
        QMessageBox.information(None, "Address", address)



class RevealAddressPlugin:
    def __init__(self, iface):
        self.map_tool = None
        self.action = None
        self.iface = iface

    def initGui(self):
        # Create action to activate the map tool
        self.action = QAction("Reveal Address", self.iface.mainWindow())
        self.action.triggered.connect(self.activate)

        # Add the action to the toolbar
        self.iface.addToolBarIcon(self.action)

    def activate(self):
        # Create and set the map tool
        self.map_tool = RevealAddressMapTool(self.iface.mapCanvas())
        self.iface.mapCanvas().setMapTool(self.map_tool)

    def unload(self):
        # Remove the map tool and action when the plugin is unloaded
        if self.map_tool:
            self.iface.mapCanvas().unsetMapTool(self.map_tool)
        self.iface.removeToolBarIcon(self.action)
