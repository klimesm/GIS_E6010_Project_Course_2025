def find_new_ditches(new_layer_path, old_layer_path, output_dir,
                     threshold=0.5, tolerance_pixels=2, buffer_distance=3):
    import os
    import glob
    import rasterio
    from rasterio.merge import merge
    from rasterio.warp import reproject, Resampling
    from rasterio.features import shapes
    import numpy as np
    import geopandas as gpd
    from shapely.geometry import shape
    from scipy.ndimage import binary_dilation
    from qgis.utils import iface  

  
    # SETTINGS
   
    os.makedirs(output_dir, exist_ok=True)

    new_dir = os.path.dirname(new_layer_path)
    old_dir = os.path.dirname(old_layer_path)

    output_vector = os.path.join(output_dir, "new_ditches_vectorized.gpkg")

    # STEP 1: Merge new raster tiles

    print("\n[1/8] Merging new raster tiles...")
    new_tif_files = glob.glob(os.path.join(new_dir, "*.tif"))
    if not new_tif_files:
        raise FileNotFoundError(f"No new .tif files found in: {new_dir}")

    src_new = [rasterio.open(fp) for fp in new_tif_files]
    mosaic_new, new_trans = merge(src_new)
    new_meta = src_new[0].meta.copy()
    new_meta.update({
        "driver": "GTiff",
        "height": mosaic_new.shape[1],
        "width": mosaic_new.shape[2],
        "transform": new_trans
    })
    merged_new_path = os.path.join(output_dir, "merged_new.tif")
    with rasterio.open(merged_new_path, "w", **new_meta) as dest:
        dest.write(mosaic_new)
    print(f" New raster saved: {merged_new_path}")

    
    # STEP 2: Merge old raster tiles
  
    print("\n[2/8] Merging old raster tiles...")
    old_tif_files = glob.glob(os.path.join(old_dir, "*.tif"))
    if not old_tif_files:
        raise FileNotFoundError(f"No old .tif files found in: {old_dir}")

    src_old = [rasterio.open(fp) for fp in old_tif_files]
    mosaic_old, old_trans = merge(src_old)
    old_meta = src_old[0].meta.copy()
    old_meta.update({
        "driver": "GTiff",
        "height": mosaic_old.shape[1],
        "width": mosaic_old.shape[2],
        "transform": old_trans
    })
    merged_old_path = os.path.join(output_dir, "merged_old.tif")
    with rasterio.open(merged_old_path, "w", **old_meta) as dest:
        dest.write(mosaic_old)
    print(f" Old raster saved: {merged_old_path}")

    
    # STEP 3: Read merged rasters

    print("\n[3/8] Reading merged rasters...")
    with rasterio.open(merged_new_path) as new_src:
        new_data = new_src.read(1)
        new_transform = new_src.transform
        new_crs = new_src.crs
        new_profile = new_src.profile

    with rasterio.open(merged_old_path) as old_src:
        old_data = old_src.read(1)
        old_crs = old_src.crs
        old_transform = old_src.transform


    # STEP 4: Reproject old raster to match new
 
    print("\n[4/8] Reprojecting old raster to match new...")
    old_reproj = np.empty_like(new_data, dtype=np.float32)
    reproject(
        source=old_data,
        destination=old_reproj,
        src_transform=old_transform,
        src_crs=old_crs,
        dst_transform=new_transform,
        dst_crs=new_crs,
        resampling=Resampling.nearest
    )
    print(" Reprojection done.")

   
    # STEP 5: Identify new ditches (raster level)
   
    print("\n[5/8] Calculating differences...")
    new_bin = (new_data >= threshold).astype(np.uint8)
    old_bin = (old_reproj >= threshold).astype(np.uint8)
    old_dilated = binary_dilation(old_bin, iterations=tolerance_pixels)
    new_only = ((new_bin == 1) & (old_dilated == 0)).astype(np.uint8)

    new_only_raster = os.path.join(output_dir, "new_only_raster.tif")
    profile = new_profile
    profile.update(dtype=rasterio.uint8, count=1, compress='lzw')
    with rasterio.open(new_only_raster, "w", **profile) as dst:
        dst.write(new_only, 1)
    print(f" Difference raster saved: {new_only_raster}")

    
    # STEP 6: Convert new areas to vector
   
    print("\n[6/8] Converting raster to vector...")
    mask = new_only == 1
    shapes_gen = shapes(new_only, mask=mask, transform=new_transform)
    geoms = [shape(geom) for geom, val in shapes_gen if val == 1]

    if not geoms:
        print(" No new ditches found.")
        return None

    gdf = gpd.GeoDataFrame(geometry=geoms, crs=new_crs)
    gdf.to_file(output_vector, driver="GPKG")
    print(f" Vector layer saved: {output_vector}")

 
    # STEP 7: Remove overlaps near old ditches
   
    print("\n[7/8] Filtering features overlapping old ditches...")
    old_shapes_gen = shapes(old_bin, mask=old_bin == 1, transform=new_transform)
    old_geoms = [shape(geom) for geom, val in old_shapes_gen if val == 1]

    if not old_geoms:
        print(" No old ditches found – skipping filter.")
        return None

    old_gdf = gpd.GeoDataFrame(geometry=old_geoms, crs=new_crs)
    old_buffer_union = old_gdf.buffer(buffer_distance).unary_union

    gdf_filtered = gdf[~gdf.intersects(old_buffer_union)]

    filtered_path = os.path.join(output_dir, "new_ditches_vectorized_filtered.gpkg")
    gdf_filtered.to_file(filtered_path, driver="GPKG")
    print(f" Final 'new ditches only' layer saved: {filtered_path}")
    print(f"   ➜ Removed {len(gdf) - len(gdf_filtered)} overlapping features")

    
    # STEP 8: Add to QGIS
  
    iface.addVectorLayer(filtered_path, "New Ditches", "ogr")
    print("\nProcess completed successfully!")
    print(f" Results in: {output_dir}")
