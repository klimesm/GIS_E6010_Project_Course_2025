# `age_classification_vectors.py` — Ditch Age Classification Using Topographic Databases

## Overview
`age_classification_vectors.py` Classify ditch age by combining a raster probability map with historical line vector datasets.
The script binarizes and vectorizes the probability raster, intersects the resulting geometries with year-stamped vector layers, and assigns the earliest year where sufficient overlap is detected.

---

## Requirements
This script uses the following libraries:
- geopandas
- rasterio
- shapely
- numpy
- pandas
- argparse (built-in)

Install the external dependencies with:
`pip install geopandas rasterio shapely numpy pandas`

## Features
This script classifies the age of detected ditches by combining:
- A probability map raster (e.g., U-Net prediction)
- Vector datasets from multiple years
- 
The workflow:
1. Binarize and vectorize the probability map
2. Load vector layers for selected years
3. Compare each raster-derived geometry with vector data
4. Assign the earliest year where a ditch is detected based on minimum intersection length
5. Export the final results as a GeoPackage
   
This script is designed for datasets such as those from Paituli, where ditch information is available as line features (e.g., virtavesikapea layer).

---

## Usage
Command-line example
```python
python age_classification_vectors.py \
 "path/to/probability_map.tif" \
 "2005:path/to/vector_2005.gpkg,layer_2005;2014:path/to/vector_2014.gpkg,layer_2014;2020:path/to/vector_2020.gpkg,layer_2020" \
 "path/to/output.gpkg" \
 --prob_threshold 0.5 \
 --min_overlap_length 10
```

**Argument rules**
- Each vector entry must follow the format: `year:path,layer` Entries are separated by semicolons.
- Paths containing spaces must be enclosed in quotes.
- For Paituli data, use: `virtavesikapea` layer.

- Adjustable parameters:
  `--prob_threshold` : raster binarization threshold (default 0.5)
  `--min_overlap_length` : minimum line intersection length (default 10.0)

---

## Methods
`main(probability_map_path, vector_layers, output_vector_path, prob_threshold, min_overlap_length)`
Coordinates the workflow:
- Vectorizes the probability map
- Loads vector datasets for defined years
- Detects the first appearance year for each geometry
- Saves results to the output path

`vectorize_probability_map(probability_map_path, threshold)`
- Reads raster
- Applies threshold to create a binary mask
- Vectorizes the mask using rasterio.features.shapes
- Returns a GeoDataFrame of polygons

`load_vector_layers(vector_layers, probability_gdf, probability_map_path)`
Loads vector layers while:
- Clipping loading to the raster bounding box for efficiency
- Ensuring all vectors share the same CRS as the raster
- Returns a dictionary: `{year: GeoDataFrame}`

`find_first_appearance(probability_gdf, vector_data, min_overlap_length)`
Determines the earliest year a ditch appears by:
- Comparing each raster geometry with vector layers
- Using spatial indexing for speed
- Evaluating real geometric intersections
- Summing the intersection lengths
- Assigning the first year where the minimum length requirement is met
Adds column:
`first_appearance_year`

`parse_vector_layers(vector_layers_str)`
Parses input strings into a dictionary.
Expected format:
`"2005:path/to.gpkg,layername;2014:path/to.gpkg,layername"`

---

## Output
The script produces a **GeoPackage** (.gpkg) containing:
- Vectorized geometries from the probability map
- Attribute: **first_appearance_year**


