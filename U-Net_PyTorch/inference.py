import argparse
from pathlib import Path
import shutil
import numpy as np

import torch

from skimage.transform import resize
import rasterio

from utils import create_hpmf_layer, create_isi_layer, create_feature_layer
from model import DitchNet


class DitchNetPredictor:
    def __init__(self, model, input_dem_dir, output_dir, threshold,
                 output_prob_map=True, output_class_map=True, device=None):

        if not output_prob_map and not output_class_map:
            raise ValueError('At least one of "output_prob_map" or "output_class_map" must be True.')

        self.input_dem_dir = Path(input_dem_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.threshold = threshold

        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)
        print(f"Using device: {self.device}")

        self.model = model.to(self.device)
        self.model.eval()

        self.create_prob_map, self.create_class_map = output_prob_map, output_class_map
        self.output_probability_dir, self.output_classified_dir = None, None
        self._set_output_directories()

        self.temp_dir, self.hpmf_temp, self.isi_temp = None, None, None
        self._set_temporary_directories()

    def _set_output_directories(self):
        if self.create_prob_map:
            self.output_probability_dir = self.output_dir / "probability_maps"
            self.output_probability_dir.mkdir(parents=True, exist_ok=True)

        if self.create_class_map:
            self.output_classified_dir = self.output_dir / "classified_maps"
            self.output_classified_dir.mkdir(parents=True, exist_ok=True)

    def _set_temporary_directories(self):
        self.temp_dir = self.output_dir / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        self.hpmf_temp = self.temp_dir / "hpmf_temp.tif"
        self.isi_temp = self.temp_dir / "isi_temp.tif"

    def _create_output_layer(self, feature_array):
        # Define the expected input and output raster dimensions.
        # The DEMs are processed as 2048x2048 grids, divided into 512x512 tiles.
        original_raster_size = 2048
        chip_size = 512

        # Allocate memory for the full 2048x2048 output raster
        output_array = np.empty((original_raster_size, original_raster_size), dtype=np.float32)

        # Loop over the raster in steps of chip_size to create non-overlapping chips
        for i in range(0, original_raster_size, chip_size):
            for j in range(0, original_raster_size, chip_size):

                # Extract a tile from the input features (2 channels: HPMF + ISI)
                feature_chip = feature_array[:, i:i + chip_size, j:j + chip_size]

                # Add batch dimension and convert to PyTorch tensor
                feature_chip = feature_chip[np.newaxis, :, :]
                feature_tensor = torch.from_numpy(feature_chip).float().to(self.device)

                # Run model inference in evaluation mode (no gradient calculation)
                with torch.no_grad():
                    predicted = self.model(feature_tensor)

                    # Apply sigmoid activation, move tensor to CPU, and convert to NumPy array
                    predicted = torch.sigmoid(predicted).squeeze().cpu().numpy()

                # Insert predicted tile back into the corresponding position
                output_array[i:i + chip_size, j:j + chip_size] = predicted

        # Resize the combined output to the final 2000x2000 DEM resolution
        output_array = resize(output_array, (2000, 2000), order=1, preserve_range=True, anti_aliasing=False)

        return output_array

    def _output_probability_map(self, input_path, profile, output_array):
        profile.update(dtype=rasterio.float32, count=1, nodata=None)
        with rasterio.open(self.output_probability_dir / f"{input_path.stem}_ditch_probability.tif", "w",
                           **profile) as dst:
            dst.write(output_array, 1)

    def _output_classified_map(self, input_path, profile, output_array):
        filtered_output_array = (output_array >= self.threshold).astype(np.uint8)

        profile.update(dtype=rasterio.uint8, count=1, nodata=None)
        with rasterio.open(self.output_classified_dir / f"{input_path.stem}_ditch_classified.tif", "w",
                           **profile) as dst:
            dst.write(filtered_output_array, 1)

    def _process_single_dem(self, dem_path):
        # Read the DEM file metadata (e.g., CRS, transform, resolution)
        with rasterio.open(dem_path) as src:
            profile = src.profile

        # Generate High-Pass Median Filter and Impoundment Size Index layers
        hpmf_array = create_hpmf_layer(dem_path, self.hpmf_temp)
        isi_array = create_isi_layer(dem_path, self.isi_temp)

        # Combine layers into a 2-channel feature array for the model
        feature_array = create_feature_layer(hpmf_array, isi_array)
        output_array = self._create_output_layer(feature_array)

        # Save probability and/or classified maps depending on user options
        if self.create_prob_map:
            self._output_probability_map(dem_path, profile, output_array)

        if self.create_class_map:
            self._output_classified_map(dem_path, profile, output_array)

        # Clean up temporary files created by WhiteboxTools
        self.hpmf_temp.unlink()
        self.isi_temp.unlink()

    def predict(self):
        print(f"Running DitchNet inference on DEM files in: {self.input_dem_dir}")

        dem_files = list(self.input_dem_dir.glob("*.tif"))
        if not dem_files:
            print("No DEM (.tif) files found — nothing to process.")
            shutil.rmtree(self.temp_dir)
            return

        for dem_path in dem_files:
            print(f"Processing: {dem_path.name}")
            self._process_single_dem(dem_path)

        shutil.rmtree(self.temp_dir)
        print(f"All predictions completed.")


class Main:
    def __init__(self):
        self.args = self._parse_arguments()

        model = DitchNet.load_from_checkpoint(self.args.model_path)
        self.predictor = DitchNetPredictor(model,
                                           self.args.input_dem_dir,
                                           self.args.output_dir,
                                           self.args.threshold,
                                           self.args.output_prob_map,
                                           self.args.output_class_map)
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
                            default=0.5,
                            help="Classification threshold for the output map.")

        parser.add_argument("--no_prob_map",
                            dest="output_prob_map",
                            action="store_false",
                            help="Disable saving of the probability map output (enabled by default).")

        parser.add_argument("--no_class_map",
                            dest="output_class_map",
                            action="store_false",
                            help="Disable saving of the classified map output (enabled by default).")

        return parser.parse_args()

    def run(self):
        self.predictor.predict()


if __name__ == "__main__":
    Main()
