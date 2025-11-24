# Conda Environment Setup Guide
To ensure stable, reproducible, and conflict-free execution of the ditch-detection workflow, this project uses a dedicated Conda environment, which isolates all required packages and guarantees that the GUI and backend scripts run consistently across systems. The following guide describes how to create, activate, and manage the environment.

## 1. Prerequisites

Ensure that Conda (Anaconda or Miniconda) is installed on your system.
You can verify this by running:

``` bash
conda --version
```

If the command returns a version number, Conda is installed.

## 2. Creating a New Environment from a YML File

To create a new Conda environment from an existing YML file, run:

``` bash
conda env create -f path/to/DEM2Ditch_env.yml
```

## 3. Activating the Environment

Activate the environment using:

``` bash
conda activate DEM2Ditch_env
```

## 4. Deactivating the Environment

When you are done, you can deactivate it with:

``` bash
conda deactivate
```

## 5. Listing All Environments

You can view available environments using:

``` bash
conda env list
```

## 6. Installing Packages

Once the environment is active, install packages with:

``` bash
conda install package-name
```

## 7. Removing an Environment

To delete an environment, use:

``` bash
conda remove -n DEM2Ditch_env --all
```
