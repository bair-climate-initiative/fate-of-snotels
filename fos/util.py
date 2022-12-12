"""!
Common utility functions and shared constants/instantiations.
This module contains common utility functions used throughout the package.
"""

import datetime
import os

import dask
import numpy as np
import pandas as pd
import xarray as xr
from rich.console import Console

##! Shared logging console object # noqa: E265
console = Console()

# CONSTANTS
MM_TO_IN = 0.03937008


def _read_wharf_input_data(dir_meta, domain):
    """Read netcdf4 wrf data, and return lat, lon, height, and the filename"""
    infile = os.path.jsoin(dir_meta, f"wrfinput_{domain}")
    data = xr.open_dataset(infile, engine="netcdf4")
    lat = data.variables["XLAT"]
    lon = data.variables["XLONG"]
    z = data.variables["HGT"]
    return (lat, lon, z, infile)


def _wrfread_gcm(model, gcm, variant, dir, var, domain):

    all_files = sorted(os.listdir(dir))
    read_files = []
    for ii in all_files:
        if (
            ii.startswith(var + ".")
            and model in ii
            and gcm in ii
            and variant in ii
            and domain in ii
        ):
            if domain in ii:
                read_files.append(dir + str(ii))

    del all_files
    # nf = len(read_files)

    data = xr.open_mfdataset(read_files, combine="by_coords")
    var_read = data.variables[var]
    # day = data.variables["day"].values
    # nt = len(day)

    # day1 = pd.to_datetime(str(int(day[0])), format='%Y-%m-%d')
    # day2 = pd.to_datetime(str(int(day[nt-1])), format='%Y-%m-%d')
    # dates = pd.date_range(day1,day2,freq="D")

    dates = []
    for val in data["day"].data:
        try:
            dates.append(datetime.datetime.strptime(str(val)[0:-2], "%Y%m%d").date())
        except ValueError:
            dates.append(datetime.datetime(int(str(val)[0:4]), int(str(val)[4:6]), 28))

    # Mask array setting leap years = True
    # is_leap_day = (dates.month == 2) & (dates.day == 29)
    # dates = dates[~is_leap_day]

    var_read = xr.DataArray(var_read, dims=["day", "lat2d", "lon2d"])
    var_read["day"] = dates  # year doesn't matter here

    return var_read


def screen_times_wrf(data, date_start, date_end):
    # Dimensions should be "day"
    dask.config.set(**{"array.slicing.split_large_chunks": True})
    data = data.sel(
        day=~((data.day.dt.month < date_start[1]) & (data.day.dt.year <= date_start[0]))
    )
    data = data.sel(day=~(data.day.dt.year < date_start[0]))
    data = data.sel(
        day=~((data.day.dt.month >= date_end[1]) & (data.day.dt.year >= date_end[0]))
    )
    data = data.sel(day=~(data.day.dt.year > date_end[0]))
    return data


def get_peak_date_amt(data):
    startyear = np.nanmin(data.index.year)
    endyear = np.nanmax(data.index.year)
    maxvals = []
    maxargs = []
    maxdates = []
    wys = []
    for wy in range(startyear + 1, endyear):
        startdate = datetime.date(year=wy - 1, month=10, day=1)
        enddate = datetime.date(year=wy, month=10, day=1)
        timemask = (data.index.date >= startdate) & (data.index.date < enddate)
        wydata = data["SWE"][timemask]
        maxval = np.nanmax(wydata)
        maxarg = np.nanargmax(wydata)
        maxdate = wydata.index[maxarg].date()
        # if maxarg < 100 :
        #    maxarg = np.nan
        #    maxdate = np.nan
        maxvals.append(maxval)
        maxargs.append(maxarg)
        maxdates.append(maxdate)
        wys.append(wy)
    metrics = pd.DataFrame(
        data={"maxval": maxvals, "maxdate": maxdates, "maxarg": maxargs}, index=wys
    )
    return metrics


# maybe a bug in this, or in the maxarg stuff above??
def shift_to_dowy(doy):
    base = datetime.datetime(year=2002, month=1, day=1)
    targ = base + datetime.timedelta(days=doy)
    wy = 2002
    if targ.month < 10:
        wy = 2001
    wystart = datetime.datetime(year=wy, month=10, day=1)
    dowy = (targ - wystart).days
    return dowy
