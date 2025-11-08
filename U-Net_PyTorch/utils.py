import numpy as np

from sklearn.preprocessing import MinMaxScaler
import tifffile as tiff
from skimage.transform import resize

from whitebox.whitebox_tools import WhiteboxTools
wbt = WhiteboxTools()
wbt.verbose = False


def minmax_normalized_image(image, no_data_value=0):
    if np.max(image) == np.min(image):
        return np.full(image.shape, no_data_value, dtype=np.float32)

    mask = np.isnan(image) | (image == -9999) | (image == -32768)
    valid = image[~mask]

    if valid.size == 0:
        return np.full(image.shape, no_data_value, dtype=np.float32)

    scaler = MinMaxScaler()

    scaled = np.zeros_like(image, dtype=np.float32)
    scaled[~mask] = scaler.fit_transform(valid.reshape(-1, 1)).flatten()
    scaled[mask] = np.mean(scaled[~mask])

    return scaled


def create_hpmf_layer(input_path, hpmf_temp_path):
    wbt.high_pass_median_filter(i=input_path, output=hpmf_temp_path, filterx=11, filtery=11)

    hpmf_array = tiff.imread(hpmf_temp_path)
    hpmf_array = minmax_normalized_image(hpmf_array, no_data_value=1)

    return hpmf_array


def create_isi_layer(input_path, isi_temp_path):
    wbt.impoundment_size_index(dem=input_path, damlength=6, out_max=isi_temp_path)

    isi_array = tiff.imread(isi_temp_path)
    isi_array = minmax_normalized_image(isi_array)

    return isi_array


def create_feature_layer(hpmf_array, isi_array, resampled_height, resampled_width):
    feature_array = np.stack((hpmf_array, isi_array), axis=0)
    feature_array = resize(feature_array, (2, resampled_height, resampled_width),
                           order=1, preserve_range=True, anti_aliasing=False)

    return feature_array
