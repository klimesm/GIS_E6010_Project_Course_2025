# `inference.py` — Model Inference for DitchNet

## Overview
`inference.py` performs inference on DEM tiles using one or more trained DitchNet model checkpoints.
During inference each model produces a prediction for every tile, and the outputs are averaged to create the final result.

---

## Class: `Predictor`
Encapsulates the full inference workflow, from preprocessing DEM data to generating and saving prediction rasters.

### Initialization
```python
Predictor(
    model_dir,                # directory containing one or more .ckpt files
    input_dem_dir,            # directory containing DEM tiles (.tif)
    output_dir,               # output directory for prediction results
    threshold=0.3,
    output_prob_map=True,
    output_binary_map=True,
    output_depth_map=True,
    device="auto"
)
```

### Main Responsibilities
- Loads all model checkpoints from the model directory.
- Moves each model to the selected device (CPU/GPU).
- Generates the required feature layers (HPMF, ISI).
- Performs inference on 512×512 feature chips.
- Averages predictions from all models.
- Writes probability, binary, and depth rasters.
- Creates VRT mosaics for each enabled output type.

---

### Methods

#### `_set_output_directories()` and `_set_temporary_directories()`:
Creates a standardized directory layout for inference results. 
Only the subdirectories corresponding to the enabled output types are created:

- `probability_maps/` — continuous probability rasters
- `binary_maps/` — binary rasters
- `depth_maps/` — HPMF-based depth rasters
- `temp/` — intermediate files (removed automatically after processing)

#### `_create_output_layer()`
Runs tile-based multi-model inference:
- Splits the 2-channel feature raster into overlapping 512×512 tiles.
- Converts each tile to a PyTorch tensor.
- For each model:
  - Performs the model’s forward pass with gradient computation disabled.
  - Applies sigmoid activation function.
- Averages predictions across all models.
- Writes each tile back into the correct position in the output mosaic.
- Resamples the prediction raster back to the original DEM resolution.

#### `_output_probability_map(input_path, profile, output_array)`
- Saves the model’s continuous probability predictions as a float32 GeoTIFF.
- Updates the raster profile accordingly and writes the single-band probability map 
to the `probability_maps/` directory using the input DEM’s name as the filename prefix.

#### `_output_binary_map(input_path, profile, output_array)`
- Creates a binary ditch/no-ditch map from the probability raster using 
the user-defined threshold (self.threshold).
- Updates the raster profile accordingly and writes the single-band binary map 
to the `binary_maps/` directory using the input DEM’s name as the filename prefix.

#### `_output_depth_map(input_path, output_array)`
- Loads the corresponding HPMF reference and replaces no-data values with zero.
- Builds the ditch depth map by combining the probability output with the temporary HPMF raster.
- Removes all positive values to preserve only negative (depression) depths.
- Saves the resulting depth raster into the `depth_maps/` directory using the input DEM’s name 
as the filename prefix.

#### `_process_single_dem(dem_path)`
This method performs all steps required to transform one DEM input into its final probability, 
binary, and/or depth outputs:
- Opens the DEM and extracts spatial metadata and dimensions.
- Skips processing if the raster is smaller than 500×500 pixels.
- Generates the HPMF and ISI feature layers using utility functions and stores them in temporary files.
- Normalizes both features and applies a **2.4% upscale** to match the model’s expected resolution.
- Stacks the two normalized feature layers into a 2-channel array.
- Calls `_create_output_layer()` to perform tile-based model inference.
- Writes the selected output maps by invoking:
  - `_output_probability_map()`
  - `_output_binary_map()` (if enabled)
  - `_output_depth_map()` (if enabled)
- Removes intermediate temporary files tied to the processed DEM.

#### `_create_virtual_rasters()`
Creates VRT mosaic files for all output types that were enabled.
For each map category (probability, binary, depth), the method:

- Collects all .tif files in the corresponding output directory.
- Builds a GDAL VRT mosaic that references these rasters without duplicating data.
- Saves the VRT using a standardized filename:
  - ditch_probability_map.vrt
  - ditch_binary_map.vrt
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

### Output

After running inference, the script produces the following directory structure inside the specified output folder:

```
output_dir/
├── probability_maps/        (if enabled)
│   ├── dem_tile_001_ditch_probability.tif
│   ├── dem_tile_002_ditch_probability.tif
│   └── ...
│
├── binary_maps/             (if enabled)
│   ├── dem_tile_001_ditch_binary.tif
│   ├── dem_tile_002_ditch_binary.tif
│   └── ...
│
├── depth_maps/              (if enabled)
│   ├── dem_tile_001_ditch_depth.tif
│   ├── dem_tile_002_ditch_depth.tif
│   └── ...
│
└── temp/                    (removed automatically after processing)
    ├── hpmf_temp.tif
    └── isi_temp.tif
```

---

## Class: `Main`
Provides a **command-line interface (CLI)** for running model inference directly from the terminal.

### Arguments
| Argument          | Type                         | Default | Description                                                                          |
|-------------------|------------------------------|---------|--------------------------------------------------------------------------------------|
| `model_dir`       | Path                         | —       | Directory containing **one or more** trained DitchNet model checkpoints (`*.ckpt`).  |
| `input_dem_dir`   | Path                         | —       | Directory containing the DEM tiles (`.tif`) to be processed.                         |
| `output_dir`      | Path                         | —       | Directory where all inference results will be written.                               |
| `--threshold`     | float                        | `0.3`   | Probability threshold used to generate the binary map.                               |
| `--no_prob_map`   | flag                         | enabled | Disables saving of the probability map output.                                       |
| `--no_binary_map` | flag                         | enabled | Disables saving of the binary map output.                                |
| `--no_depth_map`  | flag                         | enabled | Disables saving of the depth map output.                                             |
| `--device`        | str (`cpu` / `cuda` / `auto`) | `auto`  | Specifies the computation device. `"auto"` selects GPU when available, otherwise CPU. |

---

## Example Usage
```bash
python inference.py   ./models/   ./input_DEMs   ./inference_output --threshold 0.1
```

Both **relative** and **absolute** paths are supported for all input and output arguments.  
This means you can run the program from any working directory without adjusting its internal path handling.

### Example Output (Console)
```
Using device: cuda

The following models will be used and their predictions will be averaged:
model_01.ckpt
model_02.ckpt

Probability map output: enabled
Binary map output: enabled (threshold: 0.3)
Depth map output: enabled

Running DitchNet inference on DEM files in: ./input_DEMs

Processing: dem_tile_001.tif
Processing: dem_tile_002.tif
Processing: dem_tile_003.tif
...

All predictions completed.
```

---

## Dependencies
- **GDAL**: builds VRT mosaics that merge tile-based outputs into seamless virtual rasters.
- **model.py**: defines the DitchNet architecture and enables loading the trained model checkpoint.
- **NumPy**: supports array manipulation for feature stacking, masking, and output raster creation.
- **PyTorch**: runs the trained DitchNet model and handles tensor operations on CPU or GPU.
- **Rasterio**: used for reading input DEMs, writing GeoTIFF outputs, and managing spatial metadata.
- **scikit-image**: provides the resize function used for resampling the prediction layer.
- **utils.py**: generates terrain feature layers (HPMF and ISI) and performs normalization required for inference.

The inference results serve as the final product of the DitchNet workflow and can be directly visualized 
or used for GIS-based ditch mapping and analysis.
