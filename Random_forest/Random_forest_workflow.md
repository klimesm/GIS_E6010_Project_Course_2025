# Detailed Workflow for Ditch Detection Experiment

## 1. Input Data Preparation

**Point Cloud (National Land Survey of Finland, 5 p/m²):**
- Filter ALS point cloud to retain only ground returns.
- Generate a Digital Elevation Model (DEM, 0.5 m resolution).

**Vector ditch labels (Hytky 2023 data):**
- Convert digitized ditches into raster format aligned with DEM.
- Apply buffer (≈2–3 m, based on average ditch width).
- Refine rasterization using HPMF thresholds.
