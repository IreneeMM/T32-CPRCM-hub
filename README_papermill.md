**1. What does papermill do?**

Papermill executes an entire Jupyter notebook in a separate kernel, optionally replaces 
predefined parameter values, and saves the executed notebook as a new .ipynb file. 

- The original notebook is not modified. 
- The output notebook stores the executed code, printed output, figures, warnings, and 
errors. 
- Papermill executes all code cells sequentially, from top to bottom. 
- If the notebook contains a cell tagged as parameters, selected variables can be 
replaced with values provided from the terminal. Papermill does not modify the 
original tagged cell. Instead, it inserts an additional cell immediately below it and 
redefines only the variables specified in the terminal command. Because this new cell 
is executed after the original one, the new values are used throughout the rest of the 
notebook. Variables not specified in the terminal command keep their original values. 
- When execution finishes, the temporary kernel is closed and all Python objects stored 
in memory are lost. 
- After execution, the results can be reviewed by opening the generated output 
notebook.

**2. Check that papermill is installed in your environment**

First, activate the environment that contains Papermill and the packages required by the 
notebook: 

```bash
micromamba activate example_environment 
```

Then, check whether Papermill is installed in the active environment: 

```bash
papermill --version 
```
If Papermill is installed correctly, the command will display output similar to the following: 

```bash
2.7.0 from /nfs/home/gmeteo/moralesi/prueba_servidor/Y/envs/netcdf/lib/python3.14/ 
site-packages/papermill/cli.py (3.14.5) 
```

This output shows the installed Papermill version, the path where it is installed, and the 
Python version used by the active environment. If Papermill is not installed, the terminal will 
display an error similar to: 
```bash
bash: papermill: command not found 
```

To install Papermill in a Micromamba environment, run: 

```bash
micromamba install -n example_environment -c conda-forge papermill 
```

The `-n example_environment` option specifies the environment in which Papermill will be 
installed, while `-c conda-forge` specifies the package channel.

If the environment is already active, the environment name can be omitted: 

```bash
micromamba install -c conda-forge papermill 
```

For Conda, Miniconda, or Anaconda environments, use the equivalent `conda` command: 

```bash
conda install -n example_environment -c conda-forge papermill 
```

Once the installation is complete, confirm that Papermill is available: 

```bash
papermill --version
```

**3. Run a notebook from the terminal**

First, make sure the environment is active. 

The basic syntax is: 

```bash
papermill input_notebook.ipynb output_notebook.ipynb 
```

To replace one or more parameter values, use: 

```bash
papermill input_notebook.ipynb output_notebook.ipynb -p parameter_name1 parameter_value1 -p parameter_name2 parameter_value2 
```

You can replace as many parameters as necessary by repeating the ‘-p parameter_name 
parameter_value’ structure. 

For example, to execute the current interpolation notebook using Barcelona as the selected 
city, run: 

```bash
papermill File_2_Crop_Interpolate_Grid_save_In_New_file.ipynb executed.ipynb -p city Barcelona
```

File safety: 
- Use a different output filename from the input notebook. This keeps the 
parameterized execution separate from the notebook used as the template. 
- Use a different output filename for each execution to avoid overwriting previous 
results. 

Alternative: 
Papermill can also be run without activating the environment first by placing ‘micromamba run -n example_environment’ before the command. 

```bash
micromamba run -n example_environment papermill input.ipynb output.ipynb
```

**4. Viewing the results**

After the execution is complete, you can visualize the results opening the generated file. 