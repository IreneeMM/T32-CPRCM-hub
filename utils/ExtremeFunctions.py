import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from .Urban_Rural_functions import months_or_season


def figure(urban_file, rural_file, variable, city, urmask, season_months):
    """
    The function calculates the time mean of the urban and rural data and represents both fields on
    the same figure.

    Parameters:

    1) urban_file (xarray.DataArray): Data corresponding to the urban grid cells.
    2) rural_file (xarray.DataArray): Data corresponding to the rural grid cells.
    3) variable (str): Name of the analysed variable, used in the colourbar label and figure title.
    4) city (str): Name of the analysed city, used in the figure title.
    5) urmask (xarray.Dataset or xarray.DataArray): Urban–rural mask used to draw the mask boundary.
    6) season_months (list): List cointaining numbers from 1 to 12 corresponding to the months the data have.

    Returns:
    1) The generated figure (matplotlib.figure.Figure)
    """
    #Obtaination of the subtitle:
    subtitle = months_or_season(season_months)

    #Figure creation:
    fig, ax = plt.subplots(figsize=(8, 6), constrained_layout=True)

    # Time mean
    urban = urban_file.mean(dim="time")
    rural = rural_file.mean(dim="time")

    # Common colour limits for both datasets
    vmin = np.nanmin([urban.min().item(), rural.min().item()])
    vmax = np.nanmax([urban.max().item(), rural.max().item()])

    # Same colour scale for urban and rural
    im1 = ax.pcolormesh(
        urban.lon,
        urban.lat,
        urban,
        cmap="Reds",
        vmin=vmin,
        vmax=vmax,
        alpha=0.7,
        shading="auto",
        zorder=1
    )

    im2 = ax.pcolormesh(
        rural.lon,
        rural.lat,
        rural,
        cmap="Reds",
        vmin=vmin,
        vmax=vmax,
        alpha=0.7,
        shading="auto",
        zorder=2
    )

    # Extract the urban-rural mask
    if isinstance(urmask, xr.Dataset):
        mask = urmask["urmask"]
    else:
        mask = urmask

    # Create a binary mask to obtain a continuous contour: without it, the city contour will be discontinuous
    mask_contour = xr.where(mask == 1, 1, 0)

    # Urban boundary
    ax.contour(
        mask_contour.lon,
        mask_contour.lat,
        mask_contour,
        levels=[0.5],
        colors="black",
        linewidths=1.5,
        zorder=10
    )

    # Common colourbar
    cbar = plt.colorbar(
        im1,
        ax=ax,
        fraction=0.046,
        pad=0.04
    )

    # Variable units
    if urban_file.attrs["units"] == "1":
        Variable_units = "g/Kg"
    else:
        Variable_units = urban_file.attrs["units"]


    # colorbar title and title acoording to the data type:
    if urban_file.attrs["xclim_operation"] == "Tropical nights":
        cbar.set_label(f"Number of tropical nights")
        text_for_title = f'Mean number of urban and rural hot nights in {city} per spatial point per year'
    elif urban_file.attrs["xclim_operation"] == 'min_95percentile':
        cbar.set_label(f"95th percentile of minimum {variable} ({Variable_units})")  
        text_for_title = f"Mean 95th percentile of minimum {variable} in {city} per spatial point per year"
    elif urban_file.attrs["xclim_operation"] == 'max_95percentile':
        cbar.set_label(f"95th percentile of maximum {variable} ({Variable_units})")  
        text_for_title = f"Mean 95th percentile of maximum {variable} in {city} per spatial point per year"


    # Set the x and y axis limits for each city. It helps to visualise the city
    if city == 'Paris':
        ax.set_xlim(1.4, 3.3)
    elif city == 'Barcelona':
        ax.set_xlim(1.25, 3)
        ax.set_ylim(41, 42.2)
    elif city == 'Prague':
        ax.set_xlim(14, 15)
        ax.set_ylim(49.8, 50.4)

    # Labels, title and subtitle
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title(f"{text_for_title}\n ({subtitle}) ")

    plt.show()
    return fig
    
