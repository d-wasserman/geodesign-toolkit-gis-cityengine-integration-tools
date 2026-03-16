# CityEngineToolKit-GeodesignToolkit

A collection of Python scripts that integrate ArcGIS and CityEngine to enable data-driven, large-scale 3D urban design and scenario planning.

## Summary

These tools streamline the preparation of GIS data for CityEngine procedural modeling. Instead of building full urban context models (aerial imagery, terrain, building footprints), they associate design content to individual features — streets, lots, blocks — that can be visualized as pop-ups in web maps or linked to web scenes. This approach enables large-scale geodesign workflows at a fraction of the normal preparation time.

![Output Example](https://github.com/Holisticnature/GeodesignToolkit-GIS-CityEngine-Integration-Tools/blob/master/Help/asset/BatchBlockGif.gif)

## Workflow Overview

1. **Prepare geometry** — Use the `PrepareCE*Associations` scripts to convert real-world GIS features into standardized, CityEngine-compatible geometries clustered at a single reference point.
2. **Populate attributes** — Use `PopulateStreetParameters.py` to add CityEngine street rule fields and default/randomized values.
3. **Split by attribute** — Use `SplitFeaturebyAttribute.py` to divide the attributed feature class into per-scenario layers.
4. **Import into CityEngine** — Import the prepared layers and apply procedural rules.
5. **Batch export** — Use the CityEngine scripts to export all layers as images, KML, FBX, or web scenes for sharing.

---

## ArcGIS Tools

### PrepareCEStreetAssociations.py

Replaces polyline street geometries with standardized, north-south oriented lines located at the mean center of the input (or a reference) feature class. Output is projected to Web Mercator (EPSG:3857) for CityEngine compatibility.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `inFeatureClass` | Feature Class (Polyline) | Yes | Input street centerline feature class |
| `outFeatureClass` | Feature Class (Polyline) | Yes | Output path for the standardized geometry |
| `StreetLength_LotArea` | Double | Yes | Default street length in projection units (used if no size field is provided) |
| `SizeField` | Field (optional) | No | Field containing per-feature street lengths; overrides the constant if provided |
| `referenceFeatureClassCentroid` | Feature Class (optional) | No | Feature class whose mean center is used as the origin; defaults to the input's mean center |

---

### PrepareCELotAssociations.py

Converts polygon lot features into uniform squares located at the mean center of the input (or reference) feature class. Side length is derived from the square root of the target area. Output is projected to Web Mercator (EPSG:3857).

| Parameter | Type | Required | Description |
|---|---|---|---|
| `inFeatureClass` | Feature Class (Polygon) | Yes | Input lot polygon feature class |
| `outFeatureClass` | Feature Class (Polygon) | Yes | Output path for the simplified square geometries |
| `StreetLength_LotArea` | Double | Yes | Default lot area in projection units (used if no size field is provided) |
| `SizeField` | Field (optional) | No | Field containing per-feature lot areas; overrides the constant if provided |
| `referenceFeatureClassCentroid` | Feature Class (optional) | No | Feature class whose mean center is used as the origin; defaults to the input's mean center |

---

### PrepareCEBlockAssociations.py

Creates a templated set of 7 polylines (a center street plus two flanking block outlines) per input feature, all anchored at the mean center of the input or reference feature class. Enables simultaneous exploration of transportation and land-use scenarios in CityEngine. Output is projected to Web Mercator (EPSG:3857).

| Parameter | Type | Required | Description |
|---|---|---|---|
| `inFeatureClass` | Feature Class (Polyline) | Yes | Input street centerline feature class |
| `outFeatureClass` | Feature Class (Polyline) | Yes | Output path for the block geometry set |
| `StreetLength_LotArea` | Double | Yes | Default street segment length in projection units |
| `SizeField` | Field (optional) | No | Field containing per-feature street lengths; overrides the constant if provided |
| `BlockWidth` | Double | Yes | Width of the flanking block polygons on each side of the center street (projection units) |
| `referenceFeatureClassCentroid` | Feature Class (optional) | No | Feature class whose mean center is used as the origin; defaults to the input's mean center |

---

### PopulateStreetParameters.py

Adds CityEngine street shape parameter fields and Complete Street Rule attribute fields to an existing feature class, then optionally populates them with default or randomized values. Used to prepare a GIS dataset to directly drive CityEngine street procedural rules.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `in_feature_class` | Feature Class | Yes | Target feature class to receive street parameter fields |
| `add_cs_rule_attributes` | Boolean | Yes | If `True`, adds all Complete Street Rule attribute fields (bike lanes, parking, transit, sidewalk amenities, etc.) |
| `create_default_parameters` | Boolean | Yes | If `True`, populates all street parameter fields with randomized plausible default values |
| `create_random_attr` | Boolean | Yes | If `True` (and `add_cs_rule_attributes` is also `True`), populates Complete Street Rule fields with randomized values |

**Street Shape Parameter Fields Added**

| Field Name | Type | Description |
|---|---|---|
| `streetWidth` | Double | Total carriageway width (meters) |
| `streetOffset` | Double | Lateral offset of street centerline |
| `sidewalkWidthRight` | Double | Right sidewalk width (meters) |
| `sidewalkWidthLeft` | Double | Left sidewalk width (meters) |
| `precision` | Double | Geometry precision value |
| `laneWidth` | Double | Width of a single travel lane (meters) |
| `type` | Text | Intersection type (e.g., `"Crossing"`) |
| `cornerStyle` | Text | Corner geometry style (e.g., `"Arcs"`) |

**Complete Street Rule Attribute Fields Added** (when `add_cs_rule_attributes = True`)

| Field Name | Type | Section |
|---|---|---|
| `Lane_Distribution` | Double | Lane configuration |
| `Lane_Width` | Double | Lane configuration |
| `Speed_Limit_in_MPH` | Double | Lane configuration |
| `Stop_Begin` / `Stop_End` | Text | Intersection markings |
| `Crosswalk_Begin` / `Crosswalk_End` | Text | Crosswalk markings |
| `Begin_Crosswalk_To_Stop_Bar` / `End_Crosswalk_To_Stop_Bar` | Double | Crosswalk geometry |
| `Crosswalk_Width` | Double | Crosswalk geometry |
| `Right_Parking_Type` / `Left_Parking_Type` | Text | Parking |
| `Right_Parking_Width` / `Left_Parking_Width` | Double | Parking |
| `Center_Type` | Text | Median/center treatment |
| `Center_Width` | Double | Median/center treatment |
| `Planting_and_Walkway_Layout` | Text | Median planting |
| `Boulevard_Inside_Width` / `Boulevard_Configuration` | Double / Text | Boulevard configuration |
| `Median_Ground_Cover` / `Median_Planting_Length` | Text / Double | Median planting |
| `Median_Bus_Stop` / `Median_Bus_Stop_Location` | Text | Median transit |
| `Transit_Lane` / `Transit_Lane_Sides` / `Transit_Lane_Width` / `Transit_Lane_Position` | Text / Double | Transit lanes |
| `Right_Bike_Lane_Width` / `Left_Bike_Lane_Width` | Double | Bike infrastructure |
| `Right_Buffer_Width` / `Left_Buffer_Width` | Double | Bike infrastructure |
| `Buffer_Type` / `Buffer_Protection` / `Parking_Protection` | Text | Bike infrastructure |
| `Left_Bike_Box` / `Right_Bike_Box` / `Bike_Box_Color_Override` | Text | Bike boxes |
| `Sidewalk_Ground_Cover` | Text | Sidewalk |
| `Sidewalk_Planting_Width` / `Sidewalk_Planting_Length` / `Sidewalk_Planting_Spacing` | Double | Sidewalk planting |
| `Sidewalk_Bus_Stop` / `Sidewalk_Bus_Stop_Location` | Text | Sidewalk transit |
| `Sidewalk_Benches` / `Parking_Meters` / `Sidewalk_Street_Lamps` / `Traffic_Lights` | Text | Sidewalk furniture |
| `Bridge_Display` | Text | Bridge |

---

### SplitFeaturebyAttribute.py

Splits a single feature class into multiple feature classes, one per unique value of a chosen field. Useful for separating a batch-prepared CityEngine dataset into per-scenario or per-type layers before import.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `inFeatureClass` | Feature Class | Yes | Input feature class to split |
| `outWorkSpace` | Workspace (GDB or folder) | Yes | Destination workspace for the output feature classes |
| `uniqueField` | Field | Yes | Field whose unique values define the split; each unique value produces one output feature class |
| `compactWorkspace` | Boolean | Yes | If `True`, runs `Compact_management` on the output workspace after splitting |

---

## CityEngine Tools

### CEBatchLayerWebSceneExport.py

Iterates through all layers in the open CityEngine scene and exports each as a CityEngine Web Scene (`.3ws`) to a configurable output folder. Skips `Panorama` and `Scene Light` layers.

**Configuration variables** (edit at top of script before running):

| Variable | Default | Description |
|---|---|---|
| `outputFolder` | `"/BatchExport"` | Output subfolder under the project's `models/` directory |
| `generateBoolean` | `False` | If `True`, regenerates procedural models before export |
| `deleteBoolean` | `False` | If `True`, deletes each layer from the scene after export |

---

### CEBatchLayerKMLExport.py

Iterates through all layers in the open CityEngine scene and exports each as a KML file to a configurable output folder. Terrain is set to `TERRAIN_NONE`.

**Configuration variables** (edit at top of script before running):

| Variable | Default | Description |
|---|---|---|
| `outputFolder` | `"/BatchExportKML/"` | Output subfolder under the project's `models/` directory |
| `generateBoolean` | `False` | If `True`, regenerates procedural models before export |
| `deleteBoolean` | `False` | If `True`, deletes each layer from the scene after export |

---

### CEBatchLayerFBXExport.py

Iterates through all layers in the open CityEngine scene and exports each as an FBX file suitable for game engine import.

**Configuration variables** (edit at top of script before running):

| Variable | Default | Description |
|---|---|---|
| `outputFolder` | `"/BatchExportFBX"` | Output subfolder under the project's `models/` directory |
| `generateBoolean` | `False` | If `True`, regenerates procedural models before export |
| `deleteBoolean` | `False` | If `True`, deletes each layer from the scene after export |
| `fileType` | `"BINARY"` | FBX encoding; `"BINARY"` or `"TEXT"` |
| `CollectTextures` | `True` | Whether to bundle textures with the export |
| `CreateShapeGroups` | `True` | Whether to group shapes in the FBX hierarchy |
| `IncludeMaterials` | `True` | Whether to include material assignments |
| `ExportGeometry` | `"MODEL_GEOMETRY_FALLBACK"` | Geometry source: `"MODEL_GEOMETRY_FALLBACK"`, `"MODEL_GEOMETRY"`, or `"SHAPE_GEOMETRY"` |

---

### CEBatchLayerImageExport.py

Iterates through all layers in the open CityEngine scene and captures a viewport snapshot of each layer as an image file.

**Configuration variables** (edit at top of script before running):

| Variable | Default | Description |
|---|---|---|
| `outputFolder` | `"\BatchExport/"` | Output subfolder under the project's `images/` directory |
| `width` | `1920` | Snapshot width in pixels |
| `height` | `1080` | Snapshot height in pixels |
| `fileType` | `".png"` | Output image format extension |
| `turnOffAllLayers` | `True` | If `True`, hides all layers before iterating so each snapshot shows only one layer |
| `generateBoolean` | `False` | If `True`, regenerates procedural models before each snapshot |
| `deleteBoolean` | `False` | If `True`, deletes each layer from the scene after export |
| `iterateThroughBookMarksBoolean` | `False` | If `True`, captures one snapshot per saved viewport bookmark per layer |

---

### CESelectLayerByAttribute.py

Selects all layers in the open CityEngine scene that contain at least one object whose named attribute matches a target value. Useful for isolating a subset of layers before a batch operation.

**Configuration variables** (edit at top of script before running):

| Variable | Default | Description |
|---|---|---|
| `fieldName` | `"Crosswalk_End"` | Name of the CityEngine object attribute to evaluate |
| `fieldValue` | `"ladder"` | Value to match against the attribute |

---

### snapshotSelectedViewsheds.py (Esri Scripts/)

Captures viewport snapshots from the perspective of each selected viewshed, view dome, or view corridor analysis object. View domes produce 6 images covering all directions (front, left, back, right, up, down). Requires objects to be selected in the scene before running.

**Configuration variables** (edit at top of script before running):

| Variable | Default | Description |
|---|---|---|
| `hRes` | `1240` | Output image resolution in pixels (square for 360 images; width for directional) |
| `nameBase` | `"360 "` | Prefix string prepended to all output image file names |
| `ext` | `".png"` | Output image format extension |

Images are saved to the project's `images/` directory. The camera is restored to its original state after each snapshot sequence.

---

## Limitations

- Cross-sectional attribute data for street centerlines is uncommon. Databases capturing lane counts, widths, and amenities per segment are still maturing.
- Batch procedural model generation requires QAQC review, especially for complex rule sets.
- **CityEngine street width note:** After mapping `streetWidth` to a street rule, changing the width requires updating both the shape parameter and the object attribute. See the Help documents for details.

For more detailed usage, see the HTML help documents in the `Help/` directory.
