arcgis.map module
=================

.. automodule:: arcgis.map


Map
--------------
.. autoclass:: arcgis.map.Map
    :members:
    :undoc-members:

Map Classes
-----------

Bookmarks
^^^^^^^^^
.. autoclass:: arcgis.map.map_widget.Bookmarks
    :members:
    :undoc-members:

Bookmark
^^^^^^^^
.. autoclass:: arcgis.map.map_widget.Bookmark
    :members:
    :undoc-members:

MapContent
^^^^^^^^^^
.. autoclass:: arcgis.map.map_widget.MapContent
    :members:
    :undoc-members:
    
Scene
--------------
.. autoclass:: arcgis.map.Scene
    :members:
    :undoc-members:

Scene Classes
-------------

Environment
^^^^^^^^^^^
.. autoclass:: arcgis.map.scene_widget.Environment
    :members:
    :undoc-members:

SceneContent
^^^^^^^^^^^^
.. autoclass:: arcgis.map.scene_widget.SceneContent
    :members:
    :undoc-members:

Common Classes (Map and Scene)
------------------------------

Legend
^^^^^^
.. autoclass:: arcgis.map.map_widget.Legend
    :members:
    :undoc-members:

LayerVisibility
^^^^^^^^^^^^^^^
.. autoclass:: arcgis.map.LayerVisibility
    :members:
    :undoc-members:

LayerList
^^^^^^^^^
.. autoclass:: arcgis.map.map_widget.LayerList
    :members:
    :undoc-members:

TimeSlider
^^^^^^^^^^
.. autoclass:: arcgis.map.map_widget.TimeSlider
    :members:
    :undoc-members:

BasemapManager
^^^^^^^^^^^^^^
.. autoclass:: arcgis.map.map_widget.BasemapManager
    :members:
    :undoc-members:
    
GroupLayer
--------------
.. autoclass:: arcgis.map.GroupLayer
    :members:
    :undoc-members:

SmartMappingManager
--------------
.. autoclass:: arcgis.map.SmartMappingManager
    :members:
    :undoc-members:

PopupManager
--------------
.. autopydantic_model:: arcgis.map.popups.PopupManager
    :members:
    :undoc-members:

RendererManager
--------------
.. autopydantic_model:: arcgis.map.renderers.RendererManager
    :members:
    :undoc-members:

OfflineMapAreaManager
--------------
.. autoclass:: arcgis.map.OfflineMapAreaManager
    :members:
    :undoc-members:

Dataclasses
-----------

Popups
------

ArcadeReturnType
^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.popups.ArcadeReturnType

AssociationType
^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.popups.AssociationType

AttachmentDisplayType
^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.popups.AttachmentDisplayType

DateFormat
^^^^^^^^^^
.. autopydantic_model:: arcgis.map.popups.DateFormat

FieldInfo
^^^^^^^^^
.. autopydantic_model:: arcgis.map.popups.FieldInfo

Format
^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.popups.Format

LayerOptions
^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.popups.LayerOptions

MediaInfo
^^^^^^^^^
.. autopydantic_model:: arcgis.map.popups.MediaInfo

MediaType
^^^^^^^^^
.. autopydantic_model:: arcgis.map.popups.MediaType

Order
^^^^^
.. autopydantic_model:: arcgis.map.popups.Order

OrderByField
^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.popups.OrderByField

PopupElementAttachments
^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.popups.PopupElementAttachments

PopupElementExpression
^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.popups.PopupElementExpression

PopupElementFields
^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.popups.PopupElementFields

PopupElementRelationship
^^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.popups.PopupElementRelationship

PopupElementText
^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.popups.PopupElementText

PopupElementUtilityNetworkAssociations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.popups.PopupElementUtilityNetworkAssociations

PopupExpressionInfo
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.popups.PopupExpressionInfo

PopupInfo
^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.popups.PopupInfo

PopupManager
^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.popups.PopupManager

RelatedRecordsInfo
^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.popups.RelatedRecordsInfo

StringFieldOption
^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.popups.StringFieldOption

Value
^^^^^
.. autopydantic_model:: arcgis.map.popups.Value

Symbols
-------
Anchor
^^^^^^
.. autopydantic_model:: arcgis.map.symbols.Anchor

Border
^^^^^^
.. autopydantic_model:: arcgis.map.symbols.Border

Callout
^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.Callout

CimSymbolReference
^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.CimSymbolReference

Decoration
^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.Decoration

