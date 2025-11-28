# DEM2Ditch – GUI Setup Guide

This guide explains how to prepare the required environment and start the DEM2Ditch Graphical User Interface (GUI).

---

## Requirements

To run the DEM2Ditch – GUI, you need:

- **Python (tested with version 3.11)**
- **The PySide6 library**

These can be installed in any of the following ways:

- **Globally** on your computer  
- Inside a **virtual environment (venv)**  
- Inside a **Conda environment** (recommended)

#### Recommended: Conda Environment

We strongly recommend using Conda, as it is also used for all backend scripts. It provides a clean, isolated environment and avoids conflicts with other Python installations.

A ready-to-use environment file is provided in:
```
src/gui/DEM2Ditch_gui.yml
```

You can use this file to create the GUI environment by following the instructions in: **[conda_env_instructions](conda_env_instructions.md)**

## Running the GUI

Once the environment is created and activated (Python 3.11 + PySide6 installed), you can start the GUI by running the following script:

```bash
python dem2ditch_gui.py
```

It is important to run this script **within the full project folder**, not as a standalone file.  
The GUI relies on multiple additional Python modules and directories in the project structure,  
so the entire repository must be kept intact.

Make sure you run the command **inside the environment** where PySide6 is installed  
(e.g., the Conda environment created from `DEM2Ditch_gui.yml`).

After launching, the DEM2Ditch GUI window will appear, and you can continue with the processing workflow.

## Parameters and Settings

All parameters available in the GUI correspond directly to the parameters used in the underlying Python scripts.  
Their meaning, valid values, and detailed behavior are already described in the main project documentation.

For this reason, the individual parameters will not be described again here.  
The GUI simply provides a user-friendly interface for configuring the same options.

