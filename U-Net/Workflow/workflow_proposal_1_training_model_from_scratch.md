## 1. Input Data Preparation

**Point Cloud (National Land Survey of Finland, 5 p/m²):**
- Filter ALS point cloud to retain only ground returns.
- Generate a Digital Elevation Model (DEM, 0.5 m resolution).

**Vector ditch labels (Hytky 2023 data):**
- Convert digitized ditches into raster format aligned with DEM.
- Apply buffer (≈2–3 m, based on average ditch width).
- Refine rasterization using HPMF thresholds.

## 2. Feature Layer Derivation
- Compute **High-Pass Median Filter (HPMF)** from DEM (kernel ~11).

**Optional extension:**
- Derive additional topographic indices from DEM (e.g., impoundment size index).
- Combine them with HPMF as multiband inputs.

> **Note:** DEM itself is not used directly as model input, only derived indices are.

## 3. Training Data Construction
- Train/val/test split (e.g., 70/10/20%).
- Split HPMF (+optional indices) and labels into tiles (e.g., 512×512 px).
- Remove tiles with <0.1% ditch pixels.
- Pair each input tile with corresponding label tile.
- Consider augmentation (rotations, flips).

## 4. Model Development

- Encoder–decoder CNN (U-Net with Xception blocks).
- **Input:** HPMF (and optional indices).
- **Output:** pixel-wise ditch probability.
- Weighted cross-entropy loss for class imbalance.
- **CRF as the final trainable layer** to smooth discontinuities.

## 5. Evaluation & Validation

- Metrics: MCC, Cohen’s κ, recall, precision.
- Visual validation against reference ditch maps.
