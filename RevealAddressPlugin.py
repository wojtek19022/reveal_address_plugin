# Import necessary modules from QGIS
from qgis.core import QgsPointXY
from qgis.gui import QgsMapToolEmitPoint, QgsMapTool,  QgsMapCanvas
from qgis.core import QgsCoordinateTransform, QgsCoordinateReferenceSystem
# Import QMessageBox
from PyQt5.QtWidgets import QMessageBox
# Import the Nominatim module for reverse geocoding
import requests

# Import the QAction class from the QtWidgets module
from PyQt5.QtWidgets import QAction

class RevealAddressMapTool(QgsMapToolEmitPoint):
    def __init__(self, canvas):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)

        # Create a coordinate transform object
        self.coord_transform = QgsCoordinateTransform(canvas.mapSettings().destinationCrs(), QgsCoordinateReferenceSystem(4326), canvas.mapSettings().transformContext())

    def canvasReleaseEvent(self, event):
        # Get the click coordinates
        click_coords = self.toMapCoordinates(event.pos())

        # Transform the coordinates from the canvas CRS to WGS 84
        click_coords_4326 = self.coord_transform.transform(click_coords)

        # Use requests to make a GET request to the Nominatim API
        result = requests.get("https://nominatim.openstreetmap.org/reverse", params={
            "format": "json",
            "lat": click_coords_4326.y(),
            "lon": click_coords_4326.x()
        })

        # Get the address from the result
        address_json = result.json()
        if "display_name" in address_json:
            address = address_json["display_name"]
        else:
            address = "No address found"

        # Show the address in a message box
        QMessageBox.information(None, "Address", address)



class RevealAddressPlugin:
    def __init__(self, iface):
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
        self.iface.mapCanvas().unsetMapTool(self.map_tool)
        self.iface.removeToolBarIcon(self.action)
