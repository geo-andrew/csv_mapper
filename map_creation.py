import os # library used to manipulate path names and directories
import glob # allows for all files in a certain directory to be targeted
import fnmatch
from qgis.core import (QgsFeature, QgsField, QgsFields,
                       QgsGeometry, QgsPoint, QgsVectorFileWriter)


project = QgsProject.instance()

prehistoric_data= "file:///C:/Users/ADMIN/Desktop/Data/Site_type/prehistoric_data.csv"
               
archaeo_search_terms = ['Broch', 'Bank', 'Building', 'Burnt Mound', 'Dyke', 'Cairnfield', 'Clearence Cairn', 
'Chambered Cairn', 'Kerb Cairn', 'Burial Cairn', 'Dun', 'Enclosure', 'Field Boundary', 'Field System', 
'House', 'Hut Circle', 'Lithic Working Site', 'Long Cairn', 'Quarry', 'Ritual Building', 'Souterrain', 
'Standing Stone', 'Stone Heap', 'Stone Row', 'Stone Setting', 'Settlement (Prehistoric)', 
'Settlement (Neolithic)', 'Settlement (Bronze Age)', 'Settlement (Iron Age)', 'Wall']

layer_colours = [ '#1f78b4', '#a6cee3', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c', '#fdbf6f', '#ff7f00', 
'#00fffb', '#f7ff00', '#ff00d9', '#4000ff', '#ff0c00', '#713a48', '#71ee48', '#cdee48', '#ee48c2', '#ee4803', 
'#e3bbee', '#3a7141', '#82a11c', '#82a1f1', '#f19e82', '#0928f1', '#c44f6a', '#4fc461', '#08160a', '#b430c2', 
'#9bc230', '#ff9a3c']

layer_shapes = [ 'circle', 'square', 'triangle', 'diamond', 'circle', 'square', 'triangle', 'diamond', 'circle', 
'square', 'triangle', 'diamond', 'circle', 'square', 'triangle', 'diamond', 'circle', 'square', 'triangle', 'diamond', 
'circle', 'square', 'triangle', 'diamond', 'circle', 'square', 'triangle', 'diamond', 'circle', 'square']

# this line purges the layers panel to stop it becoming clutered
project.removeAllMapLayers()

# this empties the directory geoprogramming, just for housekeeping
files = glob.glob('C:/Users/ADMIN/Desktop/Data/geoprogramming/*')
for f in files:
    os.remove(f)

# the outline of the island the points fall within, the context for the map (this could be a raster)
contour_map = QgsVectorLayer("C:/Users/ADMIN/Desktop/Data/Site_type/shapefiles/Unst50metre.shp", "Unst contours", "ogr")
# this routine merely vaidates the shp file entry
if not unst_contour_map.isValid():
    print("Layer failed to load!")

reproj_contour_map = processing.run('native:reprojectlayer', {'INPUT': contour_map,
    'TARGET_CRS': 'EPSG:4326',
    'OUTPUT': 'memory:'})['OUTPUT']

# these next two blocks of code rename the output layers in the table of contents
project.addMapLayer(reproj_contour_map)
to_be_renamed = project.mapLayersByName('output')[0]
to_be_renamed.setName('Contour_map')

# this line sets the uri, the information about the crs and encoding
uri = prehistoric_data + "?encoding=%s&delimiter=%s&xField=%s&yField=%s&crs=%s" % ("UTF-8",",", "SITE EASTING", "SITE NORTHING","epsg:27700")
pre_hist_data = QgsVectorLayer(uri,'Points', 'delimitedtext')
print(pre_hist_data.isValid())
# this adds the layer to the map, for some reason it has to be added, even though it is an intermediate step, it is deleated later
pre_hist_data = iface.addVectorLayer(uri,'Brochs','delimitedtext')

# this procecing script reprojects the layer into epsg 4326, now all layers are in the same projection
reproj_pre_hist_data = processing.run('native:reprojectlayer', {'INPUT': pre_hist_data,
    'TARGET_CRS': 'EPSG:4326',
    'OUTPUT': 'memory:'})['OUTPUT']
    

# the reprojection is added
project.addMapLayer(reproj_pre_hist_data)
# the reprojection is renamed
to_be_renamed = project.mapLayersByName('output')[0]
to_be_renamed.setName('Prehistoric_data')

#just to check what is in the table of contents, the layer names are printed to the console
layers_names = []
for layer in QgsProject.instance().mapLayers().values():
    layers_names.append(layer.name())

print("layers TOC = {}".format(layers_names))

# the target layer that will be divided, or selected, by the search terms is defined
layer = reproj_pre_hist_data

for index, item in enumerate (archaeo_search_terms):
    
    # the LIKE operator acts like the word contains, the % signs are wildcards so allow the term to appear anywhere
    # by using formatting a variable can be used as the search term
    layer.selectByExpression('"SITE TYPE" LIKE \'%{}%\''.format(item),QgsVectorLayer.SetSelection)

    selection = layer.selectedFeatures()

    #if there is any information in the selection, create a geopackage and write the vector to the map
    if (len(selection) > 0):
        file_name = 'C:/Users/ADMIN/Desktop/Data/geoprogramming/{}.gpkg'.format(item)
        writer = QgsVectorFileWriter.writeAsVectorFormat(layer, file_name, 'utf-8', driverName = 'GPKG', onlySelected = True)
        
        selected_layer = iface.addVectorLayer(file_name, item, 'ogr')
        
        # these two lines take the symbol and colour at the relevant spot and applies it to the layer
        symbol = QgsMarkerSymbol.createSimple({'name': layer_shapes[index], 'color': layer_colours[index]})
        selected_layer.renderer().setSymbol(symbol)
        # make the change actual for the layer
        selected_layer.triggerRepaint()
        
        #this line updates the layer tree symbology as each layer's symbols are changed
        iface.layerTreeView().refreshLayerSymbology( iface.activeLayer().id() )
        
        project.addMapLayer(selected_layer)
        del(writer)

