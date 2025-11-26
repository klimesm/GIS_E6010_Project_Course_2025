# Ditch Detection Project

## 📄 Description
This repository contains the code, data pipeline and graphical user interface (GUI) developed for detecting ditches from LiDAR data, estimating ditch age and training the model. The project is based on machine learning with a U-Net model trained on high-resolution DEMs. The documentation is found from the link below https://github.com/klimesm/GIS_E6010_Project_Course_2025/tree/pytorch/U-Net_PyTorch/Documentation  

The work was completed as part of the Aalto University course GIS-E6010- Project Course, in collaboration with the Finnish Forest Centre.

**Repository Contents**

This repository includes:
- U-Net–based ditch detection model
- Training and inference pipeline
- Scripts for ditch age determination:
  - Old vs. new LiDAR data based probability map comparison
  - Classification using NSL ditch vector datasets
- A standalone GUI application (PySide6) for running the model and exporting results
- Documentation files
  - 

The repository contains the following key files and modules:
- __init__.py
- age_classification_vectors.py
- ditchnet_pytorch.yml
- find_new_ditches.py
- inference.py
- model.py
- preprocessing.py
- test.py
- train.py
- utils/tools.py
- utils/config.py
- utils/cli_args

**Example Usage**

Run ditch detection....
Use GUI how?

**Model Overview**

The ditch detection model is based on U-Net, inspired by the pipeline from Lidberg et al. (2023). The model is based on a CNN architecture, specifically designed for semantic segmentation. The model uses a U-Net architecture with an EfficientNet-B4 encoder. This encoder extracts multi-scale features and captures spatial contexts from the two input features derived from DEM: 

1. High-Pass Median Filter (HPMF)
2. Impoundment Size Index (ISI)
   
Then the decoder path upsamples these features to generate a pixel-wise probability map.

## Credits and References

As mentioned, this work is heavily inspired by the following study, which provided the foundation for our initial training pipeline:

Lidberg, W., Paul, S. S., Westphal, F., Richter, K. F., Lavesson, N., Melniks, R., Ivanovs, J., Ciesielski, M., Leinonen, A., & Ågren, A. M. (2023). Mapping drainage ditches in forested landscapes using deep learning and aerial laser scanning. https://doi.org/10.1061/JIDEDH.IRENG-9796 

## 👥 Authors

This project was developed by:

Ville Kauppinen <br>
Matěj Klimeš <br>
Nette Poutiainen <br>
Emma Aalto <br>
Janna Lappalainen <br>
Yuhan Nie

Aalto University
