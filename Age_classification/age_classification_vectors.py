# Required libraries for geospatial data processing
# pip install geopandas rasterio shapely numpy pandas

# Example command to run the script via command line:
# 
# python age_classification_vectors.py "path/to/probability_map.tif" 
# "2005:path/to/vector_2005.gpkg,layer_2005;2014:path/to/vector_2014.gpkg,layer_2014;
# 2020:path/to/vector_2020.gpkg,layer_2020;2025:path/to/vector_2025.gpkg,layer_2025" 
# "path/to/output.gpkg" --prob_threshold 0.5
#
# - Ensure each vector entry is formatted as `year:path,layer` and separated by semicolons.
# - Ensure paths containing spaces are enclosed in quotes.
# - You can adjust the probability threshold using `--prob_threshold {value}` (default is 0.5).
# - You can set the minimum overlap length using `--min_overlap_length {value}` (default is 10.0).
# - Adjust other parameters as needed by including their respective flags.

import geopandas as gpd
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape
import numpy as np
import os
import argparse  # Added import for argparse


# Main function to manage inputs and outputs
def main(probability_map_path, vector_layers, output_vector_path, prob_threshold=0.5, min_overlap_length=10.0):
    """Main function to classify ditch age based on probability map and vector data.

    :param probability_map_path: Path to the raster probability map
    :param vector_layers: Dictionary with year keys and file paths as values
    :param output_vector_path: Path where the output vector data will be saved
    :param prob_threshold: Threshold for probability map binarization
    :param min_overlap_length: Minimum intersection length required to consider vector data and probability map geometry as matched
    """
    # Binarize and vectorize the probability map
    probability_gdf = vectorize_probability_map(probability_map_path, prob_threshold)

    # Load vector data limited to the area covered by the probability map
    vector_data = load_vector_layers(vector_layers, probability_gdf, probability_map_path)

    # Identify the first appearance year by intersection length
    probability_gdf = find_first_appearance(probability_gdf, vector_data, min_overlap_length)

    # Ensure the output directory exists
    output_dir = os.path.dirname(output_vector_path)
    os.makedirs(output_dir, exist_ok=True)

    # Save the results to a GeoPackage file
    probability_gdf.to_file(output_vector_path, driver='GPKG')


def vectorize_probability_map(probability_map_path, threshold):
    """Convert a probability map into vector geometries by binarizing and vectorizing based on a threshold.

    :param probability_map_path: Path to the raster probability map
    :param threshold: Minimum probability to consider a feature present
    :return: GeoDataFrame with vectorized geometries and their spatial reference
    """
    with rasterio.open(probability_map_path) as src:
        probability = src.read(1)
        mask = probability > threshold  # Binarize the raster data
        transform = src.transform
        # Vectorize the binary mask
        shapes_generator = shapes(mask.astype(np.uint8), transform=transform)
        geometries = [shape(geom) for geom, value in shapes_generator if value == 1]
        crs = src.crs
        return gpd.GeoDataFrame({'geometry': geometries}, crs=crs)


def load_vector_layers(vector_layers, probability_gdf, probability_map_path):
    """Load vector layers, ensuring they are spatially limited to the probability map area and have the same CRS.

    :param vector_layers: Dictionary with year keys and file paths and layer names as values
    :param probability_map_path: Path to the raster probability map for spatial boundary limits
    :return: Dictionary with year keys and GeoDataFrame values
    """
    vector_data = {}
    with rasterio.open(probability_map_path) as src:
        bbox = (
        src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top)  # Get bounding box of the probability map

    for year, (path, layer) in vector_layers.items():
        gdf = gpd.read_file(path, layer=layer, bbox=bbox)  # Load geometries only within the bounding box
        if gdf.crs != probability_gdf.crs:
            gdf = gdf.to_crs(probability_gdf.crs)  # Convert CRS if it doesn't match
        vector_data[year] = gdf
    return vector_data


def find_first_appearance(probability_gdf, vector_data, min_overlap_length):
    """Determine the earliest intersection year based on minimum overlap length.

    :param probability_gdf: GeoDataFrame of vectorized probability map geometries
    :param vector_data: Dictionary with year keys and GeoDataFrame values of vectors
    :param min_overlap_length: Minimum required intersection length
    :return: Updated GeoDataFrame with 'first_appearance_year' attribute
    """
    probability_gdf['first_appearance_year'] = "Unknown"  # Set default as Unknown when no intersection found

    for geom_idx, geom in enumerate(probability_gdf.geometry):
        for year, gdf in sorted(vector_data.items()):
            # Check spatial index to quickly find bounding box matches
            possible_matches_index = list(gdf.sindex.intersection(geom.bounds))
            if not possible_matches_index:
                continue

            possible_matches = gdf.iloc[possible_matches_index]

            # Perform precise intersection among possible matches
            precise_matches = possible_matches[possible_matches.intersects(geom)]

            if precise_matches.empty:
                continue

            intersections = precise_matches.intersection(geom)
            valid_intersections = intersections[
                ~intersections.is_empty & (intersections.geom_type.isin(['LineString', 'MultiLineString']))
                ]

            if valid_intersections.empty:
                continue

            # Calculate total length of intersections
            total_intersecting_length = valid_intersections.length.sum()

            # If total intersecting length passes threshold, consider year as appearance
            if total_intersecting_length >= min_overlap_length:
                probability_gdf.at[geom_idx, 'first_appearance_year'] = year
                break

    return probability_gdf


# Function to parse dictionary argument from command line
def parse_vector_layers(vector_layers_str, delimiter=';'):
    """Helper function to parse vector layers dictionary from a string. Expected format is:
    'year1:path1,layer1;year2:path2,layer2' with semicolon as delimiter.

    :param vector_layers_str: String with dictionary-like data.
    :return: Parsed dictionary.
    """
    vector_layers = {}
    layers = vector_layers_str.split(delimiter)
    for layer in layers:
        try:
            year, data = layer.split(':', 1)  # Split on the first ':' only
            path, layer_name = data.rsplit(',', 1)  # rsplit to ensure only one split for path issue
            vector_layers[int(year)] = (path.strip(), layer_name.strip())
        except ValueError:
            raise ValueError(f"Invalid format: {layer}. Expected 'year:path,layer'.")
    return vector_layers


# CLI interface
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Classify ditch age based on probability map and vector data.")
    parser.add_argument("probability_map_path", type=str, help="Path to the raster probability map")
    parser.add_argument("vector_layers", type=str, help="Vector layers in form 'year1:path1,layer1 year2:path2,layer2'")
    parser.add_argument("output_vector_path", type=str, help="Path where the output vector data will be saved")
    parser.add_argument("--prob_threshold", type=float, default=0.5, help="Threshold for probability map binarization")
    parser.add_argument("--min_overlap_length", type=float, default=10.0,
                        help="Minimum intersection length required to consider vector data and probability map geometry as matched")

    args = parser.parse_args()

    # Parse vector layers argument
    vector_layers_dict = parse_vector_layers(args.vector_layers)

    # Call the main function with parsed arguments
    main(
        args.probability_map_path,
        vector_layers_dict,
        args.output_vector_path,
        prob_threshold=args.prob_threshold,
        min_overlap_length=args.min_overlap_length
    )