QCoreApplication.processEvents()

# these lines clear the table of contents of unnecessary layers
root = project.layerTreeRoot()

root.removeLayer(reproj_pre_hist_data)
root.removeLayer(pre_hist_data)


##############################################
#this part of the script creates a map from the results of the foregoing part of the script
#############################################################

project = QgsProject.instance()                                  
manager = project.layoutManager()
layout = QgsPrintLayout(project)                   
layoutName = "PrintLayout"
layout.setName('Prehistoric archaeology on Unst, Shetland, Scotland') 

layouts_list = manager.printLayouts()

for layout in layouts_list:
    if layout.name() == layoutName:
        manager.removeLayout(layout)

layout = QgsPrintLayout(project)
layout.initializeDefaults()                 #create default map canvas
layout.setName(layoutName)
manager.addLayout(layout)



# Map
#   Defaults of `A4`, `Landscape`, & `LayoutMillimeters` are 
#   due to `layout.initializeDefaults()`
map = QgsLayoutItemMap(layout)
map.setRect(QRectF(20, 20, 200, 100))  # The Rectangle will be overridden below


# sets the extent to the extent of the named layer
map.setExtent(reproj_contour_map.extent())


layout.addLayoutItem(map)

#Move & Resize
map.attemptMove(QgsLayoutPoint(15, 35, QgsUnitTypes.LayoutMillimeters))
map.attemptResize(QgsLayoutSize(200, 160, QgsUnitTypes.LayoutMillimeters))

#Checks layer tree objects and stores them in a list. This includes csv tables
checked_layers = [layer.name() for layer in QgsProject().instance().layerTreeRoot().children() if layer.isVisible()]
print(f"Adding {checked_layers} to legend." )
#get map layer objects of checked layers by matching their names and store those in a list
layersToAdd = [layer for layer in QgsProject().instance().mapLayers().values() if layer.name() in checked_layers]
root = QgsLayerTree()
for layer in layersToAdd:
    #add layer objects to the layer tree
    root.addLayer(layer)



legend = QgsLayoutItemLegend(layout)
legend.model().setRootGroup(root)
layout.addLayoutItem(legend)
legend.attemptMove(QgsLayoutPoint(240, 35, QgsUnitTypes.LayoutMillimeters))

title = QgsLayoutItemLabel(layout)
title.setText("Prehistoric archaeological sites on Unst, Shetland, Scotland")
title.setFont(QFont("Arial", 28))
title.adjustSizeToText()
layout.addLayoutItem(title)
title.attemptMove(QgsLayoutPoint(10, 4, QgsUnitTypes.LayoutMillimeters))

subtitle = QgsLayoutItemLabel(layout)
subtitle.setText("Archaeological data courtesy of the CANMORE repository")
subtitle.setFont(QFont("Arial", 17))
subtitle.adjustSizeToText()
layout.addLayoutItem(subtitle)
subtitle.attemptMove(QgsLayoutPoint(11, 20, QgsUnitTypes.LayoutMillimeters))   #allows moving text box

credit_text = QgsLayoutItemLabel(layout)
credit_text.setText("Map created by A. Prentice 2019")
credit_text.setFont(QFont("Arial", 10))
credit_text.adjustSizeToText()
layout.addLayoutItem(credit_text)
credit_text.attemptMove(QgsLayoutPoint(225, 185, QgsUnitTypes.LayoutMillimeters))

# add scalebar
scaleBar = QgsLayoutItemScaleBar(layout)
scaleBar.setLinkedMap(map)
scaleBar.applyDefaultSettings()
scaleBar.applyDefaultSize()
# scaleBar.setStyle('Line Ticks Down') 
scaleBar.setNumberOfSegmentsLeft(0)
scaleBar.setNumberOfSegments (3)

scaleBar.setPos(225, 165)
scaleBar.update()

layout.addItem(scaleBar)

#Add north arrow
arrow = QgsLayoutItemPicture(layout)
arrow.setPicturePath("C:/OSGeo4W64/apps/qgis/svg/arrows/NorthArrow_04.svg")
arrow.setLinkedMap(map)
arrow.attemptMove(QgsLayoutPoint(225, 135, QgsUnitTypes.LayoutMillimeters))
arrow.attemptResize(QgsLayoutSize(20, 20, QgsUnitTypes.LayoutMillimeters))
layout.addItem(arrow)

QgsLayoutExporter(layout).exportToPdf( 'C:/Users/ADMIN/Desktop/Data/geoprogramming/archaeo_sites.pdf', QgsLayoutExporter.PdfExportSettings() )
# this exports the map as an image
QgsLayoutExporter(layout).exportToImage('C:/Users/ADMIN/Desktop/Data/geoprogramming/archaeo_sites.png', QgsLayoutExporter.ImageExportSettings())