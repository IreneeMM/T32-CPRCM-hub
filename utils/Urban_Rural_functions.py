# Libraries required to run the script:
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from matplotlib import font_manager

def months_or_season(month_list):
    """
    Given a list of month numbers (1-12), returns the season name
    if the list exactly matches one, otherwise returns the list
    of corresponding month names.

    Parameters: 
    1) month_list (List): List of numbers from 1 to 12. 
    Example: [1, 2, 12] correspond to january, february and december, winter.

    Returns:
    2) It returns a string containing the season name if the selected months correspond exactly to a season; otherwise, a string containing the names of the selected months.
    """
    # Correspondence between numbers, months and seasons:
    months = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December"
    }

    seasons = {
        frozenset({12, 1, 2}): "Winter",
        frozenset({3, 4, 5}): "Spring",
        frozenset({6, 7, 8}): "Summer",
        frozenset({9, 10, 11}): "Autumn"
    }

    # Convert the month list into an immutable set to remove duplicates and reorder of the months.
    input_set = frozenset(month_list)

    # If it exactly matches a season, return the season name
    if input_set in seasons:
        return seasons[input_set]

    # Otherwise, return the names of the selected months
    month_names = [months[month] for month in month_list]

    return ", ".join(month_names)

def variable_rural_urban(urban_file, rural_file, urmask, variable, city):
    """
    The function calculates the temporal mean of the urban and rural data and represents both fields in 
    the same figure, together with the urban mask boundary.

    Parameters:

    1) urban_file (xarray.DataArray): Data corresponding to the urban grid cells.
    2) rural_file (xarray.DataArray): Data corresponding to the rural grid cells.
    3) urmask (xarray.Dataset or xarray.DataArray): Urban–rural mask used to draw the mask boundary.
    4) variable (str): Name of the analysed variable, used in the colourbar label and figure title.
    5) city (str): Name of the analysed city, used in the figure title.

    Returns:
    1) The generated figure (matplotlib.figure.Figure)
    """

    #Obtaination of the subtitle:
    months_in_numbers = [int(m) for m in np.unique(urban_file.time.dt.month.values)]
    subtitle = months_or_season(months_in_numbers)

    # Variable's units:
    if variable == 'hurs':
        Variable_units = "% water vapour"
    elif variable == 'huss':
            Variable_units = "g/kg"
            urban_file = urban_file*1000
            rural_file = rural_file*1000 
    else:
        Variable_units = urban_file.attrs["units"]    

    # Set figure and axis:
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

    # Create a binary mask to obtain a continuous contour:
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


    cbar.set_label(f"{variable} ({Variable_units})")

    # Extreme type to complete the title
    if urban_file.attrs["extreme_type"] == "max":
        operation = "daily maximum"
    elif urban_file.attrs["extreme_type"] == "min":
        operation = "daily minimum"
    else:
        operation = ""

    #Set axis limits
    if city == 'Paris':
        ax.set_xlim(1.4, 3.3)
    elif city == 'Barcelona':
        ax.set_xlim(1.25, 3)
        ax.set_ylim(41, 42.2)
    elif city == 'Prague':
        ax.set_xlim(14, 15)
        ax.set_ylim(49.8, 50.4)

    #Labels and title:
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title(f"Urban and rural {operation} {variable} mean value per point with the urban mask boundary of {city}\n ({subtitle}) ")

    plt.show()
    return fig


# Function to get the diurnal cycle
def get_diurnal_cycle(var):
    """
    The function first calculates the spatial mean over the `x` and `y` dimensions. The resulting 
    values are then grouped by hour of the day and averaged over all available days.

    Parameters: 
    1) var (xarray.DataArray): Input DataArray with dimensions x, y, and time.

    Returns: 
    1) xarray.DataArray: Mean value of the variable for each available hour of the day.

    """
    # Spatial mean:
    diurnal_cycle = var.mean(dim='lat').mean(dim='lon')

    # # Transform time to datetime
    # diurnal_cycle = diurnal_cycle.assign_coords(
    #     time=np.array([
    #         np.datetime64(f"{t.year:04d}-{t.month:02d}-{t.day:02d}T{t.hour:02d}:{t.minute:02d}:{t.second:02d}")
    #         for t in diurnal_cycle.time.values
    #     ])
    # )

    # Promediate by hour of the day
    diurnal_cycle = diurnal_cycle.groupby('time.hour').mean(dim='time')

    return diurnal_cycle

def get_daily_min_or_max_fields(datarray, operation):
    """
    The function calculates the maximum or minimum in the temporal coordinate ('time')
    for each spatial point.

    Parameters: 
    1) datarray (xarray.DataArray): Urban or rural data with dimensions x, y, and time. 
    2) operation (str): Operation to perform: "minimum"` or `"maximum"`. 
    
    Returns: 
    1) xarray.DataArray: Daily spatial fields corresponding to the maximum or minimum at each spatial point.

    """
    ## Ensure that the operation is either "maximum" or "minimum"
    if operation not in {"minimum", "maximum"}:
        print("operation must be either 'minimum' or 'maximum'.")
    else: 
        # Perform the maximum or minimum operation
        if operation == "minimum":
            max_or_min = datarray.resample(time="1D").min(dim="time")
        else:
            max_or_min = datarray.resample(time="1D").max(dim="time")

    # Remove time steps where all values are NaN.
    max_or_min = max_or_min.dropna(dim="time", how="all")

    
    return max_or_min

