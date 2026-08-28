# Urban and Rural Climate Analysis Using Regional Climate Models

This repository contains Python templates and tools for processing and analysing data from convection-permitting regional climate models in the context of Impetus For Change (I4C) project.

The results are generated through a standardised workflow, facilitating comparisons across different cities, variables, and simulations.

## Repository Content

The repository supports the following operations:

* Selection of climate files based on simulation characteristics.
* Cropping of the original model domain around a city.
* Regridding of the data onto a common regular grid.
* Generation and application of urban and rural masks.
* Calculation and representation of seasonal climatologies.
* Calculation of the minimum and maximum diary values from the dataset.
* Representation of minimum and maximum diary values climatologies.
* Calculation and representation of urban and rural diurnal cycles.
* Calculation and representation of the difference between urban and rural diurnal cycles.
* Analysis of daily extremes:
    * Identification and analysis of tropical nights.
    * Calculation of the 95th percentile of selected variables.
    * Generation of figures.

## workflow

The notebooks are listed below in the recommended order of use, together with a brief summary of their contents.

1. 'File_1_Interpolation_Catalogue.ipynb':
This notebook scans the NetCDF data directory, extracts the information contained in each directory level, creates a catalogue of the available files, and displays the unique options available for each parameter.

2. 'File_2_Crop_Interpolate_Grid_Save_In_New_file.ipynb':
This script regrids and crops `.nc` files with spatial `x`, `y`, `lon(x, y)`, and `lat(x, y)` coordinates onto a reference grid for each city in the context of the I4C project. This is necessary to compare data from different models on a common grid.

3. 'Readme_papermill.md':
Usage guide of how to use papermill to run the scripts with different simulation data from the terminal.

4. 'File_3_Urban_Rural_Selection.ipynb'
It calculates climatologies of the mean values, daily minima, and daily maxima, distinguishing between urban and rural grid cells defined by a spatial mask. It also computes the urban and rural diurnal cycles, as well as the difference between them, to analyse the temporal behaviour and urban–rural contrasts of the selected variable.

5. 'File_4_TropicalNights_95percentile.ipynb'
This notebook calculates the 95th percentile of daily maximum and minimum temperatures for a user-defined season. It generates spatial maps of the temporal mean and time-series plots showing the evolution of each indicator. The same spatial and temporal analyses are also performed for the annual number of tropical nights.

The notebook are in the folder 'notebooks', the papermill guide is in the upper level. The previous notebooks use functions defined in different files in the utils folder. Files 3 and 4 generate summary figures to facilitate the results interpretation.




## Repository Structure

```text
.
├── notebooks/
│   ├── File_1_InterpolationCatalogue.ipynb
│   ├── File_2_Crop_Interpolate_Grid_Save_In_New_file.ipynb
│   ├── File_3_Urban_Rural_selection.ipynb
│   └── File_4_TropicalNights_95percentile.ipynb
├── utils/
│   ├── DestinyGridParameters.py
│   ├── Urban_Rural_functions.py
│   ├── ExtremeFunctions.py
│   └── city_polygons_clean_file.gpkg
├── your_data/
└── README.md
└── README_papermill.md
└── environment.yml
```

If you run it, there will be generated 3 new folders in the upper directory level and one new folder in utils:
- I4C_CPRCM_CITY_DATA where the cropped and interpolated data will be stored with the I4C structure.
- mask_climatologies_diurnal_cycle_figures where the File 3 summary figures will be stored.
- extremes_figures where the File 4 summary figures will be stored.
- urclimask_results, in utils, where the urban and rural  masks where be stored.


## Requirements

The code is written in Python (version 3.6.8) and mainly uses the following libraries:

* `xarray`
* `sys`
* `xclim`
* `pathlib`
* `os`
* `glob`
* `io`
* `numpy`
* `pandas`
* `geopandas`
* `PIL`
* `matplotlib`
* `cartopy`
* `scipy`
* `xesmf`
* `urclimask`
* `request`
* `cf_xarray`
* `netCDF4`
* `h5netcdf`
* `scikit-image`
* `papermill`

## Installation

Creating an isolated environment to install the required dependencies is recommended.

Using Micromamba (you can substitude it by conda for miniconda or conda):

```bash
micromamba create -n climate-analysis python=<PYTHON_VERSION>
micromamba activate climate-analysis
```

The required dependencies can then be installed using:

```bash
micromamba install -c conda-forge \
    xarray \
    xclim \
    numpy \
    pandas \
    geopandas \
    pillow \
    matplotlib \
    cartopy \
    scipy \
    xesmf \
    esmpy \
    requests \
    cf_xarray \
    netcdf4 \
    h5netcdf \
    scikit-image \
    papermill
```

Finally, you have to install urclimask:

```
pip install git+https://github.com/FPS-URB-RCC/urclimask.git
```


## Configuration

Before running each notebooks, except the FILE 1, the simulation and analysis characteristics must be defined, directly in the files or using papermill in the terminal (see README_papermill).

For example:

```python
variable = "tas"
driving_model = "ERA5"
scenario = "evaluation"
member = "r1i1p1f1"
institution = "BCCR-UCAN"
model = "WRF451R-CI4C"
version = "v1-r1"
time_period = "1hr"
data_version = "v20240710"
city = "Paris"
```

The following parameters must also be configured:

* Path to the data catalogue (FILE 1).
* Directory containing the NetCDF files.
* Analysis period.
* Months included in the selected season.
* Thresholds used to define urban and rural grid cells.
* Output directories for figures and results.


## Licence
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Authors
Developed by Irene Morales Mena supervised by Ana Casanueva Vicente and Maria Dolores Frías Dominguez.

## Institution:
Santander meteorology group, University of Cantabria.

