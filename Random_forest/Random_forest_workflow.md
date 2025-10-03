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

## 3. Extract ditches with digital terrain indices (DTI) and calculate feature layers
**Sky View Factor (SVF): radius = 10 m (SAGA GIS)**
  - represents how much of the sky that is visible from a certain point on the ground
    
**Impoundment Index (dam height): dam length = 3 m (WhiteboxTools)**

**High Pass Median Filter (HPMF): window size = 4.5 m (WhiteboxTools)**

**Slope: degrees (WhiteboxTools)**

**Calculate 40 feature layers based on DTI:s** 

# 4. Split data into four sections
 Jaa aineisto lohkoihin 2x2 = 4 lohkoa
 3 lohkoa kehitykseen, yksi testaamiseen
 lohko 1 testaamiseen, lohkot 2-4 treenaamiseen
 --> ei varsinaisesti jaa aineistoa lohkoihin vaan tekee maskit, joiden perusteella pinot luodaan

# 5. Create feature stacks
  Treenidataksi valitaan kaikki pikselit lohkoista 2, 3 ja 4.
  
  Testidataksi valitaan kaikki pikselit lohkosta 1.
  
  Näin testipikselit eivät sijaitse lähellä treenipikseleitä → estetään “spatial leakage”.
  stack[:, train_mask] ottaa jokaiselta piirteeltä vain ne pikselit, jotka kuuluvat treenimaskiin.
  
  Tuloksen muoto on (40, N_train). .T kääntää sen muotoon (N_train, 40), mikä on scikit-learnin vaatima muoto: rivit = näytteet, sarakkeet = piirteet.
  
  y_train on vastaavat luokat (ojat/ei-ojat). Sama logiikka testille.
  
  Lopputulos:
  
  X_train = treeninäytteiden featurematriisi (rivit = pikselit, sarakkeet = 40 piirettä)
  
  y_train = treeninäytteiden luokat
  
  X_test, y_test vastaavat testijoukolle

# 6. Random forest
- Data pitää balansoida, koska ojapikseleitä on vain noin 7%, pitää selvittää voiko sen tehdä vain suoraan valitsemalla algoritmissa   class_weight="balanced",
  vai pitääkö erikseen balansoida

# 7. Testaus 
**en tiedä onko mittarit oikein, en ehinyt tarkastaa mitä mittareita tutkimuksessa oli käytetty **
- Precision (tarkkuus): kuinka suuri osa mallin “oja”-ennusteista on oikeasti ojia. Suuri arvo tarkoittaa, että vääriä positiivisia on vähän.

- Recall (herkkyys): kuinka suuri osa kaikista oikeista ojista löydettiin. Suuri arvo tarkoittaa, että malli löytää lähes kaikki ojat.

- Cohen’s kappa: mittaa mallin ja todellisuuden yhteensopivuutta satunnaisen arvauksen yli. Tämä on paperissa käytetty tärkein mittari.

- AUPRC (Area Under Precision-Recall Curve): ottaa huomioon, miten hyvin malli erottaa ojat ei-ojista kaikilla mahdollisilla todennäköisyyskynnyksillä. Hyödyllinen epätasapainoisessa datassa.