def to_curvilinear(ds):
        """
        Convert a 1D (lat, lon) dataset into a curvilinear-style dataset
        with 2D (lat(y, x), lon(y, x)) as expected by urclimask.

        Parameters: 
        1) ds: xarray.Dataset with 1D (lat, lon) coordinates

        Returns:
        1) ds2: xarray.Dataset with curvilinear coordinates
        """

        # 2D grid obtention from 1D longitude and latitude coordinates:
        lon1d = ds["lon"].values
        lat1d = ds["lat"].values
        lon2d, lat2d = np.meshgrid(lon1d, lat1d)  # shape (lat, lon) -> (y, x)

        # Rename x, y by longitude and latitude:
        ds2 = ds.rename({"lat": "y", "lon": "x"})
        ds2 = ds2.drop_vars(["y", "x"])
        ds2 = ds2.assign_coords(
            lat=(("y", "x"), lat2d),
            lon=(("y", "x"), lon2d),
        )

        return ds2    

        
def save_figures(positioned_figures, output_path, info_text=None):
    """
    Save several Matplotlib figures as a single image arranged in a grid.

    Parameters:
    1) positioned_figures : list of tuples
        Each tuple must contain: (figure, row, column)
        Example:
        [(figures[0], 0, 0),
         (figures[2], 1, 0),
         (figures[3], 1, 1),
         (figures[1], 2, 0),
         (figures[4], 2, 1),
         (figures[5], 2, 1),]
    2) output_path: Path where the final image will be saved.
    3)info_text : Text added below the grid.  Optional.
    """

    # Fixed configuration
    dpi = 300
    font_size = 60
    margin = 60
    text_spacing = 25
    horizontal_gap = 20
    vertical_gap = 20

    if not positioned_figures:
        raise ValueError("No figures were provided.")

    image_positions = []

    # Convert each Matplotlib figure into a PIL image
    for fig, row, column in positioned_figures:

        if row < 0 or column < 0:
            raise ValueError(
                "Row and column indices must be non-negative."
            )

        # Skip empty or undefined figures
        if fig is None or len(fig.axes) == 0:
            continue

        #convert the figures to png
        with io.BytesIO() as buffer:
            fig.savefig(
                buffer,
                format="png",
                dpi=dpi,
                bbox_inches="tight",
            )

            buffer.seek(0)

            image = Image.open(buffer).convert("RGB")

        image_positions.append((image, row, column))

    if not image_positions:
        raise ValueError("No valid figures were provided.")

    # Determine the grid dimensions 
    nrows = max(row for _, row, _ in image_positions) + 1
    ncols = max(column for _, _, column in image_positions) + 1

    # Use the largest image dimensions as the common cell size
    cell_width = max(
        image.width for image, _, _ in image_positions
    )
    cell_height = max(
        image.height for image, _, _ in image_positions
    )

    grid_width = (
        ncols * cell_width
        + (ncols - 1) * horizontal_gap
    )

    grid_height = (
        nrows * cell_height
        + (nrows - 1) * vertical_gap
    )

    # Create the blank grid
    combined = Image.new(
        "RGB",
        (grid_width, grid_height),
        "white",
    )

    # Place each image in its specified position
    for image, row, column in image_positions:

        cell_x = column * (cell_width + horizontal_gap)
        cell_y = row * (cell_height + vertical_gap)

        # Centre the image within its cell
        x = cell_x + (cell_width - image.width) // 2
        y = cell_y + (cell_height - image.height) // 2

        combined.paste(image, (x, y))

    # Add optional text below the grid
    if info_text is not None:

        font_path = font_manager.findfont("DejaVu Sans")
        font = ImageFont.truetype(font_path, font_size)

        # Draw context used only to measure the text, not to render anything
        measuring_draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))

        text_bbox = measuring_draw.multiline_textbbox(
            (0, 0),
            info_text,
            font=font,
            spacing=text_spacing,
        )

        text_height = (
            text_bbox[3] - text_bbox[1]
            + 2 * margin
        )

        new_combined = Image.new(
            "RGB",
            (
                combined.width,
                combined.height + text_height,
            ),
            "white",
        )

        new_combined.paste(combined, (0, 0))

        draw = ImageDraw.Draw(new_combined)

        draw.multiline_text(
            (
                margin,
                combined.height + margin,
            ),
            info_text,
            fill="black",
            font=font,
            spacing=text_spacing,
        )

        combined = new_combined

    # Create the output directory if it does not exist
    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Save the final image
    combined.save(output_path)

    return combined