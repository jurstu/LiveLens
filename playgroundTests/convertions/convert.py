import numpy as np



def wgs84_to_ecef(lat: float, lon: float, alt: float):
    a = 6378137.0  # semi-major axis (meters)
    e2 = 6.69437999014e-3  # eccentricity squared

    lat = np.radians(lat)
    lon = np.radians(lon)

    N = a / np.sqrt(1 - e2 * np.sin(lat)**2)

    x = (N + alt) * np.cos(lat) * np.cos(lon)
    y = (N + alt) * np.cos(lat) * np.sin(lon)
    z = ((1 - e2) * N + alt) * np.sin(lat)
    return np.array([x, y, z])


def calc_ecef_dist(pos1, pos2):
    return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2 + (pos1[2] - pos2[2])**2)




def ecef_to_enu(ecef, ref_lat, ref_lon, ref_alt):
    ref_ecef = wgs84_to_ecef(ref_lat, ref_lon, ref_alt)

    lat = np.radians(ref_lat)
    lon = np.radians(ref_lon)

    dx = ecef - ref_ecef

    R = np.array([
        [-np.sin(lon),             np.cos(lon),              0],
        [-np.sin(lat)*np.cos(lon), -np.sin(lat)*np.sin(lon), np.cos(lat)],
        [np.cos(lat)*np.cos(lon),  np.cos(lat)*np.sin(lon),  np.sin(lat)]
    ])
    enu = R @ dx
    return enu



if __name__ == "__main__":
    lat1, lon1 = 52.201361, 21.038073
    lat2, lon2 = 52.201860, 21.038023

    ecef2 = wgs84_to_ecef(lat2, lon2, 0)
    enu1to2 = ecef_to_enu(ecef2, lat1, lon1, 0)

    print(enu1to2)


    exit()

    pos1 = wgs84_to_ecef(lat1, lon1, 0)
    pos2 = wgs84_to_ecef(lat2, lon2, 0)
    

    print(pos1)
    print(pos2)

    dist = calc_ecef_dist(pos1, pos2)
    print(dist)


