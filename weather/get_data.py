from typing import Tuple
import pandas as pd
from math import pi, tan, log, cos, pow, ceil
import numpy as np
from numba import njit
from scipy.spatial import cKDTree
from pydantic import BaseModel
from typing import List, Tuple
import json
import logging as logg


logg.info("Setting start...")
# Variable for converting from lat,lon to grid
RAD = 6371.00877 # Earth's radius
GRID = 5.0       # Grid spacing
SLAT1 = 30.0     # Projection lat 1 (degrees)
SLAT2 = 60.0     # Projection lat 2 (degrees)
OLON = 126.0     # Reference lon (degrees)
OLAT = 38.0      # Reference lat (degrees)
XO = 43          # Reference X cordinate
YO = 136         # Reference Y cordinate

# Precomputed values
DEGRAD = pi / 180.0
re = RAD / GRID
slat1 = np.radians(SLAT1)
slat2 = np.radians(SLAT2)
olon = np.radians(OLON)
olat = np.radians(OLAT)
sn = tan(pi * 0.25 + slat2 * 0.5) / tan(pi * 0.25 + slat1 * 0.5)
sn = log(cos(slat1) / cos(slat2)) / log(sn)
sf = tan(pi * 0.25 + slat1 * 0.5)
sf = pow(sf, sn) * cos(slat1) / sn
ro = tan(pi * 0.25 + olat * 0.5)
ro = re * sf / pow(ro, sn)

# csv file load
lat_lon_code = pd.read_csv("weather/lat_lon_code.csv")

# Convert to radian
lats = np.radians(lat_lon_code['lat'].values.astype(float))
lons = np.radians(lat_lon_code['lon'].values.astype(float))
codes = lat_lon_code['code'].values.astype(str)

# Convert to 3D sphere coordinate
x = RAD * np.cos(lats) * np.cos(lons)
y = RAD * np.cos(lats) * np.sin(lons)
z = RAD * np.sin(lats)

# cKDTree is comming!!
#
#    -\_-| \  \_/
#     -\\/ / _/-
#      -\_//_/
#        | /
#        | |
#       //\|\
#
tree = cKDTree(np.column_stack([x, y, z]))
# 입력 모델 (pydantic)

logg.info("Setting end!")

@njit
def latlon_to_grid(lat: float, lon: float,
                   re: float, sf: float, sn: float, ro: float,
                   XO: float, YO: float, olon: float) -> Tuple[int, int]:
    ra = np.tan(np.pi * 0.25 + lat * DEGRAD * 0.5)
    ra = re * sf / np.power(ra, sn)
    theta = lon * DEGRAD - olon
    if theta > np.pi:
        theta -= 2.0 * np.pi
    if theta < -np.pi:
        theta += 2.0 * np.pi
    theta *= sn

    x = int(ra * np.sin(theta) + XO + 0.5)
    y = int(ro - ra * np.cos(theta) + YO + 0.5)

    return (x, y)

def combert_latlon_to_grid( lat, lon ) -> Tuple[int,int]:
    '''
    Change latitude and longitude to Korean weather grid coordinates.

    Param:
        lat : float
            current latitude
        lon : float
            current longitude
    return:
        grid : Tuple[int, int]
            Index[0] : grid xpos
            Index[1] : grid ypos
    '''
    return latlon_to_grid(lat,lon,re,sf,sn,ro,XO,YO,olon) 

@njit
def get_efficient_params_vil(hour, day):
    today_data_num = (24 - (hour + 1) % 24) * 12
    full_index = today_data_num + 290 * day
    if hour < 6:
        full_index += 2
    elif hour < 15:
        full_index += 1 

    # If the full index is less than or equal to 290, return the first page and the full index
    if full_index <= 290:
        return 1, 0, full_index, 0, 0
    page = int(ceil(full_index / 290))
    back_padding = page * 290 - full_index
    front_padding = full_index - (page-1) * 290 

    return page , (1 if back_padding else 0) , 290 , front_padding, back_padding    

@njit
def get_3Dcoordinate(lat:float,lon:float):
    lat_r = np.radians(lat)
    lon_r = np.radians(lon)
    qx = RAD * np.cos(lat_r) * np.cos(lon_r)
    qy = RAD * np.cos(lat_r) * np.sin(lon_r)
    qz = RAD * np.sin(lat_r)
    return qx, qy, qz

def get_nearest_Fcstcodes(lat:float, lon:float)->str:
    qx, qy, qz = get_3Dcoordinate(lat,lon)
    _, idx = tree.query([qx, qy, qz], k=1)
    return codes[idx]