ExtrudeSymbol3DLayer
^^^^^^
.. autopydantic_model:: arcgis.map.symbols.ExtrudeSymbol3DLayer

FillSymbol3DLayer
^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.FillSymbol3DLayer

Font
^^^^
.. autopydantic_model:: arcgis.map.symbols.Font

Halo
^^^^
.. autopydantic_model:: arcgis.map.symbols.Halo

HorizontalAlignment
^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.HorizontalAlignment

IconSymbol3DLayer
^^^^^^
.. autopydantic_model:: arcgis.map.symbols.IconSymbol3DLayer

IconSymbol3DLayerResource
^^^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.IconSymbol3DLayerResource

Join
^^^^
.. autopydantic_model:: arcgis.map.symbols.Join

LineCap
^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.LineCap

Marker
^^^^^^
.. autopydantic_model:: arcgis.map.symbols.Marker

Pattern
^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.Pattern

Style
^^^^^^
.. autopydantic_model:: arcgis.map.symbols.Style

LineSymbol3D
^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.LineSymbol3D

LineSymbol3DLayer
^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.LineSymbol3DLayer

Marker
^^^^^^
.. autopydantic_model:: arcgis.map.symbols.Marker

MarkerPlacement
^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.MarkerPlacement

MarkerStyle
^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.MarkerStyle

Material
^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.Material

MeshSymbol3D
^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.MeshSymbol3D

ObjectSymbol3DLayer
^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.ObjectSymbol3DLayer

ObjectSymbol3DLayerResource
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.ObjectSymbol3DLayerResource

Outline
^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.Outline

PathCap
^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.PathCap

PathSymbol3DLayer
^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.PathSymbol3DLayer

Pattern
^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.Pattern

PictureFillSymbolsEsriPFS
^^^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.PictureFillSymbolsEsriPFS

PictureMarkerSymbolEsriPMS
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.PictureMarkerSymbolEsriPMS

Placement
^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.Placement

PointSymbol3D
^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.PointSymbol3D

PolygonStyle
^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.PolygonStyle

PolygonSymbol3D
^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.PolygonSymbol3D

Primitive
^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.Primitive

Profile
^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.Profile

ProfileRotation
^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.ProfileRotation

SimpleFillSymbolEsriSFS
^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.SimpleFillSymbolEsriSFS

SimpleFillSymbolStyle
^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.SimpleFillSymbolStyle

SimpleLineSymbolEsriSLS
^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.SimpleLineSymbolEsriSLS

SimpleLineSymbolStyle
^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.SimpleLineSymbolStyle

SimpleMarkerSymbolEsriSMS
^^^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.SimpleMarkerSymbolEsriSMS

SimpleMarkerSymbolStyle
^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.SimpleMarkerSymbolStyle

SketchEdges
^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.SketchEdges

SolidEdges
^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.SolidEdges

Style
^^^^^
.. autopydantic_model:: arcgis.map.symbols.Style

StyleOrigin
^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.StyleOrigin

TextBackground
^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.TextBackground

TextDecoration
^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.TextDecoration

TextFont
^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.TextFont

TextStyle
^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.TextStyle

TextSymbol3DLayer
^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.TextSymbol3DLayer

TextSymbolEsriTS
^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.TextSymbolEsriTS

TextWeight
^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.TextWeight

VerticalAlignment
^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.VerticalAlignment

VerticalOffset
^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.VerticalOffset

WaterbodySize
^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.WaterbodySize

WaterSymbol3DLayer
^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.WaterSymbol3DLayer

WaveStrength
^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.symbols.WaveStrength

Weight
^^^^^^
.. autopydantic_model:: arcgis.map.symbols.Weight

Renderers
---------
AttributeColorInfo
^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.AttributeColorInfo

AuthoringInfo
^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.AuthoringInfo

AuthoringInfoClassBreakInfo
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.AuthoringInfoClassBreakInfo

AuthoringInfoField
^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.AuthoringInfoField

AuthoringInfoStatistics
^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.AuthoringInfoStatistics

AuthoringInfoVisualVariable
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.AuthoringInfoVisualVariable

ClassBreakInfo
^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.ClassBreakInfo

ClassBreaksRenderer
^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.ClassBreaksRenderer

ClassificationMethod
^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.ClassificationMethod

ColorInfoVisualVariable
^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.ColorInfoVisualVariable

ColorRamp
^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.ColorRamp

ColorRampType
^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.ColorRampType

