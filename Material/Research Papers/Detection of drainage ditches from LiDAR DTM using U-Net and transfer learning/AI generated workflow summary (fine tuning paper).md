# Workflow Summary — Detection of Drainage Ditches from LiDAR DTM Using U-Net and Transfer Learning

**Source:** Virro, H., Kmoch, A., Lidberg, W., Muru, M., Chan, W.T., Moges, D.M., & Uuemaa, E. (2025). *Detection of drainage ditches from LiDAR DTM using U-Net and transfer learning*. Big Earth Data, 9(2), 243–264. https://doi.org/10.1080/20964471.2025.2491177

---

## Workflow Steps

1. **Preprocess LiDAR data**
   - Create LiDAR-derived **Digital Terrain Model (DTM)** from point cloud.
   - Resolution: 0.5–1 m, depending on dataset (Sweden: 0.5 m; Estonia: 1 m).

2. **Preprocess terrain data**
   - Apply **High-Pass Median Filter (HPMF)** to emphasize small-scale depressions and ridges.
   - Normalize HPMF values to [0,1].

3. **Generate reference labels**
   - Digitize ditch centerlines from HPMF and aerial data.
   - Rasterize lines with **buffer (≈3 m)**.
   - Classify pixels with **HPMF < –0.075** inside buffer as ditch pixels.

4. **Prepare datasets**
   - Split into **image-label tiles** (≈500 × 500 px, resampled to 512 × 512 for U-Net input).
   - Swedish dataset (≈1360 pairs) → used for **pre-training**.
   - Estonian dataset (≈72 pairs, from 18 km²) → used for **fine-tuning**.

5. **Fine-tuning**
   - Load pre-trained weights from Swedish models.
   - Train further on Estonian dataset (all configurations augmented).
   - Again train for **250 epochs**, extracting best-performing weights.

6. **Prediction & evaluation**
   - Apply fine-tuned model (best = **FT3A, kernel 3×3, augmented**, F1 = 0.766).
   - Use probability threshold (default 0.5; optionally lower to 0.1 for more complete ditch networks).
   - Evaluate using **precision, recall, F1-score** (per land use: peatland > arable > forest).

---

## Key Notes for Replication
- **Transfer learning** reduces the need for large local training datasets — only a small (18 km²) Estonian dataset was sufficient for adaptation.  
- **Augmentation** improves generalization but increases training time.  
- **Smaller kernels (3×3)** were sufficient; larger kernels did not improve accuracy.  
- Lower probability thresholds (e.g., 0.1) can recover more ditch continuity but risk more false positives.  

---

