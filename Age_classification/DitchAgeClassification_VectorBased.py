# Required libraries for geospatial data processing
# pip install geopandas rasterio shapely numpy pandas

import geopandas as gpd
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape
import numpy as np
import os

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
        bbox = (src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top)  # Get bounding box of the probability map

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




# Example call to main function (to be replaced with QGIS UI parameters)
# main(
#     r"Your path to probability map",
#     {
#         year1: ("Path to vector file 1", 'Layer name 1'),
#         year2: ("Path to vector file 2", 'Layer name 2')
#     },
#     r"Your output path"
# )
