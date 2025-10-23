# Ditch Age and Condition Assessment Workflow

This workflow describes how to analyse **ditch age** and **condition** using trained machine learning models and LiDAR-derived terrain data.

---

## Requirements

- Python 3.10+
- `rasterio`, `numpy`, `matplotlib`, `whitebox`, `scikit-learn`, `joblib`
- Two LiDAR DEM datasets:
  - `DEM_old.tif` → older LiDAR (e.g. 2008–2019)
  - `DEM_new.tif` → recent LiDAR (e.g. 2020–present)
- Optional: NDVI raster (`ortokuva.tif`) from orthophotos or satellite imagery

---

## Overview

A trained Random Forest model is used to detect ditches from LiDAR DEMs.  
By comparing **old vs new predictions**, we identify **newly created** or **maintained** ditches.  
Additional indices (TWI, NDVI, depth) are used to evaluate the **condition and activity** of each ditch.

---

## Workflow Steps

### 1️ Ditch Prediction
Run the trained Random Forest model on both DEMs:
- `old_ditches.tif` ← from old DEM  
- `new_ditches.tif` ← from new DEM

Each pixel classified as **1 = ditch**, **0 = non-ditch**.

---

### 2️ Ditch Age Mapping
Compare results to identify **newly appearing ditches**:
- `new_only.tif` = pixels where `new_ditches == 1` and `old_ditches == 0`  
These represent **newly dug or reopened ditches**.

---

### 3️ Vegetation Cover (NDVI)
Calculate NDVI from orthophotos:

NDVI = (NIR - RED) / (NIR + RED)
- Low NDVI (<0.25) → bare soil → likely new ditch
- High NDVI (>0.5) → vegetated → old or inactive ditch

Use NDVI to refine new ditch predictions.

---

### 4. Condition Index

Combine multiple indicators to estimate ditch quality:
| Indicator | Description                              | Weight |
| --------- | ---------------------------------------- | ------ |
| Depth     | Local depression depth (DEM − local min) | 0.4    |
| TWI       | Topographic Wetness Index                | 0.4    |
| NDVI      | Vegetation / surface cover               | 0.2    |

Formula:
Condition = 0.4*(Depth_norm) + 0.4*(TWI_norm) + 0.2*(1 - NDVI)

- High value (≈1.0) → deep, wet, bare → good / active ditch
- Low value (≈0.0) → shallow, dry, vegetated → poor / old ditch

--- 
### 5️ Depth Classification

Categorize ditch depth for interpretation: (For example):
| Depth (m) | Class | Meaning   |
| --------- | ----- | --------- |
| 0.5–1     | 1     | Shallow   |
| 1–2       | 2     | Moderate  |
| 2–5       | 3     | Deep      |
| 5–10      | 4     | Very deep |

---

### Interpretation

| Indicator                | Meaning                         |
| ------------------------ | ------------------------------- |
| Detected in both DEMs    | Persistent ditch → *old/stable* |
| Detected only in new DEM | *New or re-opened ditch*        |
| High TWI + Deep          | *Wet and functional drainage*   |
| Low NDVI + Deep          | *Recently dug*                  |
| Shallow + Vegetated      | *Degraded / filled ditch*       |

