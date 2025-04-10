import numpy as np



def wgs84_to_ecef(lat, lon, alt):
    a = 6378137.0  # semi-major axis (meters)
    e2 = 6.69437999014e-3  # eccentricity squared

    lat = np.radians(lat)
    lon = np.radians(lon)

    N = a / np.sqrt(1 - e2 * np.sin(lat)**2)

    x = (N + alt) * np.cos(lat) * np.cos(lon)
    y = (N + alt) * np.cos(lat) * np.sin(lon)
    z = ((1 - e2) * N + alt) * np.sin(lat)
    return np.array([x, y, z])


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