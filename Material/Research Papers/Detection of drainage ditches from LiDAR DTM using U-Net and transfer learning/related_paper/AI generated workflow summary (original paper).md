### Workflow (replicable protocol)
1. **Acquire ALS data**
   - Target ≥ **1–2 pts/m²** point density (our ALS data has 5pts/m².
   - Ensure consistent vertical accuracy and coverage over forested areas.

2. **Generate high-resolution DEM**
   - Build **0.5 m** DEM via TIN gridding (or equivalent).
   - Validate DEM quality (voids, artifacts).

3. **Compute high-pass median filter (HPMF)**
   - Apply HPMF (e.g., **11-cell kernel**).
   - Interpret: negative = depressions; positive = ridges.

4. **Prepare reference labels**
   - **Manually digitize** ditch centerlines with expert calibration (in our case Hytky 2023 data).
   - Convert to raster labels:
     - Buffer logic: tag pixels within **3 m** of lines **AND** with **HPMF < −0.075** as ditch.
     - Remove isolated speckles via **3-cell majority filter**.
   - Document labeling parameters for reproducibility.

5. **Create training chips**
   - Tile to **512 × 512 px** image/label pairs.
   - Discard chips with **<0.1% ditch pixels** to reduce extreme imbalance.

6. **Train segmentation model**
   - **Encoder–decoder CNN** with **Xception blocks**.
   - **Weighted cross-entropy** to handle imbalance.
   - Include **CRF layer** to smooth predictions.
   - Track metrics: **MCC**, κ, precision, recall.

7. **Evaluate & generalize**
   - Hold out ~**20%** of tiles for testing.
   - Test on **independent sites** (different ALS densities/landscapes).
   - Analyze error patterns (streams vs. ditches; geomorphic confounders).

8. **Deploy & scale**
   - Run inference (≈ **8.6 s/km²** on GTX 1080 Ti as a reference).
   - Produce probability maps and threshold as needed for vectorization.
   - Plan **transfer learning** if moving to new regions.

### Practical notes for replication
- Start with HPMF-only inputs for speed; add indices **only if** accuracy is insufficient.
- Use robust, imbalance-aware metrics (**MCC**) to avoid misleading overall accuracy.
- Maintain a **labeling handbook** with examples of edge cases to stabilize ground truth quality.

---

## Reference
Lidberg, W., Paul, S.S., Westphal, F., Richter, K.F., Lavesson, N., Melniks, R., Ivanovs, J., Ciesielski, M., Leinonen, A., & Ågren, A.M. (2023). *Mapping Drainage Ditches in Forested Landscapes Using Deep Learning and Aerial Laser Scanning*. Journal of Irrigation and Drainage Engineering, 149(3), 04022051. https://doi.org/10.1061/JIDEDH.IRENG-9796

