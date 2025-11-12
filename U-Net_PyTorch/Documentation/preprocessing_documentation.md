# `preprocessing.py` — Data Preparation for DitchNet

## Overview
`preprocessing.py` handles all **data preprocessing and chip generation** steps required for training and testing the DitchNet segmentation model.  
It converts large digital elevation model (DEM) rasters and vector ditch data into small, standardized feature–label pairs (chips) suitable for model input.

The preprocessing pipeline:
1. Generates feature layers (`HPMF` and `ISI`) from DEM tiles using WhiteboxTools.
2. Creates corresponding binary ditch labels from vector geometries.
3. Normalizes, resamples, and tiles data into `512×512` chips.
4. Produces separate chip directories for training or testing.

---

## Class: `DitchDataset`
A PyTorch Dataset class used in both `train.py` and `test.py` scripts, 
providing feature and label tensors to the model during training, validation, or testing.

### Attributes
- **X** (`list[Path]`): Paths to input feature TIFFs.
- **y** (`list[Path]`): Paths to label TIFFs.
- **transform** (`albumentations.Compose`): Albumentations pipeline applied jointly to image and mask.

### Behavior
Each sample pair is:
1. Loaded as a NumPy array (features as `float32`, labels as `uint8`).
2. Channels of feature image are rearranged from `[C, H, W] → [H, W, C]`.
3. The transform is applied consistently to both image and label.
4. The label is binarized (`0`/`1`), cast to `float32`, and reshaped to `[1, H, W]`.

This ensures compatibility with the segmentation model’s input shape.

---

## Class: `ChipGenerator`
Responsible for **DEM processing, feature extraction, label creation, and chip generation**.

### Initialization
```python
ChipGenerator(
    input_dem_dir,        # directory with input DEM tiles (.tif)
    label_vector_data,    # vector data of ditch lines (.shp or .gpkg)
    output_dir,           # target directory for generated data
    mode="train",         # "train" or "test"
    label_hpmf_threshold=-0.075
)
```

### Main Responsibilities
- Establishes directory hierarchy for `training_data` or `test_data`.
- Creates HPMF and ISI feature rasters using `WhiteboxTools`.
- Rasterizes and filters ditch vector geometries to form binary label rasters.
- Normalizes all layers and tiles them into `512×512` chips.
- Removes temporary rasters after processing.

### Internal Workflow

#### `_set_directories()`
Creates a standardized directory layout:
```
output_dir/
└── training_data/ or test_data/
    ├── feature_chips/
    ├── label_chips/
    └── temp/
```

#### `_create_label_layer(dem_path, hpmf_array, resampled_height, resampled_width)`
- Reads the corresponding DEM’s spatial metadata.
- Clips vector ditch geometries to DEM extent and buffers them by 1.5 m.
- Rasterizes buffered geometries and filters pixels using the HPMF threshold (`≤ -0.075` by default).
- Applies a 3×3 majority filter for smoothing.
- Resamples to align with model resolution by using nearest-neighbor interpolation.

<div style="border: 1.5px solid #d3d3d3; border-radius: 6px; padding: 10px;">

⚠️ **IMPORTANT** ⚠️ \
The input label vector data must share the same coordinate reference system (CRS) as the DEM data and fully cover the same spatial extent.  
If the coordinate systems differ or the vector layer does not overlap the DEM tile completely, the label generation and clipping process will fail.

</div>




#### `_generate_single_chip_pair(...)`
- Extracts matching `feature_chip` and `label_chip` arrays.
- Skips chips with < 0.1 % ditch pixels to reduce class imbalance.
- Saves both as `.tif` files (float32 and uint8 respectively).

#### `generate_chips()`
The main method controlling the full preprocessing pipeline:
1. Iterates through all DEM files in the input directory.
2. Generates temporary HPMF, ISI, and label rasters.
3. Combines them into normalized two-channel feature arrays.
4. Iteratively tiles the data into `512×512` chips.
5. Removes all temporary files after completion.
6. Logs and reports skipped or invalid DEM inputs.

---

## Class: `Main`
A small command-line interface (CLI) wrapper allowing direct execution of preprocessing from the terminal.

### Arguments
| Argument | Type | Description                                                                            |
|-----------|------|----------------------------------------------------------------------------------------|
| `input_dem_dir` | Path | Directory containing DEM `.tif` files to process.                                      |
| `label_vector_data` | Path | Vector dataset (e.g. `.shp`, `.gpkg`) containing ditch features.                       |
| `output_dir` | Path | Output directory for generated chips.                                                  |
| `--mode` | str | `"train"` or `"test"` — determines subdirectory naming. Default: `"train"`                      |
| `--label_hpmf_threshold` | float | Threshold for ditch pixel selection in HPMF layer (`≤ value` kept). Default: `-0.075`. |

---

## Output
Depending on the mode, preprocessing produces the following structure:

```
output_dir/
└── training_data/ or test_data/
    ├── feature_chips/
    │   ├── 0.tif
    │   ├── 1.tif
    │   └── ...
    ├── label_chips/
    │   ├── 0.tif
    │   ├── 1.tif
    │   └── ...
    └── temp/ (removed automatically after processing)
```

Each feature chip is a 2-channel raster (HPMF + ISI) normalized to `[0, 1]`,  
and each label chip is a binary raster (`1` = ditch, `0` = background).

---

## Example Usage
```bash
python preprocessing.py   ./input_DEMs   ./ditch_vectors/ditches.gpkg   ./dataset_output   --mode train   --label_hpmf_threshold -0.05
```

Both **relative** and **absolute** paths are supported for all input and output arguments.  
This means you can run the program from any working directory without adjusting its internal path handling.

### Example Output (Console)
```
Running DitchNet preprocessing on DEM files in: ./input_DEMs

Mode: train
Label HPMF threshold: -0.05

Processing: dem_tile_001.tif
Processing: dem_tile_002.tif
...
Preprocessing completed.
```

---

## Dependencies and Integration
- **WhiteboxTools**: used for hydrologic and terrain analysis (`high_pass_median_filter`, `impoundment_size_index`, `majority_filter`).
- **Rasterio**, **GeoPandas**, **Shapely**: handle raster and vector geospatial data.
- **tifffile**, **scikit-image**: for reading, writing, and resizing TIFF images.
- **Albumentations**: for image augmentation and preprocessing in `DitchDataset`.
- **utils.py**: provides helper functions for normalization and layer creation.

The output dataset integrates directly with `train.py` and `test.py` for model development.
