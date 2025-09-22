# Mapping Drainage Ditches in Forested Landscapes Using Deep Learning and Aerial Laser Scanning — Structured Summary & Workflow

**Source:** Lidberg, W., Paul, S.S., Westphal, F., Richter, K.F., Lavesson, N., Melniks, R., Ivanovs, J., Ciesielski, M., Leinonen, A., & Ågren, A.M. (2023). *Mapping Drainage Ditches in Forested Landscapes Using Deep Learning and Aerial Laser Scanning*. Journal of Irrigation and Drainage Engineering, 149(3), 04022051. CC BY 4.0.

---

## 1) Introduction — short summary
Drainage ditches are widespread in boreal forests (notably in northern Europe) and were dug to improve tree growth by lowering groundwater levels. However, extensive ditching has altered wetland/soil hydrology and led to greenhouse gas emissions, nutrient loads to waters, and biodiversity loss. Despite their impact, ditch networks are poorly mapped, especially under forest canopy where optical imagery fails. Previous methods often target small, open areas. Combining airborne laser scanning (ALS) with deep learning enables mapping of fine‐scale ditches across large, forested regions.

---

## 2) Methods — detailed summary

### Study design
- Objective: detect drainage ditches via **semantic segmentation** using **ALS-derived topography**.
- Training data: **10 forest-dominated regions** across Sweden representing diverse soils, topographies, and land uses.

### Data collection & preprocessing
- ALS acquisition: Leica ALS80-HP; **1–2 points/m²**; altitude ~2,900 m.
- Tiling: **55 tiles** of **2.5 × 2.5 km** → total **344 km²**.
- DEMs: **0.5 m** resolution generated from ALS point clouds (TIN gridding).
- Filtering: **High-Pass Median Filter (HPMF)** applied to DEMs to emphasize local relief (negatives ≈ depressions such as ditches; positives ≈ ridges).

### Reference data (labels)
- Expert **manual digitization** of ditch centerlines with calibration meetings to harmonize edge cases.
- Ditch pixel definition used field-based mean ditch width (**2 m ± 1.3 m**).
- Pixels within **3 m** of digitized lines **AND** with **HPMF < −0.075** flagged as ditch pixels.
- Spurious isolated pixels removed by a **3-cell majority filter**.
- Total labeled network: **1,607 km** of ditches.

### Model & training
- Input: single-band **HPMF raster**.
- Architecture: **encoder–decoder CNN** with **Xception blocks**; output = pixel-wise ditch probability.
- Post-processing within the net: **Conditional Random Field (CRF)** layer to smooth label discontinuities.
- Loss: **weighted cross-entropy** (handles strong class imbalance).
- Samples: chips of **512 × 512 px** extracted from tiles; chips with <0.1% ditch pixels discarded → **2,367** chip pairs.
- Framework: **TensorFlow 2.6**.

### Evaluation
- Holdout: **11/55 tiles (20%)** reserved for testing (not used during training).
- External generalization tests (independent ALS datasets):
  - Sweden (**68 km²**, **20 pts/m²**)
  - Finland (**70 km²**, **5 pts/m²**)
  - Latvia (**25 km²**, **4 pts/m²**)
  - Poland (**44 km²**, **4 pts/m²**)
- Metrics for imbalanced data: **Recall**, **Precision**, **Cohen’s κ**, **Matthews Correlation Coefficient (MCC)** (primary), plus overall accuracy.

---

## 3) Results — detailed summary

### Swedish test tiles (holdout)
- **Overall accuracy:** ~**99%** of pixels.
- **Recall (ditch):** **86%**.
- **Precision:** **0.71**.
- **Cohen’s κ:** **0.78**.
- **MCC:** **0.78**.
- Frequent false positives were **natural stream channels** misclassified as ditches.

### External test sites
- Model generalized across the Baltic Sea region; **highest MCC in Poland**, **lowest in Latvia** (Sweden/Finland intermediate).
- Variation likely due to ALS density, landscape differences, and labeling procedures by different teams.

### Comparison to prior work
- Performance equals or exceeds most earlier studies, despite operating in larger, more complex forested terrain.
- Notable minimalism: strong performance using **one** topographic index (**HPMF**) only.

### Efficiency
- Inference speed ≈ **8.6 s per km²** on a **GeForce GTX 1080 Ti**, supporting large-area mapping.

---

## 4) Discussion — detailed summary

**Strengths**
- Scalable and accurate in **forested** landscapes; robust across multiple countries.
- **Computationally lean** (single index), enabling regional/national mapping on modest hardware.

**Limitations**
- Confusion between **natural streams** and **ditches** (ALS morphology can be similar).
- False positives in glacial/sedimentary features and ravines.
- Cross-country validation complicated by heterogeneous digitization standards (reference uncertainty).

**Future directions**
- Extend to **multi-class mapping** (natural streams + artificial ditches).
- Add auxiliary covariates (e.g., aerial photos, impoundment size index) if canopy/terrain complexity warrants.
- **Transfer learning** for local adaptation.

**Implications**
- Reliable ditch maps inform **hydrology**, **GHG budgeting**, **biodiversity**, **restoration**, and **forest operations** planning.

---

## 5) Conclusions — with workflow emphasis

The study demonstrates a **large-scale deep learning workflow** for ditch detection in forested regions using **ALS**. It achieves **high accuracy** (MCC ~0.78; overall pixel accuracy ~99%) with **minimal inputs** (HPMF only), and generalizes to multiple countries. This provides a practical basis for **national-scale ditch mapping** and management.

### Workflow (replicable protocol)
1. **Acquire ALS data**
   - Target ≥ **1–2 pts/m²** point density.
   - Ensure consistent vertical accuracy and coverage over forested areas.

2. **Generate high-resolution DEM**
   - Build **0.5 m** DEM via TIN gridding (or equivalent).
   - Validate DEM quality (voids, artifacts).

3. **Compute high-pass median filter (HPMF)**
   - Apply HPMF (e.g., **11-cell kernel**).
   - Interpret: negative = depressions; positive = ridges.

4. **Prepare reference labels**
   - **Manually digitize** ditch centerlines with expert calibration.
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

