# Ditch Detection Project
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
## 📄 Description
This repository contains the full codebase for LiDAR preprocessing, training and testing a U-Net–based ditch detection model, running inference, performing ditch age determination, and a GUI that provides user-friendly access to all these functionalities.  
The work was completed as part of the Aalto University course **GIS-E6010 – Project Course**, in collaboration with the **Finnish Forest Centre**.


## 📁 Repository Structure

```
GIS_E6010_Project_Course_2025/
│
├── _archive/                       # Archived legacy scripts and experimental files
│
├── Documentation/                  # Full project documentation (pipelines, methods, usage)
│
├── src/                            # Main source code
│   │
│   ├── gui/                        # Standalone PySide6 GUI
│   │   ├── tabs/                   # GUI tab widgets
│   │   ├── utils/                  # Shared GUI utilities
│   │   ├── workers/                # Subprocess handlers for running scripts
│   │   ├── dem2ditch_gui.py        # Main script for running GUI
│   │   └── DEM2Ditch_gui.yml       # Conda environment file for GUI
│   │
│   ├── utils/                      # Utility functions used across scripts
│   │
│   ├── ditchnet_pytorch.yml        # Conda environment for model training/inference
│   ├── age_classification_vectors.py # Ditch age determination (first appearance, vector-based)
│   ├── find_new_ditches.py         # Ditch age determination (new vs old, raster-based)
│   ├── inference.py                # Run inference on DEM tiles
│   ├── model.py                    # Model definition
│   ├── preprocessing.py            # DEM preprocessing pipeline (HPMF, ISI…)
│   ├── test.py                     # Model evaluation
│   └── train.py                    # Model training script
│
├── .gitignore
└── README.md
```

## 🛠 Environment Setup and Usage

A complete and detailed installation guide and usage instructions are provided in the project [Documentation](Documentation).  
The documentation covers everything needed to run the project, including:

- full environment setup guide (Conda)
- how to run all scripts (preprocessing, training, testing, inference, age determination)
- examples, recommended parameters, and explanations of all configurable options, methods etc.

## Model Overview

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

## License
This project is licensed under the MIT License.  
See the [LICENSE](LICENSE) file for more details.

