from typing import Tuple
from math import pi, tan, log, cos, pow, sin
from numba import njit

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

def latlon_to_grid(lat: float, lon: float,
                   re: float, sf: float, sn: float, ro: float,
                   XO: float, YO: float, olon: float) -> Tuple[int, int]:
    ra = tan(pi * 0.25 + lat * DEGRAD * 0.5)
    ra = re * sf / pow(ra, sn)
    theta = lon * DEGRAD - olon
    if theta > pi:
        theta -= 2.0 * pi
    if theta < -pi:
        theta += 2.0 * pi
    theta *= sn

    x = int(ra * sin(theta) + XO + 0.5)
    y = int(ro - ra * cos(theta) + YO + 0.5)

    return [x, y]

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

    

if __name__ == "__main__":
    print(combert_latlon_to_grid(37.564214, 127.001699))