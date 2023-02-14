#!/usr/bin/env python

import subprocess

from math import pi, sin, cos, acos, tan
from datetime import datetime, timedelta, timezone


def get_daytime(
    dt: datetime, lattitude: float, longitude: float
) -> (datetime, datetime):
    """
    Calculates sunrise and sunset time for given coordinates

    Based on https://gml.noaa.gov/grad/solcalc/solareqns.PDF

    Returns datetimes in local timezone
    """
    degree = pi / 180  # 1 degree in radians

    start_of_year = dt.replace(
        month=1, day=1, hour=0, minute=0, second=0, microsecond=0
    )
    start_of_next_year = start_of_year.replace(year=start_of_year.year + 1)

    gamma = (
        2
        * pi
        * (dt - start_of_year).total_seconds()
        / (start_of_next_year - start_of_year).total_seconds()
    )
    eqtime = 229.18 * (
        0.000075
        + 0.001868 * cos(gamma)
        - 0.032077 * sin(gamma)
        - 0.014615 * cos(2 * gamma)
        - 0.040849 * sin(2 * gamma)
    )
    decl = (
        0.006918
        - 0.399912 * cos(gamma)
        + 0.070257 * sin(gamma)
        - 0.006758 * cos(2 * gamma)
        + 0.000907 * sin(2 * gamma)
        - 0.002697 * cos(3 * gamma)
        + 0.00148 * sin(3 * gamma)
    )

    zenith = 90.833 * degree
    halfday = 4 * timedelta(
        minutes=acos(
            cos(zenith) / cos(lattitude * degree) / cos(decl)
            - tan(lattitude * degree) * tan(decl)
        )
        / degree
    )

    noon = dt.astimezone(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    ) + timedelta(minutes=720 - 4 * longitude - eqtime)
    sunrise = noon - halfday
    sunset = noon + halfday

    return sunrise.astimezone(), sunset.astimezone()


def dconf_write(key: str, value: str) -> None:
    cmd = ["dconf", "write", key, value]
    subprocess.call(cmd)


def dconf_read(key: str) -> str:
    cmd = ["dconf", "read", key]
    return subprocess.run(cmd, capture_output=True).stdout.decode().strip()


def hours_from_midnight(dt: datetime) -> float:
    return dt.hour + dt.minute / 60 + dt.second / 3600


if __name__ == "__main__":
    path = "/org/gnome/shell/extensions/nightthemeswitcher/time/"
    location = dconf_read(path + "location").strip("()").split(",")

    lattitude, longitude = map(float, location)
    sunrise, sunset = get_daytime(datetime.now(), lattitude, longitude)

    dconf_write(path + "sunrise", str(hours_from_midnight(sunrise)))
    dconf_write(path + "sunset", str(hours_from_midnight(sunset)))
