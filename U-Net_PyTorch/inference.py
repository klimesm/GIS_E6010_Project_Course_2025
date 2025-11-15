import argparse

import torch

from pathlib import Path
import shutil
import numpy as np

from skimage.transform import resize
import rasterio

from utils import (minmax_normalized_image,
                   create_hpmf_layer,
                   create_isi_layer,
                   create_feature_layer)

from model import DitchNet

from osgeo import gdal
gdal.UseExceptions()


class Predictor:
    def __init__(self, model, input_dem_dir, output_dir, threshold=0.3,
                 output_prob_map=True, output_class_map=True, output_depth_map=True,
                 device="auto"):

        if not output_prob_map and not output_class_map and not output_depth_map:
            raise ValueError('At least one of "output_prob_map", "output_class_map" or "output_depth_map" must be True.')

        # Define and prepare directories
        self.input_dem_dir = Path(input_dem_dir).resolve()
        self.output_dir = Path(output_dir).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.threshold = threshold

        # Auto-select computation device
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"

        self.device = torch.device(device)
        print(f"\nUsing device: {self.device}\n")

        # Load model for inference
        self.model = model.to(self.device)
        self.model.eval()

        # Output mode flags
        self.create_prob_map = output_prob_map
        self.create_class_map = output_class_map
        self.create_depth_map = output_depth_map

        # Initialize output and temp directories
        self.output_probability_dir, self.output_classified_dir, self.output_depth_dir = None, None, None
        self._set_output_directories()

        self.temp_dir, self.hpmf_temp, self.isi_temp = None, None, None
        self._set_temporary_directories()

        self.invalid_inputs = []

    def _set_output_directories(self):
        # Create subdirectories only for the enabled output types
        if self.create_prob_map:
            print("Probability map output: enabled")
            self.output_probability_dir = self.output_dir / "probability_maps"
            self.output_probability_dir.mkdir(parents=True, exist_ok=True)

        if self.create_class_map:
            print(f"Classified map output: enabled (threshold: f{self.threshold})")
            self.output_classified_dir = self.output_dir / "classified_maps"
            self.output_classified_dir.mkdir(parents=True, exist_ok=True)

        if self.create_depth_map:
            print("Depth map output: enabled")
            self.output_depth_dir = self.output_dir / "depth_maps"
            self.output_depth_dir.mkdir(parents=True, exist_ok=True)

    def _set_temporary_directories(self):
        # Create temporary working directory for intermediate raster products
        self.temp_dir = self.output_dir / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        self.hpmf_temp = self.temp_dir / "hpmf_temp.tif"
        self.isi_temp = self.temp_dir / "isi_temp.tif"

    def _create_output_layer(self, feature_array, orig_height, orig_width, resampled_height, resampled_width):
        chip_size = 512

        output_array = np.empty((resampled_height, resampled_width), dtype=np.float32)

        # Iterate over the raster in 512×512 tiles, last tiles may overlap to fully cover the image
        for i in range(0, resampled_height, chip_size):
            start_i = min(i, resampled_height - chip_size)
            for j in range(0, resampled_width, chip_size):
                start_j = min(j, resampled_width - chip_size)

                # Extract 2-channel feature tile (HPMF + ISI)
                feature_chip = feature_array[:, start_i:start_i + chip_size, start_j:start_j + chip_size]

                # Add batch dimension and send to device
                feature_chip = feature_chip[np.newaxis, :, :]
                feature_tensor = torch.from_numpy(feature_chip).float().to(self.device)

                # Run model inference in evaluation mode (no gradient calculation)
                with torch.no_grad():
                    predicted = self.model(feature_tensor)

                    # Apply sigmoid activation, move tensor to CPU, and convert to NumPy array
                    predicted = torch.sigmoid(predicted).squeeze().cpu().numpy()

                # Place prediction back into the output mosaic
                output_array[start_i:start_i + chip_size, start_j:start_j + chip_size] = predicted

        # Resample back to the original DEM resolution
        output_array = resize(output_array, (orig_height, orig_width), order=1, preserve_range=True, anti_aliasing=False)

        return output_array

    def _output_probability_map(self, input_path, profile, output_array):
        # Save continuous probability map
        profile.update(dtype=rasterio.float32, count=1, nodata=None)
        output_file = self.output_probability_dir / f"{input_path.stem}_ditch_probability.tif"
        with rasterio.open(output_file, "w", **profile) as dst:
            dst.write(output_array, 1)

    def _output_classified_map(self, input_path, profile, output_array):
        # Convert probabilities to binary classification using threshold
        filtered_output_array = (output_array >= self.threshold).astype(np.uint8)

        # Save binary classified map
        profile.update(dtype=rasterio.uint8, count=1, nodata=None)
        output_file = self.output_classified_dir / f"{input_path.stem}_ditch_classified.tif"
        with rasterio.open(output_file, "w", **profile) as dst:
            dst.write(filtered_output_array, 1)

    def _output_depth_map(self, input_path, output_array):
        with rasterio.open(self.hpmf_temp) as src:
            hpmf_ref = src.read(1)
            profile = src.profile

        # Use HPMF depth where ditch probability > 0.1, replacing no-data with 0
        hpmf_ref[hpmf_ref == -9999] = 0
        output_array = np.where(output_array > 0.1, hpmf_ref, 0)

        # Force all positive elevations to 0 to keep only negative HPMF values (depressions)
        output_array[output_array > 0] = 0

        # Save HPMF depth map
        output_file = self.output_depth_dir / f"{input_path.stem}_ditch_depth.tif"
        with rasterio.open(output_file, "w", **profile) as dst:
            dst.write(output_array, 1)

    def _process_single_dem(self, dem_path):
        with rasterio.open(dem_path) as src:
            orig_height = src.height
            orig_width = src.width
            profile = src.profile

        if orig_height < 500 or orig_width < 500:
            print(f"Input image {dem_path.name} is too small — minimum size is 500x500 pixels.")
            self.invalid_inputs.append(dem_path.name)
            return

        # Generate feature layers (HPMF and ISI) and normalize them
        hpmf_array = minmax_normalized_image(create_hpmf_layer(dem_path, self.hpmf_temp), no_data_value=1)
        isi_array = minmax_normalized_image(create_isi_layer(dem_path, self.isi_temp), no_data_value=0)

        # Slight upscaling to align with expected model resolution
        resampled_height = int(orig_height + (orig_height * 0.024))
        resampled_width = int(orig_width + (orig_width * 0.024))

        # Stack normalized features and perform model inference
        feature_array = create_feature_layer(hpmf_array, isi_array, resampled_height, resampled_width)
        output_array = self._create_output_layer(feature_array, orig_height, orig_width,
                                                 resampled_height, resampled_width)

        # Write selected outputs
        if self.create_prob_map:
            self._output_probability_map(dem_path, profile, output_array)

        if self.create_class_map:
            self._output_classified_map(dem_path, profile, output_array)

        if self.create_depth_map:
            self._output_depth_map(dem_path, output_array)

        # Remove temporary files
        for temp in (self.hpmf_temp, self.isi_temp):
            if temp.exists():
                temp.unlink()

    def _create_virtual_rasters(self):
        # Build VRT mosaics from generated output rasters
        if self.create_prob_map:
            depth_raster_files = [raster_name for raster_name in self.output_probability_dir.glob("*.tif")]

            vrt_path = self.output_probability_dir / "ditch_probability_map.vrt"
            gdal.BuildVRT(vrt_path, depth_raster_files)

        if self.create_class_map:
            depth_raster_files = [raster_name for raster_name in self.output_classified_dir.glob("*.tif")]

            vrt_path = self.output_classified_dir / "ditch_classified_map.vrt"
            gdal.BuildVRT(vrt_path, depth_raster_files)

        if self.create_depth_map:
            depth_raster_files = [raster_name for raster_name in self.output_depth_dir.glob("*.tif")]

            vrt_path = self.output_depth_dir / "ditch_hpmf_depth_map.vrt"
            gdal.BuildVRT(vrt_path, depth_raster_files)

    def predict(self):
        print(f"\nRunning DitchNet inference on DEM files in: {self.input_dem_dir}\n")

        dem_files = list(self.input_dem_dir.glob("*.tif"))
        if not dem_files:
            print("No DEM (.tif) files found — nothing to process.")
            if self.output_probability_dir.exists():
                shutil.rmtree(self.output_probability_dir)

            if self.output_classified_dir.exists():
                shutil.rmtree(self.output_classified_dir)

            if self.output_depth_dir.exists():
                shutil.rmtree(self.output_depth_dir)

            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)

            return

        # Process all input DEMs
        for dem_path in dem_files:
            print(f"Processing: {dem_path.name}")
            self._process_single_dem(dem_path)

        self._create_virtual_rasters()

        # Remove the temporary working directory
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

        print(f"\nAll predictions completed.")

        # Report skipped files
        if self.invalid_inputs:
            print(f"\nThe following input files failed to process:")
            for dem_name in self.invalid_inputs:
                print(dem_name)


