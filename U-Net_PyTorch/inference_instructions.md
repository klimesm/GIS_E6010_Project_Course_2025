# DitchNet Inference Instructions

## ⚙️ Create a Conda Environment from `ditchnet_pytorch.yml`

1. Open **Anaconda Prompt** or **PowerShell**.  
2. Navigate to the folder containing `ditchnet_pytorch.yml`:  
   ```bash
   cd path\to\your\project
   ```
3. Create the environment:  
   ```bash
   conda env create -f ditchnet_pytorch.yml
   ```
4. Activate it:  
   ```bash
   conda activate ditchnet_pytorch
   ```

---

## Run the Inference Script

Before running the script, open Anaconda Prompt (or PowerShell) and navigate to the directory where inference.py, utils.py, the model file, and other project files are located.

For example:
1. Make sure your trained model checkpoint (`.ckpt`) and input DEM files are available.  
2. Run the script:  
   ```bash
   python inference.py <model_path> <input_dem_dir> <output_dir>
   ```
   Example:  
   ```bash
   python inference.py model.ckpt ./input_dems ./output
   ```

3. Optional arguments:
   ```
   --threshold <value>       Classification threshold (default: 0.5)
   --no_prob_map             Disable saving probability maps
   --no_class_map            Disable saving classified maps
   ```

---

## Output Structure

After running the script, the following folders will be created inside the specified `output_dir`:

```
output/
├── probability_maps/
├── classified_maps/
└── temp/                (temporary files, automatically deleted)
```
