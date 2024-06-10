# ArcGIS API for Python Deprecation Announcements

The ArcGIS API for Python occasionally deprecates functionalities, scheduling their removal in future releases. The API reference itself clearly identifies these deprecated features. To ensure your applications continue to function flawlessly and avoid compatibility issues, proactively migrate your code away from them.

## Deprecation Candidates

These classes, functions, and modules in the ArcGIS API for Python are deprecated and may cause compatibility issues in future versions:

### `arcgis.apps` Module 

- `arcgis.apps.dashboard` - entire module deprecated at version **2.1.0**.  This sub-module maybe removed at a future major release (example: 2.x to 3.x). 
- `WebExperience.clone` - deprecated in **2.3.0** will be removed in **2.4.2**. Pass in the Web Experience item to `gis.content.clone_items()` instead.
- `StoryMap.get` - deprecated in **2.2.0** will be removed in **2.4.2**. `get` method has been deprecated, use `content_list` property instead.

### `arcgis.learn` Module

- `categorize_features` - depreacted in **1.7.1** and will be removed in a future major release (example: 2.x to 3.x).  Please use `arcgis.learn.classify_objects` instead.

### `arcgis.gis.nb` Module 

- `Container.terminate` - deprecated in **2.3.0** will be removed in **2.4.2**. Use `Container.shutdown` instead.

### `arcgis.gis` Module

- `ContentManager.add` - deprecated in **2.3.0** will be removed in a future major release (example: 2.x to 3.x).  Use `Folder.add` instead.
- `ContentManager.create_folder` - deprecated in **2.3.0** will be removed in a future major release (example: 2.x to 3.x).  Use `gis.content.folders.create` instead.
- `ContentManager.delete_folder` - deprecated in **2.3.0** will be removed in a future major release (example: 2.x to 3.x).  Use `Folder.delete()` instead.
- `ContentManager.rename_folder` - deprecated in **2.3.0** will be removed in a future major release (example: 2.x to 3.x).  Use `Folder.rename()` instead.
- `Item.share` - deprecated in **2.3.0** will be removed in a future major release (example: 2.x to 3.x).  Use `Item.sharing` instead.
- `Item.shared_with` - deprecated in **2.3.0** will be removed in a future major release (example: 2.x to 3.x).  Use `Item.sharing` instead.
- `Item.unshare` - deprecated in **2.3.0** will be removed in a future major release (example: 2.x to 3.x).  Use `Item.sharing` instead.

## Deprecation Removals

Several classes, functions, and methods have been completely removed from the ArcGIS API for Python. This means your code relying on them will no longer function properly. For a smooth transition, consult the API documentation to find alternative approaches and update your code accordingly.
### `arcgis.mapping` Module
- `WebMap` - removed in **2.4.0**. Use `arcgis.map.Map` instead.
- `WebScene` - removed in **2.4.0**. Use `arcgis.map.Scene` instead.
- `forms` - removed in **2.4.0**. Use dataclasses found in `arcgis.map.forms` module instead.
- `renderer` - removed in **2.4.0**. Use dataclasses found in `arcgis.map.renderers` and methods in `arcgis.map.SmartMappingManager`.

### `arcgis.widgets` Module
- `MapView` - removed in **2.4.0**. Use either `arcgis.map.Map` or `arcgis.map.Scene` instead.

### `arcgis.gis.server` Module

- `Mode.update` - deprecated in **1.7.1** removed in **2.4.0**. Use `Mode.update_mode` instead.

### `arcgis.gis.admin` Module

- `Security.ssl property` - deprecated in **2.1.0** removed in **2.4.0**.  Use `Machine.ssl_certificate` instead.
- `UX.enable_comments` - deprecated in **2.1.0** removed in **2.4.0**. This applies to the getter and setter of the property. 
- `UX.set_background` -deprecated in **2.1.0** removed in **2.4.0**. This applies to the getter and setter of the property. 
- `UX.set_banner` - deprecated in **2.1.0** removed in **2.4.0**. This applies to the getter and setter of the property. 
- `UX.default_extent` - deprecated in **2.1.0** removed in **2.4.0**. This applies to the getter and setter of the property. 
- `UX.default_basemap` - deprecated in **2.1.0** removed in **2.4.0**. This applies to the getter and setter of the property. 
- `UX.vector_basemap` - deprecated in **2.1.0** removed in **2.4.0**. This applies to the getter and setter of the property. 

### `arcgis.raster` Module

