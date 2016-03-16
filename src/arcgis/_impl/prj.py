import arcgis.gis
import json

import os
import tempfile
import collections
from contextlib import contextmanager

import arcpy
from arcpy.pdfdocument import PDFDocument, PDFDocumentOpen, PDFDocumentCreate

"""
The arcgis.prj module provides functionality for manipulating the contents of 
ArcGIS Pro projects(.aprx) and layer files(.lyr or .lyrx). It also provides functions 
to automate exporting and printing. This module can be used to automate map production
and is required to build complete map books because it includes functions to export to,
create, and manage PDF documents.
"""

def _lazy_property(fn):
    '''Decorator that makes a property lazy-evaluated.
    '''
    # http://stevenloria.com/lazy-evaluated-properties-in-python/
    attr_name = '_lazy_' + fn.__name__

    @property
    def _lazy_property(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return _lazy_property

# pylint: disable=fixme, line-too-long
class ArcGISProject(object):
    """
    Provides access to ArcGIS Pro project methods and properties. A reference to this object
    is essential for most map scripting operations.
    """
    def __init__(self, portal, project_path, project_item):
        """
        Provides a reference to an ArcGIS project (.aprx)
        """
        self._portal = portal
        self.project_path = project_path
        self.project_item = project_item
        if self.project_item is not None:
            # download the project and save it at project_path
            file_downloaded = self.project_item.download(project_path)
            ppkx_name = os.path.splitext(os.path.basename(file_downloaded))[0] 

            project_path = os.path.join(project_path, ppkx_name)
            # unpack it
            arcpy.ExtractPackage_management(file_downloaded, project_path)

            aprxfiles = [os.path.join(d, x)
                for d, dirs, files in os.walk(project_path)
                for x in files if x.endswith(".aprx")]
            
            self.project_path = aprxfiles[0]
            # print("aprx_path: " + aprxfiles[0]) 
        self.arcpyProject = arcpy.mp.ArcGISProject(self.project_path)
        self.date_saved = self.arcpyProject.dateSaved
        self.default_geodatabase = self.arcpyProject.defaultGeodatabase
        self.default_toolbox = self.arcpyProject.defaultToolbox
        self.file_path = self.arcpyProject.filePath
        self.home_folder = self.arcpyProject.homeFolder
        self.version = self.arcpyProject.version

    @_lazy_property
    def layouts(self):
        """
           Returns a Python list of Layout objects in an ArcGIS project.
        """
        return [Layout(lyt) for lyt in self.arcpyProject.listLayouts("*")] 

    @_lazy_property
    def maps(self):
        """Returns a Python list of Map objects in an ArcGIS project
        """
        return [Map(map) for map in self.arcpyProject.listMaps("*")] 
   
    @_lazy_property
    def broken_data_sources(self):
        """Returns a Python list of Layer or Table objects that have broken
           connections to their original source data for all maps in a project.
        """
        brokenDataSources = []
        _arcpyBrokenDataSources = self.arcpyProject.listBrokenDataSources()
        for brokenDS in _arcpyBrokenDataSources:
            if isinstance(brokenDataSources, arcpy.mp.Table):
                brokenDataSources.append(Table(brokenDS))
            elif isinstance(brokenDataSources, arcpy.mp.Layer):
                brokenDataSources.append(Layer(brokenDS))
            else:
                brokenDataSources.append(brokenDS)
        return brokenDataSources

    def import_document(self, document_path, include_layout=True):
        """ArcGISProject.import_document(document_path, {include_layout})

           Imports map ( .mxd ), globe ( .3dd ) and scene ( .sxd ) documents
           into an ArcGIS Pro project.

             document_path(String):
           A string that includes the system path and name of a ( .mxd , .3dd ,
           or .sxd ) document  to import.

             include_layout{Boolean}:
           A Boolean indicating if the layout from a map document ( .mxd ) is
           imported.  If  set to True , the layout and all data frames are
           imported. If set to False , only the data frames are imported.  This
           parameter is ignored for globe ( .3dd ) and scene ( .sxd ) documents."""
        return self.arcpyProject.importDocument(document_path, include_layout)

    def save(self, file_name=None):
        """ArcGISProject.save({fileName})
           Saves changes to an ArcGISProject ( .aprx ) or saves to a new file path or name

             file_name(String):
           Optional. A string used to save an ArcGISProject ( .aprx ) to a new file path
           or file name.
        """
        if file_name is not None:
            return self.arcpyProject.saveACopy(file_name)
        else:
            return self.arcpyProject.save()

    def update_connection_properties(self, current_connection_info, new_connection_info, auto_update_joins_and_relates=True, validate=True):
        """ArcGISProject.update_connection_properties(current_connection_info,
           new_connection_info, {auto_update_joins_and_relates}, {validate})

           Replaces connection properties using a dictionary or a path to a
           workspace.

             current_connection_info(String):
           A string that represents the workspace path or a Python dictionary
           that contains connection properties to the source you want to update.

             new_connection_info(String):
           A string that represents the workspace path or a Python dictionary
           that contains connection properties with the new source information.

             auto_update_joins_and_relates{Boolean}:
           If  set to True , the updateConnectionProperties method will also
           update the connections for associated joins or relates.

             validate{Boolean}:
           If  set to True , the connection properties will only be updated if
           the new_connection_info value is a valid connection.  If it is not
           valid, the connection will not be replaced.   If set to False , the
           method will set all connections to match the new_connection_info ,
           regardless of a valid match.  In this case, if a match does not
           exist, then the data sources would be broken.
        """
        return self.arcpyProject.updateConnectionProperties(current_connection_info, new_connection_info, auto_update_joins_and_relates, validate)
                
    #def _repr_html_(self):
    #    return '<iframe width=810 height=600 src="'+"http://developers.arcgis.com/javascript/samples/mobile_arcgis/?webmap="+self.item.itemid+'"/>'

    def __str__(self):
        return "ArcGIS Pro project at " + self.project_path


class Layout(object):
    """
    The Layout object references a single-page layout in an ArcGIS Pro
    project ( .aprx ).  It provides access to page elements and methods 
    to export the layout to several formats
    """
    def __init__(self, arcpyLayout):
        self._arcpyLayout = arcpyLayout
        self.name = arcpyLayout.name
        self.page_height = arcpyLayout.pageHeight
        self.page_units = arcpyLayout.pageUnits
        self.page_width = arcpyLayout.pageWidth

    def export(self, out_file, resoultion=96):
        """Layout.export(out_file, {resolution})

           Exports the page layout to the output file. The format is determined by 
           the filename extension. Supported formats are:
           Microsoft Windows Bitmap format (BMP)
           Enhanced Metafile (EMF)
           Encapsulated PostScript (EPS)
           Graphic Interchange format (GIF)
           Joint Photographic Experts Group format (JPEG)
           Portable Network Graphics format (PNG)
           Scalable Vector Graphics format (SVG)
           Truevision Graphics Adapter format (TGA)
           Tagged Image File Format (TIFF)

             out_file(String):
           A string that represents the path and file name for the output export
           file.

             resolution{Integer}:
           A number that defines the resolution of the export file in dots per
           inch (dpi).
        """
        extension = os.path.splitext(filename)[1][1:].strip().lower()
        options = {
           "bmp" : self._arcpyLayout.exportToBMP,
           "emf" : self._arcpyLayout.exportToEMF,
           "eps" : self._arcpyLayout.exportToEPS,
           "gif ": self._arcpyLayout.exportToGIF,
           "jpg" : self._arcpyLayout.exportToJPEG,
           "jpeg": self._arcpyLayout.exportToJPEG,
           "png" : self._arcpyLayout.exportToPNG,
           "svg" : self._arcpyLayout.exportToSVG,
           "tga" : self._arcpyLayout.exportToTGA,
           "tiff": self._arcpyLayout.exportToTIFF,
           "tif" : self._arcpyLayout.exportToTIFF
        }
        return options[extension](out_file, resoultion)

    def export_PDF(self, out_pdf, resolution=300, image_quality='BEST', compress_vector_graphics=True, image_compression='ADAPTIVE', embed_fonts=True, layers_attributes='LAYERS_ONLY', georef_info=True, jpeg_compression_quality=80, clip_to_elements=False):
        """Layout.export_PDF(out_pdf, {resolution}, {image_quality},
           {compress_vector_graphics}, {image_compression}, {embed_fonts},
           {layers_attributes}, {georef_info}, {jpeg_compression_quality},
           clip_to_elements)

           Exports the page layout  to the Portable Document Format (PDF).

             out_pdf(String):
           A string that represents the path and file name for the output export
           file.

             resolution{Integer}:
           A number that defines the resolution of the export file in dots per
           inch (DPI).

             image_quality{String}:
           A string that defines output image quality, the draw resolution of
           map layers that draw as rasters.

            * BEST:  An output image quality resample ratio of 1.

            * BETTER:  An output image quality resample ratio of 2.

            * NORMAL:  An output image quality resample ratio of 3.

            * FASTER:  An output image quality resample ratio of 4.

            * FASTEST:  An output image quality resample ratio of 5.

             compress_vector_graphics{Boolean}:
           A Boolean that controls compression of vector and text portions of
           the output file. Image compression is defined separately.

             image_compression{String}:
           A string that defines the compression scheme used to compress image
           or raster data in the output file.

            * ADAPTIVE:   Automatically selects the best compression type for
            each image on the page.   JPEG will be used for large images with
            many unique colors.  DEFLATE will be used for all other images.

            * DEFLATE:   A lossless data compression.

            * JPEG:   A lossy data compression.

            * LZW:   Lempel-Ziv-Welch, a lossless data compression.

            * NONE:   Compression is not applied.

            * RLE:   Run-length encoded compression.

             embed_fonts{Boolean}:
           A Boolean that controls the embedding of fonts in the export file.
           Font embedding allows text and character markers to be displayed
           correctly when the document is viewed on a computer that does not
           have the necessary fonts installed.

             layers_attributes{String}:
           A string that controls inclusion of PDF layer and PDF object data
           (attributes) in the export file.

            * LAYERS_ONLY:  Export PDF layers only

            * LAYERS_AND_ATTRIBUTES:  Export PDF layers and feature attributes

            * NONE:  None

             georef_info{Boolean}:
           A Boolean that enables the export of coordinate system information
           for each data frame into the output PDF file.

             jpeg_compression_quality{Integer}:
           A number that controls compression quality value when
           image_compression is set to ADAPTIVE or JPEG . The valid range is 1
           to 100.    A jpeg_compression_quality of 100 provides the best-
           quality images but creates large export files.   The recommended
           range is between 70 and 90.

             clip_to_elements(Boolean):
           If set to True , the layout is clipped to the smallest bounding box
           that includes all layout elements."""
        return self._arcpyLayout.exportToPDF(out_pdf, resolution, image_quality,
                                             compress_vector_graphics, image_compression,
                                             embed_fonts, layers_attributes, georef_info,
                                             jpeg_compression_quality, clip_to_elements)

    def list_elements(self, element_type=None, wildcard=None):
        """Layout.list_elements({element_type}, {wildcard})

           Returns a Python list of page layout elements  that exist on  a
           Layout object.

             element_type{String}:
           A string that represents the element type that will be used to filter
           the returned list of elements.

            * GRAPHIC_ELEMENT:   Filter for GraphicElement objects.

            * LEGEND_ELEMENT:   Filter for LegendElement objects.

            * MAPFRAME_ELEMENT: Filter for MapFrame objects.

            * MAPSURROUND_ELEMENT:   Filter for MapsurroundElement objects.

            * PICTURE_ELEMENT:   Filter for PictureElement objects.

            * TEXT_ELEMENT:   Filter for TextElement objects.

             wildcard{String}:
           A wildcard is based on the element name and is not case sensitive.  A
           combination of asterisks (*) and characters can be used to help limit
           the results.
        """
        listElements = self._arcpyLayout.listElements(element_type, wildcard)
        if element_type == "MAPFRAME_ELEMENT":
            return [MapFrame(x) for x in listElements]
        elif element_type == "TEXT_ELEMENT":
            return [TextElement(x) for x in listElements]
        elif element_type == "PICTURE_ELEMENT":
            return [PictureElement(x) for x in listElements]
        elif element_type == "GRAPHIC_ELEMENT":
            return [GraphicElement(x) for x in listElements]
        elif element_type == "MAPSURROUND_ELEMENT":
            return [MapSurroundElement(x) for x in listElements]
        elif element_type == "TEXT_ELEMENT":
            return [TextElement(x) for x in listElements]
        elif element_type == "LEGEND_ELEMENT":
            return [LegendElement(x) for x in listElements]

    def _repr_pdf_(self):
        import tempfile
        filepath = os.path.join(tempfile.tempdir, 'temp.pdf')
        self.export_PDF(filepath)
        with open(filepath, 'r+') as f:
            contents = f.read()


class Map(object):
    """
    The Map is the primary object for referencing and managing layers and
    tables within an ArcGIS Pro project.
    """
    def __init__(self, arcpyMap):
        self._arcpyMap = arcpyMap
        self.default_camera = self._arcpyMap.defaultCamera
        self.map_type = self._arcpyMap.mapType
        self.name = self._arcpyMap.name

    @_lazy_property
    def layers(self):
        """
           Returns a Python list of Layer objects that exist within a map.
        """
        return [Layer(lyr) for lyr in self._arcpyMap.listLayers("*")] 

    @_lazy_property
    def tables(self):
        """Returns a Python list of Table objects that exist within a map.
        """
        return [Table(tbl) for tbl in self._arcpyMap.listTables("*")] 

    @_lazy_property
    def bookmarks(self):
        """Returns a Python list of bookmark objects in a Map """
        return [Bookmark(bkm) for bkm in self._arcpyMap.listBookmarks("*")] 

    @_lazy_property
    def broken_data_sources(self):
        """Returns a Python list of Layer or Table objects that have broken
           connections to their original source data within a map."""
        brokenDataSources = []
        _arcpyBrokenDataSources = self._arcpyMap.listBrokenDataSources("*")
        for brokenDS in _arcpyBrokenDataSources:
            if isinstance(brokenDataSources, arcpy.mp.Table):
                brokenDataSources.append(Table(brokenDS))
            elif isinstance(brokenDataSources, arcpy.mp.Layer):
                brokenDataSources.append(Layer(brokenDS))
            else:
                brokenDataSources.append(brokenDS)
        return brokenDataSources
    
    def add_layer(self, add_layer_or_layerfile, target_group_layer=None, reference_layer=None, add_position='AUTO_ARRANGE'):
        """Map.add_layer(add_layer_or_layerfile, {target_group}, {reference_layer}, {add_position})

           Provides the ability to add a Layer or LayerFile to a map within a
           project ( .aprx ) using basic placement options. The layer can be added to
           an existing group layer OR added to a specific position by specifying
           a reference layer

             add_layer_or_layerfile(Layer):
           A reference to a Layer or LayerFile object representing the layer or
           layers  to be added.
           
             target_group_layer(Layer):
           A reference to an existing group Layer object, default is None. Only one
           of target_group_layer or reference_layer can be specified.
           
           reference_layer(Layer):
           A Layer object representing an existing layer that determines the
           location where the new layer will be inserted. Only one
           of target_group_layer or reference_layer can be specified.

             add_position{String}:
           A constant that determines the placement of the added layer or layers
           in a map.

            * AUTO_ARRANGE: Automatically places the layer or layers based on
            its layer weight rules and geometry.

            * BOTTOM: Places the layer or layers at the bottom of the TOC layer
            stack.

            * TOP: Places the layer or layers at the top of the TOC layer stack.
            
            When adding a layer relative to the reference_layer, use one of these:

            * AFTER: Inserts the new layer after or below the reference layer.

            * BEFORE: Inserts the new layer before or above the reference layer.
        """
        if type(add_layer_or_layerfile) is Layer:
            add_layer_or_layerfile = add_layer_or_layerfile._arcpy_object
        
        if target_group_layer is not None:
            target_group_layer = target_group_layer._arcpy_object
            return self._arcpyMap.addLayerToGroup(target_group_layer, add_layer_or_layerfile, add_position)
        elif reference_layer is not Null:
            reference_layer = reference_layer._arcpy_object
            return self._arcpyMap.insertLayer(reference_layer, add_layer_or_layerfile, add_position)
        else:
            return self._arcpyMap.addLayer(add_layer_or_layerfile, add_position)
 
    def move_layer(self, reference_layer, move_layer, insert_position='BEFORE'):
        """Map.move_layer(reference_layer, move_layer, {insert_position})

           Provides the ability to move a layer or group layer in a map to  a
           specific location in the layer stack.

             reference_layer(Layer):
           A Layer object representing an existing layer that determines the
           location where the new layer will be moved.

             move_layer(Layer):
           A reference to a Layer object representing the layer to be moved.

             insert_position{String}:
           A constant that determines the placement of the moved layer relative
           to the reference layer.

            * AFTER: Moves the  layer after or below the reference layer.

            * BEFORE: Moves the layer before or above the reference layer."""
        return self._arcpyMap.moveLayer(reference_layer._arcpy_object, move_layer._arcpy_object, insert_position)

    def remove_layer(self, remove_layer):
        """Map.remove_layer(remove_layer)

           Provides the ability to remove a layer from a map in a project.

             remove_layer(Layer):
           A reference to a Layer object representing the layer to be removed."""
        return self._arcpyMap.removeLayer(remove_layer._arcpy_object)

    def add_table(self, add_table):
        """Map.add_table(add_table)

           Provides the ability to add a Table to a map within a project (.aprx).

             add_table(Table):
           A reference to a Table object representing the table  to be added.
        """
        return self._arcpyMap.addTable(add_table._arcpyTable)

    def remove_table(self, remove_table):
        """Map.remove_table(remove_table)

           Provides the ability to remove a table from a map in a project.

             remove_table(Table):
           A reference to a Table object representing the layer to be removed."""
        return self._arcpyMap.removeTable(remove_table._arcpyTable)

    def clear_selection(self):
        """Map.clear_selection()

           Clears the selection for all layers and tables in a map."""
        return self._arcpyMap.clearSelection()
   
    def update_connection_properties(self, current_connection_info, new_connection_info, auto_update_joins_and_relates=True, validate=True):
        """Map.update_connection_properties(current_connection_info,
           new_connection_info, {auto_update_joins_and_relates}, {validate})

           Replaces connection properties using a dictionary or a path to a
           workspace.

             current_connection_info(String):
           A string that represents the workspace path or a Python dictionary
           that contains connection properties to the source you want to update.

             new_connection_info(String):
           A string that represents the workspace path or a Python dictionary
           that contains connection properties with the new source information.

             auto_update_joins_and_relates{Boolean}:
           If  set to True , the updateConnectionProperties method will also
           update the connections for associated joins or relates.

             validate{Boolean}:
           If  set to True , the connection properties will only be updated if
           the new_connection_info value is a valid connection.  If it is not
           valid, the connection will not be replaced.   If set to False , the
           method will set all connections to match the new_connection_info ,
           regardless of a valid match.  In this case, if a match does not
           exist, then the data sources would be broken."""
        return self._arcpyMap.updateConnectionProperties(current_connection_info, new_connection_info, auto_update_joins_and_relates, validate)


class Bookmark(object):
    """Provides access to bookmark methods and properties."""
    def __init__(self, arcpyBookmark):
        self._arcpy_object = arcpyBookmark
        self.hasThumbnail = arcpyBookmark.hasThumbnail
        self.map = arcpyBookmark.map
        self.name = arcpyBookmark.name

    def update_thumbnail(self):
        """Bookmark.update_thumbnail()

           Updates a bookmark's thumbnail image."""
        return self._arcpy_object.updateThumbnail()


class Camera(object):
    """
    The Camera object provides access to 2D and 3D viewer properties that
    control the display in a MapFrame.
    """
    def __init__(self, arcpy_object):
        self._arcpy_object = arcpy_object
        self.heading = arcpy_object.heading
        self.mode = arcpy_object.mode
        self.pitch = arcpy_object.pitch
        self.roll = arcpy_object.roll
        self.scale = arcpy_object.scale
        self.X = arcpy_object.X
        self.Y = arcpy_object.Y
        self.Z = arcpy_object.Z

    @property
    def extent(self):
        """Extent object for a 2D map frame"""
        return Extent(self._arcpy_object.getExtent())

    @extent.setter
    def x(self, value):
        self._arcpy_object.setExtent(value._arcpy_object)


class GraphicElement(object):
    """
    The GraphicElement object provides access to properties that enables its
    repositioning on the page layout, as well as methods that allow for
    duplicating and deleting existing graphic elements.
    """
    def __init__(self, arcpy_object):
        self._arcpy_object = arcpy_object
        self.elementHeight = arcpy_object.elementHeight
        self.elementPositionX = arcpy_object.elementPositionX
        self.elementPositionY = arcpy_object.elementPositionY
        self.elementRotation = arcpy_object.elementRotation
        self.elementWidth = arcpy_object.elementWidth
        self.isGroup = arcpy_object.isGroup
        self.name = arcpy_object.name
        self.type = arcpy_object.type
        self.visible = arcpy_object.visible

    def clone(self, suffix=None):
        """GraphicElement.clone({suffix})

           Provides a mechanism to clone an existing graphic element on a page
           layout.

             suffix{String}:
           An optional string that is used to tag each newly created graphic
           element.  The new element will get the same element name as the
           parent graphic plus the suffix value along with  a numeric sequencer.
           For example, if the parent element name is Line and the suffix value
           is _copy , the newly cloned elements are named Line_copy ,
           Line_copy_1 , Line_copy_2 , and so on.  If a suffix is not provided,
           the results resemble Line_1 , Line_2 , Line_3 , and so on."""
        return GraphicElement(self._arcpy_object.clone(suffix))

    def delete(self):
        """GraphicElement.delete()

           Provides a mechanism to delete an existing graphic element on a page
           layout."""
        return self._arcpy_object.delete(self._arcpy_object)


class LabelClass(object):
    """Provides access to a layer's label class properties."""
    def __init__(self, arcpy_object):
        self._arcpy_object = arcpy_object
        self.expression = arcpy_object.expression
        self.name = arcpy_object.name
        self.SQLQuery = arcpy_object.SQLQuery
        self.visible = arcpy_object.visible


class Layer(object):
    """Provides access to basic layer properties and methods"""
    def __init__(self, arcpy_object):
        self._arcpy_object = arcpy_object
        
        self.brightness = arcpy_object.brightness
        self.contrast = arcpy_object.contrast
        self.connectionProperties = arcpy_object.connectionProperties
        self.dataSource = arcpy_object.dataSource
        self.definitionQuery = arcpy_object.definitionQuery
        self.is3DLayer = arcpy_object.is3DLayer
        self.isBroken = arcpy_object.isBroken
        self.isFeatureLayer = arcpy_object.isFeatureLayer
        self.isGroupLayer = arcpy_object.isGroupLayer
        self.isNetworkAnalystLayer = arcpy_object.isNetworkAnalystLayer
        self.isRasterLayer = arcpy_object.isRasterLayer
        self.isWebLayer = arcpy_object.isWebLayer
        self.longName = arcpy_object.longName
        self.maxThreshold = arcpy_object.maxThreshold
        self.minThreshold = arcpy_object.minThreshold
        self.name = arcpy_object.name
        self.showLabels = arcpy_object.showLabels
        self.transparency = arcpy_object.transparency
        self.visible = arcpy_object.visible

    def extrusion(self, extrusion_type='NONE', expression=None):
        """Layer.extrusion({extrusion_type}, {expression})

           Extrudes 2D features in a layer to display 3D symbology.

             extrusion_type{String}:
           A string that specifies the extrusion method.  The default value is
           NONE which turns off layer extrusion.

            * ABSOLUTE_HEIGHT: The feature is extruded to the specified z-value,
            as a flat top, regardless of the z-values of the feature.

            * BASE_HEIGHT: A z-value is calculated for each vertex of the
            feature's base, and the feature is extruded to the various z-values
            creating a multifaceted top.

            * MAX_HEIGHT: Adds extrusion height to the minimum z-value of the
            feature, and the feature is extruded to a flat top at that value.

            * MIN_HEIGHT: Adds extrusion height to the minimum z-value of the
            feature, and the feature is extruded to a flat top at that value.

            * NONE: Features are not extruded.

             expression{String}:
           A string that defines the extrusion expression, which provides an
           absolute extrusion height for each feature."""
        return self._arcpy_object.extrusion(extrusion_type, expression)

    @_lazy_property
    def selection_set(self):
        """
           a layer's selection as a Python set of object IDs
        """
        return self._arcpy_object.getSelectionSet()

    @_lazy_property
    def label_classes(self, wildcard=None):
        """list of LabelClass objects in a layer."""
        return [LabelClass(lc) for lc in self._arcpy_object.listLabelClasses("*")]

    @_lazy_property
    def layers(self):
        """list of Layer objects in a layer file."""
        return [Layer(lyr) for lyr in self._arcpy_object.listLayers("*")]

    def save(self, file_name):
        """Layer.save(file_name)

           Saves a layer to a layer file ( .lyrx ).

             file_name(String):
           A string that includes the location and name of the output layer file
           ( .lyrx )."""
        return self._arcpy_object.saveACopy(file_name)

    def set_selection_set(self, oidList=None, method='NEW'):
        """Layer.set_selection_set({oidList}, {method})

           Sets a layer's selection using a Python set of Object IDs.

             oidList{Integer}:
           A Python set of Object IDs to use along with the appropriate
           selection method.

             method{String}:
           A string that specifies which selection method to use.

            * NEW: Creates a new feature selection from the oidList .

            * DIFFERENCE: Selects the features that are not in the current
            selection but are in the oidList .

            * INTERSECT: Selects the features that are in the current selection
            and the oidList .

            * SYMDIFFERENCE: Selects the features that are in the current
            selection or the oidList but not both.

            * UNION: Selects all the features in both the current selection and
            those in the oidList ."""
        return self._arcpy_object.setSelectionSet(oidList, method)

    def supports(self, layer_property):
        """Layer.supports(layer_property)

           Used to determine if a particular layer type supports a property on
           the layer object.  Not all layers support the same set of properties;
           the supports property can be used to test if a layer supports that
           property before attempting to set it.

             layer_property(String):
           The name of a particular layer property that will be tested.

            * BRIGHTNESS:   A raster layer's brightness value.

            * CONNECTIONPROPERTIES: A Layer's connection information.

            * CONTRAST:   A raster layer's contrast value

            * CREDITS:   A layer's credit information.

            * DATASOURCE:   A layer's file path or connection file.

            * DEFINITIONQUERY:   A layer's definition query string.

            * LONGNAME:   A layer's path including the group layers it may be
            nested within.

            * MAXTHRESHOLD:   A layer's maximum threshold to display the
            features.

            * MINTHRESHOLD:   A layer's minimum threshold to display the
            features.

            * NAME:   A layer's name.

            * TRANSPARENCY:   A layer's transparency value."""
        return self._arcpy_object.supports(layer_property)

    def update_connection_properties(self, current_connection_info, new_connection_info, auto_update_joins_and_relates=True, validate=True):
        """Layer.updateConnectionProperties(current_connection_info,
           new_connection_info, {auto_update_joins_and_relates}, {validate})

           Replaces connection properties using a dictionary or a path to a
           workspace.

             current_connection_info(String):
           A string that represents the workspace path or a Python dictionary
           that contains connection properties to the source you want to update.

             new_connection_info(String):
           A string that represents the workspace path or a Python dictionary
           that contains connection properties with the new source information.

             auto_update_joins_and_relates{Boolean}:
           If  set to True , the updateConnectionProperties method will also
           update the connections for associated joins or relates.

             validate{Boolean}:
           If  set to True , the connection properties will only be updated if
           the new_connection_info value is a valid connection.  If it is not
           valid, the connection will not be replaced.   If set to False , the
           method will set all connections to match the new_connection_info ,
           regardless of a valid match.  In this case, if a match does not
           exist, then the data sources would be broken."""
        return self._arcpy_object.updateConnectionProperties(current_connection_info, new_connection_info, auto_update_joins_and_relates, validate)

    def __str__(self):
        return self.longName


class LayerFile(object):
    """LayerFile(layer_file_path)

       References a layer file ( .lyr or .lyrx ) stored on disk.

         layer_file_path(String):
       A string that includes the full system path and file name of an existing
       layer file.
    """
    def __init__(self, layer_file_path):
        self._arcpy_object = arcpy.mp.LayerFile(layer_file_path)
        self.filePath = self._arcpy_object.filePath
        self.version = self._arcpy_object.version
 
    @_lazy_property
    def layers(self):
        """list of Layer objects in the layer file."""
        return [Layer(lyr) for lyr in self._arcpy_object.listLayers()] 
           
    @_lazy_property
    def broken_data_sources(self):
        """Returns a Python list of Layer objects that have broken
           connections to their original source data within a map.
        """
        return [Layer(lyr) for lyr in self._arcpy_object.listBrokenDataSources()] 

    
    def add_layer(self, add_layer_or_layerfile, target_group_layer=None, reference_layer=None, add_position='AUTO_ARRANGE'):
        """LayerFile.add_layer(add_layer_or_layerfile, {target_group}, {reference_layer}, {add_position})

           Provides the ability to add a Layer or LayerFile to a Layer File 
           using basic placement options. The layer can be added to
           an existing group layer OR added to a specific position by specifying
           a reference layer

             add_layer_or_layerfile(Layer):
           A reference to a Layer or LayerFile object representing the layer or
           layers  to be added.
           
             target_group_layer(Layer):
           A reference to an existing group Layer object, default is None. Only one
           of target_group_layer or reference_layer can be specified.
           
           reference_layer(Layer):
           A Layer object representing an existing layer that determines the
           location where the new layer will be inserted. Only one
           of target_group_layer or reference_layer can be specified.

             add_position{String}:
           A constant that determines the placement of the added layer or layers
           in a map.

            * AUTO_ARRANGE: Automatically places the layer or layers based on
            its layer weight rules and geometry.

            * BOTTOM: Places the layer or layers at the bottom of the TOC layer
            stack.

            * TOP: Places the layer or layers at the top of the TOC layer stack.
            
            When adding a layer relative to the reference_layer, use one of these:

            * AFTER: Inserts the new layer after or below the reference layer.

            * BEFORE: Inserts the new layer before or above the reference layer.
        """
        if type(add_layer_or_layerfile) is Layer:
            add_layer_or_layerfile = add_layer_or_layerfile._arcpy_object
        
        if target_group_layer is not None:
            target_group_layer = target_group_layer._arcpy_object
            return self._arcpy_object.addLayerToGroup(target_group_layer, add_layer_or_layerfile, add_position)
        elif reference_layer is not Null:
            reference_layer = reference_layer._arcpy_object
            return self._arcpy_object.insertLayer(reference_layer, add_layer_or_layerfile, add_position)
        else:
            return self._arcpy_object.addLayer(add_layer_or_layerfile, add_position)
 
    def move_layer(self, reference_layer, move_layer, insert_position='BEFORE'):
        """LayerFile.move_layer(reference_layer, move_layer, {insert_position})

           Provides the ability to move a layer or group layer in a layer file to  a
           specific location in the layer stack.

             reference_layer(Layer):
           A Layer object representing an existing layer that determines the
           location where the new layer will be moved.

             move_layer(Layer):
           A reference to a Layer object representing the layer to be moved.

             insert_position{String}:
           A constant that determines the placement of the moved layer relative
           to the reference layer.

            * AFTER: Moves the  layer after or below the reference layer.

            * BEFORE: Moves the layer before or above the reference layer."""
        return self._arcpy_object.moveLayer(reference_layer._arcpy_object, move_layer._arcpy_object, insert_position)

    def remove_layer(self, remove_layer):
        """LayerFile.remove_layer(remove_layer)

           Provides the ability to remove a layer from a layer file.

             remove_layer(Layer):
           A reference to a Layer object representing the layer to be removed."""
        return self._arcpy_object.removeLayer(remove_layer._arcpy_object)

    def save(self, file_name=None):
        """LayerFile.save({fileName})
           Saves changes to a LayerFile ( .lyrx ) or saves to a new file path or name

             file_name(String):
           Optional. A string used to save an ArcGISProject ( .aprx ) to a new file path
           or file name.
        """
        if file_name is not None:
            return self._arcpy_object.saveACopy(file_name)
        else:
            return self._arcpy_object.save()

    def update_connection_properties(self, current_connection_info, new_connection_info, auto_update_joins_and_relates=True, validate=True):
        """LayerFile.update_connection_properties(current_connection_info,
           new_connection_info, {auto_update_joins_and_relates}, {validate})

           Replaces connection properties using a dictionary or a path to a
           workspace.

             current_connection_info(String):
           A string that represents the workspace path or a Python dictionary
           that contains connection properties to the source you want to update.

             new_connection_info(String):
           A string that represents the workspace path or a Python dictionary
           that contains connection properties with the new source information.

             auto_update_joins_and_relates{Boolean}:
           If  set to True , the updateConnectionProperties method will also
           update the connections for associated joins or relates.

             validate{Boolean}:
           If  set to True , the connection properties will only be updated if
           the new_connection_info value is a valid connection.  If it is not
           valid, the connection will not be replaced.   If set to False , the
           method will set all connections to match the new_connection_info ,
           regardless of a valid match.  In this case, if a match does not
           exist, then the data sources would be broken.
        """
        return self._arcpy_object.updateConnectionProperties(current_connection_info, new_connection_info, auto_update_joins_and_relates, validate)
   
    def __str__(self):
        return self.filePath


class LegendElement(object):
    """The LegendElement object provides access to properties that enable its
       positioning and resizing on the page layout as well as modifying its title.
    """
    def __init__(self, arcpyLegendElement):
        self._arcpy_object = arcpyLegendElement
        self.elementHeight = self._arcpy_object.elementHeight
        self.elementPositionX = self._arcpy_object.elementPositionX
        self.elementPositionY = self._arcpy_object.elementPositionY
        self.elementWidth = self._arcpy_object.elementWidth
        self.name = self._arcpy_object.name
        self.mapFrame = MapFrame(self._arcpy_object.mapFrame)
        self.title = self._arcpy_object.title
        self.type = self._arcpy_object.type
        self.visible = self._arcpy_object.visible


class MapSurroundElement(object):
     def __init__(self, arcpy_map_surround_element):
        self._arcpy_object = arcpy_map_surround_element
        self.elementPositionX = self._arcpy_object.elementPositionX
        self.elementPositionY = self._arcpy_object.elementPositionY
        self.elementHeight = self._arcpy_object.elementHeight
        self.elementWidth = self._arcpy_object.elementWidth
        self.name = self._arcpy_object.name
        self.mapFrame = MapFrame(self._arcpy_object.mapFrame)
        self.type = self._arcpy_object.type
        self.visible = self._arcpy_object.visible


class PictureElement(object):
    """Provides access to picture properties that enable the repositioning of a
       picture on the page layout as well as getting and setting its data source.
    """
    def __init__(self, arcpy_picture_element):
        self._arcpy_object = arcpy_picture_element
        self.elementHeight = self._arcpy_object.elementHeight
        self.elementPositionX = self._arcpy_object.elementPositionX
        self.elementPositionY = self._arcpy_object.elementPositionY
        self.elementRotation = self._arcpy_object.elementRotation
        self.elementWidth = self._arcpy_object.elementWidth
        self.name = self._arcpy_object.name
        self.sourceImage = self._arcpy_object.sourceImage
        self.type = self._arcpy_object.type
        self.visible = self._arcpy_object.visible


class TextElement(object):
    """The TextElement object provides access to properties that enable its
       repositioning on the page layout as well as modifying the text string and font size.
    """
    def __init__(self, arcpy_text_element):
        self._arcpy_object = arcpy_text_element
        self.elementHeight = self._arcpy_object.elementHeight
        self.elementPositionX = self._arcpy_object.elementPositionX
        self.elementPositionY = self._arcpy_object.elementPositionY
        self.elementRotation = self._arcpy_object.elementRotation
        self.elementWidth = self._arcpy_object.elementWidth
        self.textAngle = self._arcpy_object.textAngle
        self.textSize = self._arcpy_object.textSize
        self.name = self._arcpy_object.name
        self.text = self._arcpy_object.text
        self.type = self._arcpy_object.type
        self.visible = self._arcpy_object.visible

    @property
    def text(self):
        return self._arcpy_object.text

    @text.setter
    def text(self, value):
        self._arcpy_object.text = value

    def clone(self, suffix=None):
        """TextElement.clone({suffix})

           Provides a mechanism to clone an existing  text element on a page
           layout.

             suffix{String}:
           An optional string that is used to tag each newly created text
           element.  The new element gets the same element name as the parent
           text element, plus the suffix value, plus a numeric sequencer.  For
           example, if the parent element name is FieldLabel and the suffix
           value is _copy , the newly cloned elements are named FieldLabel_copy
           , FieldLabel_copy_1 , FieldLabel_copy_2 , and so on.  If a suffix is
           not provided, the results resemble FieldLabel_1 , FieldLabel_2 ,
           FieldLabel_3 , and so on.
        """
        return TextElement(self._arcpy_object.clone(suffix))

    def delete(self):
        """TextElement.delete()

           Provides a mechanism to delete an existing text element on a page
           layout.
        """
        return self._arcpy_object.delete()


class MapFrame(object):
    """The MapFrame object is a page layout element that is used to display the
       contents of a map on a layout.  It also provides access to page size
       and positioning, basic navigation methods, and export options.
    """
    def __init__(self, arcpy_map_frame):
        self._arcpy_object = arcpy_map_frame
        self.camera = Camera(self._arcpy_object.camera)
        self.elementHeight = self._arcpy_object.elementHeight
        self.elementPositionX = self._arcpy_object.elementPositionX
        self.elementPositionY = self._arcpy_object.elementPositionY
        self.elementRotation = self._arcpy_object.elementRotation
        self.elementWidth = self._arcpy_object.elementWidth
        self.map = Map(self._arcpy_object.map)
        self.name = self._arcpy_object.name
        self.type = self._arcpy_object.type
        self.visible = self._arcpy_object.visible

    def get_layer_extent(self, layer, selection_only=True, symbolized_extent=True):
        """MapFrame.getLayerExtent(layer, {selection_only}, {symbolized_extent})

           Returns a layer's extent for all features or only the selected
           features in a layer.

             layer(Layer):
           A reference to a Layer object.

             selection_only{Boolean}:
           If True, it returns the extent for selected features; if False, it
           returns the extent for all features.

             symbolized_extent{Boolean}:
           A value of True will return the layer's symbolized extent; otherwise,
           it will return the geometric extent.  The symbolized extent takes
           into account the area the symbology covers so that it does not get
           cut off by the data frame's boundary.
        """
        return self._arcpy_object.getLayerExtent(layer, selection_only, symbolized_extent)

    def pan_to_extent(self, extent):
        """MapFrame.pan_to_extent(extent)

           Pans and centers the MapFrame using a new Extent object without
           changing the map frame's scale.

             extent(Extent):
           A geoprocessing Extent object.
        """
        return self._arcpy_object.panToExtent(extent)

    def zoom_to_all_layers(self, selection_only=True, symbolized_extent=True):
        """MapFrame.zoom_to_all_layers({selection_only}, {symbolized_extent})

           Modifies the MapFrame view to match the extent of all layers or
           selected layers in a map.

             selection_only{Boolean}:
           If True , it sets the extent based on the selected  features; if
           False , it sets the extent for all  features in a map.

             symbolized_extent{Boolean}:
           A value of True will return the layer's symbolized extent; otherwise,
           it will return the geometric extent.  The symbolized extent takes
           into account the area the symbology covers so that it does not get
           cut off by the map frame's boundary.
        """
        return self._arcpy_object.zoomToAllLayers(selection_only, symbolized_extent)

    def zoom_to_bookmark(self, bookmark):
        """MapFrame.zoom_to_bookmark(bookmark)

           Modifies the MapFrame view to match the view information stored with
           a spatial bookmark.

             bookmark(Bookmark):
           A reference to a Bookmark object.
        """
        return self._arcpy_object.zoomToBookmark(bookmark._arcpy_object)

    
    def export(self, filename, resolution=96, world_file=False, color_mode='24-BIT_TRUE_COLOR',
               jpeg_quality=80, tiff_compression='LZW', geoTIFF_tags=False):
        """
        MapFrame.export(out_file, {resolution}, {world_file},
        {jpeg_color_mode}, {jpeg_quality}, {tiff_compression}, {geoTIFF_tags})

        Exports the contents of a MapFrame to the specified file

            filename(String):
        A string that represents the path and file name for the output export
        file. JPEG, PNG and TIFF are supported export formats. If JPEG file
        is being exported, optionally set the jpeg_quality. If TIFF file is
        being exported, oprtionally set tiff_compression and the geoTIFF parameter

            resolution{Integer}:
        A number that defines the resolution of the export file in dots per
        inch (dpi).

            world_file{Boolean}:
        If set to True , a georeferenced world file is created. The file
        contains pixel scale information and real-world coordinate
        information.  If you export a 3D map frame, this parameter will be
        ignored regardless of the setting because world files are not
        applicable to 3D views.

            color_mode{String}:
        This value specifies the number of bits used to describe color.

        * 8-BIT_GRAYSCALE:   8-bit grayscale

        * 24-BIT_TRUE_COLOR:   24-bit true color

            jpeg_quality{Integer}:
        This value (0-100) controls the amount of compression applied to the
        output image. For JPEG, image quality is adversely affected the more
        compression is applied. A higher quality (highest = 100) setting will
        produce sharper images and larger file sizes. A lower quality setting
        will produce more image artifacts and smaller files.
            
        tiff_compression{String}:
        This value represents a compression scheme.

        * DEFLATE:   A lossless data compression.

        * JPEG: JPEG compression.

        * LZW:   Lempel-Ziv-Welch, a lossless data compression.

        * NONE:   Compression is not applied.

        * PACK_BITS:   Pack bits compression.

            geoTIFF_tags{Boolean}:
        If set to True , georeferencing tags are included in the structure of
        the TIFF export file. The tags contain pixel scale information and
        real-world coordinate information. These tags can be read by
        applications that support GeoTIFF format.
        """
        extension = os.path.splitext(filename)[1][1:].strip().lower()
        if extension == "jpeg" or extension == "jpg":
            return self._arcpy_object.exportToJPEG(filename, resolution, world_file, color_mode, jpeg_quality)
        elif extension == "png":
            return self._arc_object.exportToPNG(filename, resolution, world_file, color_mode)
        elif extension == "tiff" or extension == "tif":
            return self._arc_object.exportToTIFF(filename, resolution, world_file, color_mode, tiff_compression, geoTIFF_tags)


class Table(object):
    """Enables you to reference a table in a workspace so that it can be added
       to a Map .
    """

    def __init__(self, table_data_source):
        """Table(table_data_source)

           Enables you to reference a table in a workspace so that it can be added to a Map .

             table_data_source(String):
           A string that includes the full workspace path, including the name of the table.  For SDE tables, the workspace path is the path to an SDE connection file.
        """
        self._arcpy_object = arcpy.mp.Table(table_data_source)

        self.connectionProperties = self._arcpy_object.connectionProperties
        self.dataSource = self._arcpy_object.dataSource
        self.definitionQuery = self._arcpy_object.definitionQuery
        self.isBroken = self._arcpy_object.isBroken
        self.name = self._arcpy_object.name

    @_lazy_property
    def selection_set(self):
        """
           a table's selection as a Python set of object IDs
        """
        return self._arcpy_object.getSelectionSet()

    def set_selection_set(self, oidList=None, method='NEW'):
        """Table.set_selection_set({oidList}, {method})

            Sets a table's selection using a Python set of Object IDs.

                oidList{Integer}:
            A Python set of Object IDs to use along with the appropriate
            selection method.

                method{String}:
            A string that specifies which selection method to use.

            * NEW: Creates a new feature selection from the oidList .

            * DIFFERENCE: Selects the features that are not in the current
            selection but are in the oidList .

            * INTERSECT: Selects the features that are in the current selection
            and the oidList .

            * SYMDIFFERENCE: Selects the features that are in the current
            selection or the oidList but not both.

            * UNION: Selects all the features in both the current selection and
            those in the oidList .
         """
        return self._arcpy_object.setSelectionSet(oidList, method)


    def update_connection_properties(self, current_connection_info, new_connection_info, auto_update_joins_and_relates=True, validate=True):
        """Table.update_connection_properties(current_connection_info,
           new_connection_info, {auto_update_joins_and_relates}, {validate})

           Replaces connection properties using a dictionary or a path to a
           workspace.

             current_connection_info(String):
           A string that represents the workspace path or a Python dictionary
           that contains connection properties to the source you want to update.

             new_connection_info(String):
           A string that represents the workspace path or a Python dictionary
           that contains connection properties with the new source information.

             auto_update_joins_and_relates{Boolean}:
           If  set to True , the updateConnectionProperties method will also
           update the connections for associated joins or relates.

             validate{Boolean}:
           If  set to True , the connection properties will only be updated if
           the new_connection_info value is a valid connection.  If it is not
           valid, the connection will not be replaced.   If set to False , the
           method will set all connections to match the new_connection_info ,
           regardless of a valid match.  In this case, if a match does not
           exist, then the data sources would be broken.
        """
        return self._arcpy_object.updateConnectionProperties(current_connection_info, new_connection_info, auto_update_joins_and_relates, validate)

    def __str__(self):
        return self.name