class Main:
    def __init__(self):
        self.args = self._parse_arguments()
        model = DitchNet.load_from_checkpoint(self.args.model_path)
        self.predictor = Predictor(model,
                                   self.args.input_dem_dir,
                                   self.args.output_dir,
                                   threshold=self.args.threshold,
                                   output_prob_map=self.args.output_prob_map,
                                   output_class_map=self.args.output_class_map,
                                   output_depth_map=self.args.output_depth_map,
                                   device=self.args.device)
        self.run()

    @staticmethod
    def _parse_arguments():
        parser = argparse.ArgumentParser(description="Generate ditch probability and classification maps "
                                                     "from DEM data using a trained DitchNet model.")

        parser.add_argument("model_path", help="Path to the trained DitchNet model (.ckpt file).")
        parser.add_argument("input_dem_dir", help="Directory containing DEM files (.tif) to process.")
        parser.add_argument("output_dir", help="Directory where output maps will be saved.")

        parser.add_argument("--threshold",
                            type=float,
                            default=0.3,
                            help="Classification threshold for the output map.")

        # Optional flags to disable specific output types
        parser.add_argument("--no_prob_map",
                            dest="output_prob_map",
                            action="store_false",
                            help="Disable saving of the probability map output (enabled by default).")

        parser.add_argument("--no_class_map",
                            dest="output_class_map",
                            action="store_false",
                            help="Disable saving of the classified map output (enabled by default).")

        parser.add_argument("--no_depth_map",
                            dest="output_depth_map",
                            action="store_false",
                            help="Disable saving of the depth map output (enabled by default).")

        parser.add_argument("--device",
                            choices=["cpu", "cuda", "auto"],
                            default="auto",
                            help='Computation device: "cpu", "cuda", or "auto" (automatically detect GPU if available).')

        return parser.parse_args()

    def run(self):
        self.predictor.predict()


if __name__ == "__main__":
    Main()
