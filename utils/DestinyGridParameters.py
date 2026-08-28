#Imports:
import numpy as np
import requests

#Functions:

def newlonlat_city(city_name):

    """
    It calculates the I4C reference longitude and latitude grid for a given city and gives the GitHub grid parameters as output.
    It's sum up one degree in each side of the 2D output grids to not lose data points in the interpolation. The rest of the grid parameters do not include the extra degree.
    
    Parameters:
    1) city_name (str): The name of the city for which to calculate the grid.  The city options are: 'Paris', 'Barcelona', 'Prague', 'Bergen', 'Hamburg', 'NewCastle'.   
    
    Returns:
    1) longitude_2d (numpy.ndarray): A 2D array of longitudes for the I4C grid points.
    2) latitude_2d (numpy.ndarray): A 2D array of latitudes for the I4C grid points.
    3) xfirst (float): The first value of the x coordinate.
    4) xend (float): The last value of the x coordinate.
    5) xsize (int): The number of grid points in the x direction.
    6) ysize (int): The number of grid points in the y direction.
    7) xincrement (float): The spacing between consecutive x points.
    8) yincrement (float): The spacing between consecutive y points.
    9) yfirst (float): The first value of the y coordinate.
    10) yend (float): The last value of the y coordinate.
    """

    #Define the domain of the city:
    if city_name=='Barcelona' or city_name=='Paris' or city_name=='Prague':
        domain= 'ALPX-3i-'
    elif city_name=='Bergen' or city_name=='Hamburg' or city_name=='NewCastle':
        domain= 'NSEA-3i-'
    else:
        print('The city name is not valid')
        return

    #Github repository with the grid variables for the interpolation:
    url="https://raw.githubusercontent.com/impetus4change/T32-CPRCM/refs/heads/main/grids-3i/"+domain+city_name+".grid"

    #It downloads the content of the file (grid variables) as text
    text = requests.get(url).text

    #Create an empty dictionary:
    grid = {}

    for line in text.splitlines(): #Loops through the file line by line
                                    #text.splitlines() splits the full text into individual lines
        key, value = line.split("=")#Splits each line at the '=' symbol
        key = key.strip()#Removes extra spaces before and after the key
        value = value.strip()#Removes extra spaces before and after the value

        #The url content is read as text, here we convert the numbers of the varibles into float or interger
        try:
            value = float(value) if "." in value else int(value)
        except ValueError:#If the value isn´t a number, for example lonlat, it doesn´t do nothing
            pass

        grid[key] = value #Stores the result in the dictionary

    # Save grid variables individually
    # grid_type = grid["gridtype"] #Gets the grid type
    x_size = grid["xsize"] #Gets the number of grid points in the x direction
    y_size = grid["ysize"]#Gets the number of grid points in the y direction
    x_first = grid["xfirst"]# Gets the first value of the x coordinate
    x_increment = grid["xinc"]# Gets the spacing between consecutive x points
    y_first = grid["yfirst"]# Gets the first value of the x coordinate
    y_increment = grid["yinc"]#Gets the spacing between consecutive y points

    #To not lose data points in the interpolation, the limits of the grid are expanded one degree in each side, so we sum up 1º 
    # to the first value and to the last value of the coordinates
    x_first_use=x_first-1
    y_first_use=y_first-1

    #Last value of the coordinates according to the GitHub grid parameters
    xend=x_first+(x_size-1)*x_increment
    yend=y_first+(y_size-1)*y_increment #We use (y_size - 1) because the first point is already y_first.

    #Expand the last value of the coordinates one degree
    x_end_use = xend + 1
    y_end_use = yend + 1


    ## Expand the size of the grid in each direction to keep the same spacing between points.
    x_size = round(((x_end_use) - (x_first_use)) / x_increment)
    y_size = round(((y_end_use) - (y_first_use)) / y_increment)#If the result is not an integer, it is rounded to the nearest integer, introducing a small error.

    longitude_expanded = (x_first_use) + np.arange(x_size) * x_increment #Creates the 1D longitude array
                                                            # (x_first + [0, 1, 2, ..., last x] * x_increment)
                                                            #Limits are expanded one degree in each side to not lose data points in the interpolation
    latitude_expanded = (y_first_use) + np.arange(y_size) * y_increment #Creates the 1D latitude array
                                                        # (y_first + [0, 1, 2, ..., last y] * y_increment)
                                                        #Limits are expanded one degree in each side to not lose data points in the interpolation

    return longitude_expanded, latitude_expanded, x_first, xend, x_size, y_size, x_increment, y_increment, y_first, yend


def crop_curvilinear(ds, x_first, xend, y_first, yend, lon_name="lon", lat_name="lat"):
    """
    This function crops a curvilinear dataset to a specified bounding box defined by the first and last values of the x and y coordinates.

    Parameters:
    1) ds (xarray.Dataset): The input curvilinear dataset to be cropped
    2) x_first (float): The first value of the x coordinate for cropping
    3) xend (float): The last value of the x coordinate for cropping
    4) y_first (float): The first value of the y coordinate for cropping
    5) yend (float): The last value of the y coordinate for cropping
    6) lon_name (str, optional): The name of the longitude coordinate in the dataset (default is "lon")
    7) lat_name (str, optional): The name of the latitude coordinate in the dataset (default is "lat")

    Returns:
    1) xarray.Dataset: The cropped dataset containing only the grid cells within the specified bounding box.
    """

    lon = ds[lon_name]
    lat = ds[lat_name]

    mask = ((lon >= x_first) & (lon <= xend) & (lat >= y_first) & (lat <= yend))
    mask = mask.compute()

    y_dim, x_dim = lon.dims

    y_indices = np.where(mask.any(dim=x_dim).values)[0]
    x_indices = np.where(mask.any(dim=y_dim).values)[0]

    if y_indices.size == 0 or x_indices.size == 0:
        raise ValueError("The condition does not select any grid cell in the domain.")

    return ds.isel({y_dim: slice(y_indices[0], y_indices[-1] + 1),
                    x_dim: slice(x_indices[0], x_indices[-1] + 1)})