from typing import Tuple
import math

# Variable for converting from lat,lon to grid
RAD = 6371.00877 # Earth's radius
GRID = 5.0       # Grid spacing
SLAT1 = 30.0     # Projection lat 1 (degrees)
SLAT2 = 60.0     # Projection lat 2 (degrees)
OLON = 126.0     # Reference lon (degrees)
OLAT = 38.0      # Reference lat (degrees)
XO = 43          # Reference X cordinate
YO = 136         # Reference Y cordinate

# This function should get location infomation
# TODO
def get_location() -> Tuple[float,float]:
    return [37.5665,126.9780]

def latlon_to_grid( pos : Tuple[float,float] ):
    DEGRAD = math.pi / 180.0

    re = RAD / GRID
    slat1 = SLAT1 * DEGRAD
    slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD
    olat = OLAT * DEGRAD

    sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
    sf = math.pow(sf, sn) * math.cos(slat1) / sn
    ro = math.tan(math.pi * 0.25 + olat * 0.5)
    ro = re * sf / math.pow(ro, sn)

    ra = math.tan(math.pi * 0.25 + (pos[0]) * DEGRAD * 0.5)
    ra = re * sf / math.pow(ra, sn)
    theta = pos[1] * DEGRAD - olon
    if theta > math.pi:
        theta -= 2.0 * math.pi
    if theta < -math.pi:
        theta += 2.0 * math.pi
    theta *= sn

    x = int(ra * math.sin(theta) + XO + 0.5)
    y = int(ro - ra * math.cos(theta) + YO + 0.5)

    return [x, y]

if __name__ == "__main__":
    print(latlon_to_grid([37.5665,126.9780]))