ColorStop
^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.ColorStop

DictionaryRenderer
^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.DictionaryRenderer

DotDensityRenderer
^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.DotDensityRenderer

ExpressionInfo
^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.ExpressionInfo

FlowRenderer
^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.FlowRenderer

FlowRepresentation
^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.FlowRepresentation

FlowTheme
^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.FlowTheme

Focus
^^^^^
.. autopydantic_model:: arcgis.map.renderers.Focus

HeatmapColorStop
^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.HeatmapColorStop

HeatmapRenderer
^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.HeatmapRenderer

InputOutputUnit
^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.InputOutputUnit

LegendOptions
^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.LegendOptions

LegendOrder
^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.LegendOrder

NormalizationType
^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.NormalizationType

OthersThresholdColorInfo
^^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.OthersThresholdColorInfo

PieChartRenderer
^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.PieChartRenderer

PredominanceRenderer
^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.PredominanceRenderer

RampAlgorithm
^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.RampAlgorithm
    :members:
    :undoc-members:
    
RatioStyle
^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.RatioStyle

RendererManager
^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.RendererManager

RendererType
^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.RendererType

RotationInfoVisualVariable
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.RotationInfoVisualVariable

RotationType
^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.RotationType

SimpleRenderer
^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.SimpleRenderer

Size
^^^^
.. autopydantic_model:: arcgis.map.renderers.Size

SizInfoVisualVariable
^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.SizInfoVisualVariable

SizeStop
^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.SizeStop

StandardDeviationInterval
^^^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.StandardDeviationInterval
    :members:
    :undoc-members:
    
StretchRenderer
^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.StretchRenderer

StretchType
^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.StretchType

TemporalRenderer
^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.TemporalRenderer

Theme
^^^^^
.. autopydantic_model:: arcgis.map.renderers.Theme

TimeUnits
^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.TimeUnits

TrailCap
^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.TrailCap

TransparencyInfoVisualVariable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.TransparencyInfoVisualVariable

TransparencyStop
^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.TransparencyStop

UniqueValueClass
^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.UniqueValueClass

UniqueValueGroup
^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.UniqueValueGroup

UniqueValueInfo
^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.UniqueValueInfo

UniqueValueRenderer
^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.UniqueValueRenderer

UniqueValueSymbolStyle
^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.UniqueValueSymbolStyle

UnivariateTheme
^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.UnivariateTheme

VectorFieldRenderer
^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.VectorFieldRenderer

VectorFieldStyle
^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.VectorFieldStyle

VisualVariableType
^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.renderers.VisualVariableType

Forms
-----
CodedValue
^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.CodedValue

FormAttachmentElement
^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.FormAttachmentElement

FormAttachmentInput
^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.FormAttachmentInput

FormAudioInput
^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.FormAudioInput

FormBarcodeScannerInput
^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.FormBarcodeScannerInput

FormComboBoxInput
^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.FormComboBoxInput

FormDatePickerInput
^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.FormDatePickerInput

FormDatetimePickerInput
^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.FormDatetimePickerInput

FormDocumentInput
^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.FormDocumentInput

FormExpressionInfo
^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.FormExpressionInfo

FormFieldElement
^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.FormFieldElement

FormGroupElement
^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.FormGroupElement

FormImageInput
^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.FormImageInput

FormInfo
^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.FormInfo

FormRadioButtonInput
^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.FormRadioButtonInput

FormRelationshipElement
^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.FormRelationshipElement

FormSignatureInput
^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.FormSignatureInput
    :members:
    :undoc-members:
    
FormSwitchInput
^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.FormSwitchInput

FormTextAreaInput
^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.FormTextAreaInput

FormTextBoxInput
^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.FormTextBoxInput

FormTextElement
^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.FormTextElement

FormTimeInput
^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.FormTimeInput

FormTimestampOffsetPickerInput
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.FormTimestampOffsetPickerInput

FormVideoInput
^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.FormVideoInput

InheritedDomain
^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.InheritedDomain

InitialState
^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.InitialState

Order
^^^^^
.. autopydantic_model:: arcgis.map.forms.Order

OrderByField
^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.OrderByField

RangeDomain
^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.RangeDomain

ReturnType
^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.ReturnType

TextFormat
^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.TextFormat

TimeResolution
^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.TimeResolution

UniqueCodedValue
^^^^^^^^^^^^^^^^
.. autopydantic_model:: arcgis.map.forms.UniqueCodedValue