- `calculate_distance` - deprecated in **1.8.1** removed in **2.4.0**. Please use arcgis.raster.functions.gbl.distance_accumulation (or arcgis.raster.functions.gbl.distance_allocation for allocation output) instead.
- `calculate_travel_cost` - deprecated in **1.8.1** removed in **2.4.0**. Please use arcgis.raster.functions.gbl.distance_accumulation (or arcgis.raster.functions.gbl.distance_allocation for allocation output), instead.
- `cost_allocation` - deprecated in **1.8.1** removed in **2.4.0**. Please use arcgis.raster.functions.gbl.distance_accumulation instead.
- `cost_backlink` - deprecated in **1.8.1** removed in **2.4.0**. Please use arcgis.raster.functions.gbl.distance_accumulation with value specified for output_back_direction_raster_name, instead.
- `cost_distance` - deprecated in **1.8.1** removed in **2.4.0**. Please use arcgis.raster.functions.gbl.distance_accumulation instead.
- `cost_path` - deprecated in **1.8.1** removed in **2.4.0**. Please use arcgis.raster.functions.gbl.optimal_path_as_raster instead.
- `costpath_as_polyline` - deprecated in **1.8.1** removed in **2.4.0**. Please use arcgis.raster.analytics.optimal_path_as_line instead.
- `determine_travel_costpath_as_polyline` - deprecated in **1.8.1** removed in **2.4.0**. lease use arcgis.raster.functions.gbl.distance_accumulation followed by arcgis.raster.analytics.optimal_path_as_line instead.
- `euclidean_allocation` - deprecated in **1.8.1** removed in **2.4.0**. Please use arcgis.raster.functions.gbl.distance_allocation instead.
- `euclidean_back_direction` - deprecated in **1.8.1** removed in **2.4.0**. Please use arcgis.raster.functions.gbl.distance_accumulation with value specified for output_back_direction_raster_name, instead.
- `euclidean_direction` - deprecated in **1.8.1** removed in **2.4.0**. Please use arcgis.raster.functions.gbl.distance_allocation instead with value specified for output_source_direction_raster_name, instead.
- `euclidean_distance` - deprecated in **1.8.1** removed in **2.4.0**. Please use arcgis.raster.functions.gbl.distance_allocation instead.
- `least_cost_path` - deprecated in **1.9.0** removed in **2.4.0**. Please use arcgis.raster.functions.gbl.distance_accumulation and arcgis.raster.functions.gbl.optimal_path_as_raster instead.
- `optimum_travel_cost_network` - deprecated in **1.8.1** removed in **2.4.0**. Please use arcgis.raster.analytics.optimal_region_connections instead.
- `path_distance` - deprecated in **1.8.1** removed in **2.4.0**. Please use arcgis.raster.functions.gbl.distance_accumulation instead.
- `path_distance_back_link` - deprecated in **1.8.1** removed in **2.4.0**. Please use arcgis.raster.functions.gbl.distance_accumulation with value specified for output_back_direction_raster_name, instead..
- `path_distance_allocation` - deprecated in **1.8.1** removed in **2.4.0**. Please use arcgis.raster.functions.gbl.distance_accumulation.

### `arcgis.features` Module

- `UtilityNetworkManager.query_overrides` - deprecated in **2.1.0** removed in **2.4.0**. 
- `UtilityNetworkManager.apply_overrides` - deprecated in **2.1.0** removed in **2.4.0**. 

### `arcgis.apps` Module

- `StoryMap.nodes` - deprecated in **2.2.0** removed in **2.4.0**. The `nodes` property has been deprecated, use `content_list` property instead.
- `StoryMap.cover_date` - deprecated in **2.4.0** removed in future major release. Use the `date` property in the Cover class.
- `StoryMap.cover` - deprecated in **2.4.0** removed in future major release. Use the Cover class.
- `StoryMap.navigation` - deprecated in **2.4.0** removed in future major release. Use the Navigation class.
- `Briefing.cover` - deprecated in **2.4.0** removed in future major release. Use the Cover class.
- `Collection.cover` - deprecated in **2.4.0** removed in future major release. Use the Cover class.
- `Swipe.properties` - deprecated in **2.4.0** removed in future major release. Use the `content` property instead.
- `Swipe.edit` - deprecated in **2.4.0** removed in future major release. Use the `content` property setter instead.

#### `arcgis.gis` Module

- `Group.invite_by_email` - deprecated in **1.5.1** removed in **2.4.0**.  Use `Group.invite` instead.