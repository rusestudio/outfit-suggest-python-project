from typing import Tuple
from math import pi, tan, log, cos, pow, sin
import numpy as np
from numba import njit

import json

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
slat1 = SLAT1 * DEGRAD
slat2 = SLAT2 * DEGRAD
olon = OLON * DEGRAD
olat = OLAT * DEGRAD
sn = tan(pi * 0.25 + slat2 * 0.5) / tan(pi * 0.25 + slat1 * 0.5)
sn = log(cos(slat1) / cos(slat2)) / log(sn)
sf = tan(pi * 0.25 + slat1 * 0.5)
sf = pow(sf, sn) * cos(slat1) / sn
ro = tan(pi * 0.25 + olat * 0.5)
ro = re * sf / pow(ro, sn)

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

# 
def combert_latlon_to_grid( lat, lon ) -> Tuple[int,int]:
    '''
    Change latitude and longitude to Korean weather grid coordinates.

    Param:
        lat : float
            corrent latation
        lon : float
            corrent lon
    return:
        grid : Tuple[int, int]
            Index[0] : grid xpos
            Index[1] : grid ypos
    '''
    return latlon_to_grid(lat,lon,re,sf,sn,ro,XO,YO,olon) 

def get_efficient_vilFcst_params(hour, day):
    full_index = (24 - (hour+1)%24) * 12 + 290 * day

    if hour > 6:
        full_index += 2
    elif hour > 15:
        full_index += 1
    
    if full_index <= 290:
        return 1, full_index
    
    

if __name__ == "__main__":
    print(combert_latlon_to_grid(37.564214, 127.001699))
    # 결과 저장용 리스트

    for hour in range(24):
        for day in range(4):
            result = get_efficient_vilFcst_params(hour, day)
            print(f"Hour: {hour}, Day: {day}, Result: {result}")