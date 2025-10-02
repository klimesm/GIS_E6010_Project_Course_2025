# Detailed Workflow for Ditch Detection Experiment

## Data and Software Requirements
**Input data:**
  - LiDAR ground-classified point cloud (~20 pts/m²) or DEM at 0.5 m resolution
  - Manually digitised ditch vector data for training and evaluation
    
**Software:**
  - LAStools (ground classification, DEM generation)
  - SAGA GIS (Sky View Factor)
  - WhiteboxTools (Impoundment Index, HPMF)
  - ArcGIS Pro (slope, hillshade)
  - Python (rasterio, numpy, scikit-learn, scikit-image, OpenCV, scipy)


## 1. Create DEM 

**Point Cloud (National Land Survey of Finland, 5 p/m²):**
- Filter ALS point cloud to retain only ground returns.
- Generate a Digital Elevation Model (DEM, 0.5 m resolution).


## 2. Digitise the Ground Truth Labels (Hytky 2023 data)
**Rasterise the vector layer (Hytky 2023)  with a resolution of 0.5 ∗ 0.5 m for use as a ground-truth for ditch detector**
**To ensure that all pixels are labelled correctly, label all pixels within three pixels (1,5m) as ditch**
  -> Produces labels with width of 3,5m
  - Since ditch widths vary (0.5–3.5 m), this widening does not perfectly represent every ditch, but it ensures that most ditch pixels are covered.
    
**To prepare for later evaluation, convert the raster labels into evaluation grid cells:**  
  - Divide the map into 6 × 6 pixel blocks (3 m × 3 m).  
  -> A block is labelled as ditch if at least 25% (≥9/36) of its pixels are ditch. 

## 3. Extract ditches with digital terrain indices
**Sky View Factor (SVF): radius = 10 m (SAGA GIS)**
  - represents how much of the sky that is visible from a certain point on the ground
    
**Impoundment Index (dam height): dam length = 3 m (WhiteboxTools)**

**High Pass Median Filter (HPMF): window size = 4.5 m (WhiteboxTools)**

**Slope: degrees (WhiteboxTools)**

Jaa alue alialueisiin

Tee tilallinen jako (esim. 21 lohkoa ≈196 ha/lohko).

Varaa 10 lohkoa kehitysvaiheeseen (piirteiden ideointi, kynnysten viritys).

Pidä 11 lohkoa täysin erillään loppuarviointiin; käytä näitä K=11 -CV:ssä. [4][5]



Feature engineering ja malli

Laske valitut piirteet per alialue (ettei reuna-efekteistä vuoda).

Kouluta RF, tee undersampling treenille (ojat + lähipikselit, satunnaisotanta ei-ojista). [8][9]



Arvioi

K=11 CV niillä 11 pidetyllä lohkolla; raportoi esim. Cohenin κ. [4][5]



