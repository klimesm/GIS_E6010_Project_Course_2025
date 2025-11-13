# `inference.py` — Model Inference for DitchNet

## Overview
`inference.py` performs **model inference** on new unseen Digital Elevation Model (DEM) tiles using a trained DitchNet 
segmentation model. It automates the generation of ditch probability, binary classification, and depth maps 
across entire DEM areas.

---

## Class: `Predictor`
Encapsulates the full inference workflow, from preprocessing DEM data to generating and saving prediction rasters.

### Initialization
```python
Predictor(
    model_path,               # path to trained model checkpoint (.ckpt)
    input_dem_dir,            # directory containing DEM tiles (.tif)
    output_dir,               # output directory for prediction results
    batch_size=4,
    compute_precision="32-true"
)
```

### Main Responsibilities
- Loads the trained DitchNet model from a checkpoint.  
- Prepares terrain features (`HPMF`, `ISI`) for each DEM using WhiteboxTools.  
- Divides feature rasters into 512×512 tiles and normalizes their values before feeding them into the model.  
- Runs predictions tile-by-tile using PyTorch Lightning.  
- Merges and saves probability, classified, and depth maps as GeoTIFFs.  
- Builds VRT mosaics for each result type after processing all tiles.

---

### Methods

#### `_set_output_directories()` and `_set_temporary_directories()`:
Creates a standardized directory layout for inference results,
generating only the subdirectories that correspond to the output types selected by the user:

```
output_dir/
    ├── probability_maps/
    ├── classified_maps/
    ├── depth_maps/
    └── temp/ (removed automatically after processing)
```

#### `_create_output_layer()`
Generates a full-size prediction raster by running model inference on the resampled feature data in 512×512 tiles.
The method:

- Divides the 2-channel feature array (HPMF + ISI) into 512×512 tiles, 
ensuring full coverage of the resampled raster.
- Converts each tile into a model-ready tensor and performs inference.
- Applies sigmoid activation and inserts each tile’s prediction 
back into the correct position in an initially empty output mosaic.
- Resamples the assembled prediction raster back to the original DEM resolution.
- Returns a floating-point NumPy array matching the original DEM’s height and width.

#### `_output_probability_map(input_path, profile, output_array)`
- Saves the model’s continuous probability predictions as a float32 GeoTIFF.
- Updates the raster profile accordingly and writes the single-band probability map 
to the `probability_maps/` directory using the input DEM’s name as the filename prefix.

#### `_output_classified_map(input_path, profile, output_array)`
- Creates a binary ditch/no-ditch classification map from the probability raster using 
the user-defined threshold (self.threshold).
- Updates the raster profile accordingly and writes the single-band classified map 
to the `classified_maps/` directory using the input DEM’s name as the filename prefix.

#### `_output_depth_map(input_path, output_array)`
- Loads the corresponding HPMF reference and replaces no-data values with zero.
- Builds the ditch depth map by combining the probability output with the temporary HPMF raster.
- Removes all positive values to preserve only negative (depression) depths.
- Saves the resulting depth raster into the `depth_maps/` directory using the input DEM’s name 
as the filename prefix.

#### `_process_single_dem(dem_path)`
This method performs all steps required to transform one DEM input into its final probability, 
classification, and/or depth outputs:
- Opens the DEM and extracts spatial metadata and dimensions.
- Skips processing if the raster is smaller than 500×500 pixels.
- Generates the HPMF and ISI feature layers using utility functions and stores them in temporary files.
- Normalizes both features and applies a **2.4% upscale** to match the model’s expected resolution.
- Stacks the two normalized feature layers into a 2-channel array.
- Calls `_create_output_layer()` to perform tile-based model inference.
- Writes the selected output maps by invoking:
  - `_output_probability_map()`
  - `_output_classified_map()` (if enabled)
  - `_output_depth_map()` (if enabled)
- Removes intermediate temporary files tied to the processed DEM.

#### `_create_virtual_rasters()`
Creates VRT mosaic files for all output types that were enabled.
For each map category (probability, classified, depth), the method:

- Collects all .tif files in the corresponding output directory.
- Builds a GDAL VRT mosaic that references these rasters without duplicating data.
- Saves the VRT using a standardized filename:
  - ditch_probability_map.vrt
  - ditch_classified_map.vrt
  - ditch_hpmf_depth_map.vrt

These mosaics allow all tile-based outputs to be viewed as seamless layers in GIS software.

#### `predict()`
Serves as the main entry point for running inference across an entire directory of DEM files.
The method:
- Scans the input directory and collects all `.tif` DEM files.
- Prints a processing summary and device information (CPU or GPU).
- Iterates through each DEM and executes `_process_single_dem()`.
- Keeps track of how many DEMs were processed, skipped, or failed.
- After all DEMs are handled, creates VRT mosaics using `_create_virtual_rasters()` for the enabled output types.
- Cleans up the temporary working directory.
- Prints a final summary listing processed, skipped, and failed files.

---

## Class: `Main`
Provides a **command-line interface (CLI)** for running model inference directly from the terminal.

### Arguments
| Argument         | Type                          | Default | Description                                                                           |
| ---------------- |-------------------------------|---------| ------------------------------------------------------------------------------------- |
| `model_path`     | Path                          | —       | Path to the trained DitchNet model checkpoint (`.ckpt`).                              |
| `input_dem_dir`  | Path                          | —       | Directory containing the DEM tiles (`.tif`) to be processed.                          |
| `output_dir`     | Path                          | —       | Directory where all inference results will be written.                                |
| `--threshold`    | float                         | `0.3`   | Probability threshold used to generate the binary classification map.                 |
| `--no_prob_map`  | flag                          | enabled | Disables saving of the probability map output.                                        |
| `--no_class_map` | flag                          | enabled | Disables saving of the classified (binary) map output.                                |
| `--no_depth_map` | flag                          | enabled | Disables saving of the depth map output.                                              |
| `--device`       | str (`cpu` / `cuda` / `auto`) | `auto`  | Specifies the computation device. `"auto"` selects GPU when available, otherwise CPU. |


---

## Output
Creates a standardized directory layout under the specified output folder.
Within the main `output_dir/`, the script organizes inference results into dedicated subfolders:

- `probability_maps/` – stores continuous probability raster outputs.

- `classified_maps/` – contains binary classification rasters showing predicted ditch areas.

- `depth_maps/` – holds depth estimation rasters derived from the HPMF layer.

The script creates only the folders for the output types the user has enabled.

---

## Example Usage
```bash
python inference.py   ./lightning_logs/train_logs/version_0/checkpoints/epoch=005-step=50.ckpt   ./input_DEMs   ./inference_output --threshold 0.1
```

Both **relative** and **absolute** paths are supported for all input and output arguments.
This means you can run the program from any working directory without adjusting its internal path handling.

---

## Dependencies
- **PyTorch**: runs the trained DitchNet model and handles tensor operations on CPU or GPU.
- **Rasterio**: used for reading input DEMs, writing GeoTIFF outputs, and managing spatial metadata.
- **NumPy**: supports array manipulation for feature stacking, masking, and output raster creation.
- **scikit-image**: provides the resize function used for resampling the prediction layer.
- **GDAL**: builds VRT mosaics that merge tile-based outputs into seamless virtual rasters.
- **utils.py**: generates terrain feature layers (HPMF and ISI) and performs normalization required for inference.
- **model.py**: defines the DitchNet architecture and enables loading the trained model checkpoint.

The inference results serve as the final product of the DitchNet workflow and can be directly visualized 
or used for GIS-based ditch mapping and analysis.
