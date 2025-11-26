# Conda Environment Setup Guide

This project uses **two separate Conda environments** to ensure stable, reproducible, and conflict-free execution:

1. **GUI Environment** – used for running the application’s graphical interface  
   → defined in `DEM2Ditch_gui.yml`

2. **Backend Environment** – used for model training, inference, and preprocessing  
   → defined in `ditchnet_pytorch.yml`

Separating the environments prevents dependency conflicts (e.g., PyTorch vs. GUI libraries), keeps the system clean, and makes the workflow easier to debug.

Also GUI environment is not necessary if you have python executable on your computer and have installed PySide6 library for example via pip.

This guide explains how to work with Conda, even if you have never used it before.

---

## 1. Prerequisites

Make sure you have **Conda** installed (Anaconda or Miniconda).  
Check by running:

```bash
conda --version
```

If a version number appears, Conda is installed.

### Where to Download Conda

You can install Conda by downloading either **Anaconda** (which includes many scientific packages by default) or **Miniconda** (a minimal installer recommended for lightweight environments). Both are available for Windows, macOS, and Linux. Download links and installation instructions can be found on the official website: https://docs.conda.io/en/latest/miniconda.html


---

## 2. Creating the Environments

### Create the GUI environment
```bash
conda env create -f path/to/DEM2Ditch_gui.yml
```

### Create the backend environment
```bash
conda env create -f path/to/ditchnet_pytorch.yml
```

After creation, Conda will list both environments.

---

## 3. Activating the Environments

### Activate the GUI environment
```bash
conda activate DEM2Ditch_gui
```

### Activate the backend environment
```bash
conda activate ditchnet_pytorch
```

Only one environment can be active at a time.

---

## 4. Deactivating an Environment

When you’re done:

```bash
conda deactivate
```

---

## 5. Listing All Conda Environments

To see all installed environments:

```bash
conda env list
```

The currently active environment will be marked with `*`.

---

## 6. Installing Additional Packages

Once an environment is active, install packages using:

```bash
conda install package-name
```

or using `pip` (only if necessary):

```bash
pip install package-name
```

---

## 7. Updating an Existing Environment

If the `.yml` file changes and you want to update your environment:

```bash
conda env update -f updated_file.yml --prune
```

`--prune` removes packages that are no longer listed.

---

## 8. Removing an Environment

To completely delete an environment:

### Remove the GUI environment
```bash
conda remove -n DEM2Ditch_gui --all
```

### Remove the backend environment
```bash
conda remove -n ditchnet_pytorch --all
```

---

## 9. Verifying Installation

To confirm everything works:

### GUI environment
```bash
conda activate DEM2Ditch_gui
python -c "import PySide6; print('GUI OK')"
```

### Backend environment
```bash
conda activate ditchnet_pytorch
python -c "import torch; print(torch.__version__)"
```

---

## Summary

| Purpose        | Environment name     | YML file                   |
|----------------|-----------------------|-----------------------------|
| GUI            | `DEM2Ditch_gui`       | `DEM2Ditch_gui.yml`         |
| Backend / ML   | `ditchnet_pytorch`    | `ditchnet_pytorch.yml`      |

Use the GUI environment for running the application and the backend environment for training, inference, utilities, and preprocessing.

