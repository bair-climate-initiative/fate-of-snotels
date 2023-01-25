"""!
Common utility functions and shared constants/instantiations.
This module contains common utility functions used throughout the package.
"""

import datetime
import glob
import os

import dask
import geopandas as gpd
import netCDF4 as nc
import numpy as np
import pandas as pd
import xarray as xr
from rich.console import Console

##! Shared logging console object # noqa: E265
console = Console()

# CONSTANTS
MM_TO_IN = 0.03937008

# Keep global variables available to all modules
## define directories
# TODO remove these and use dirs.py instead
basedir = '/glade/u/home/mcowherd/'
projectdir = basedir + 'fos-data/'
snoteldir = projectdir + 'snoteldata/'
wrfdir = '/glade/campaign/uwyo/wyom0112/postprocess/'
coorddir = wrfdir + 'WRF-data/wrf_coordinates/' 
domain = "d02"

def setup(
    new_basedir: str = '/glade/u/home/mcowherd/',
    new_domain: str = "d02",
    new_projectdir: str = basedir + 'fos-data/',
):
    """! Set up the package environment.
    Call setup(new_basedir, new_domain, new_projectdir) to set up the environment,
    e.g. if you are on perlmutter call
    ```
    setup("/global/project/projectdirs/")
    ```
    """
    global basedir, domain, projectdir
    basedir = new_basedir
    domain = new_domain
    if new_projectdir is None:
        new_projectdir = os.path.join(basedir, "fate-of-snotel")
    projectdir = new_projectdir



def _wrfread_gcm(model, gcm, variant, dir, var, domain):
    dir = os.path.join(dir, domain)
    all_files = sorted(os.listdir(dir))
    read_files = []

    for ii in all_files:
        if (
            ii.startswith(var + ".")
            and model in ii
            # and gcm in ii
            and variant in ii
            and domain in ii
        ):
            if domain in ii:
                read_files.append(os.path.join(dir, str(ii)))
    assert len(read_files) > 0, f"No matching files found in {dir}"

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

    datedata = pd.to_datetime(data.day)
    data = data.sel(day=~((datedata.month < date_start[1]) & (datedata.year <= date_start[0])))

    datedata = pd.to_datetime(data.day)
    data = data.sel(day=~(datedata.year < date_start[0]))

    datedata = pd.to_datetime(data.day)
    data = data.sel(day=~((datedata.month >= date_end[1]) & (datedata.year >= date_end[0])))

    datedata = pd.to_datetime(data.day)
    data = data.sel(day=~(datedata.year > date_end[0]))

    return data


def get_peak_date_amt(data):
    """Get peak date and amount for each water year (Oct 1 to Oct 1)."""
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
        wydata = data.SWE[timemask]
        if len(wydata) == 0:
            continue
        maxval = np.nanmax(wydata)
        maxarg = np.nanargmax(wydata)
        maxdate = wydata.index[maxarg].date()
        maxvals.append(maxval)
        maxargs.append(maxarg)
        maxdates.append(maxdate)
        wys.append(wy)
    metrics = pd.DataFrame(
        data={"maxval": maxvals, "maxdate": maxdates, "maxarg": maxargs}, index=wys
    )
    return metrics

def _read_wrf_meta_data(dir_meta: str, domain: str):
    """Read wrf meta data from nc4 files, and return lat, lon, height, and the filename"""
    infile = os.path.join(dir_meta, f"wrfinput_{domain}")
    data = xr.open_dataset(infile, engine="netcdf4")
    lat = data.variables["XLAT"]
    lon = data.variables["XLONG"]
    z = data.variables["HGT"]
    return (lat, lon, z, infile)


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


def get_coords(coorddir):
    """Get the coordinates of the WRF grid and snotels."""
    #coorddir = os.path.join(projectdir, "WRF-data", "wrf_coordinates")
    dir_meta = coorddir

    # Load the location of all wrf pixels
    lat1, lon1, z1, _ = _read_wrf_meta_data(dir_meta, domain)
    lon_wrf = lon1[0, :, :]
    lat_wrf = lat1[0, :, :]
    z_wrf = z1[0, :, :]
    lat_wrf = xr.DataArray(lat_wrf, dims=["lat2d", "lon2d"])
    lon_wrf = xr.DataArray(lon_wrf, dims=["lat2d", "lon2d"])
    z_wrf = xr.DataArray(z_wrf, dims=["lat2d", "lon2d"])

    # Load the location info for all snotels
    coords = nc.Dataset(os.path.join(coorddir, "wrfinput_d02_coord.nc"))
    snoteldir = os.path.join(projectdir, "snoteldata")
    snotelmeta = pd.read_csv(os.path.join(snoteldir, "snotelmeta.csv"))
    huc6 = gpd.read_file(os.path.join(projectdir, "spatialdata", "huc6.shp"))
    huc8 = gpd.read_file(os.path.join(projectdir, "spatialdata", "huc8.shp"))
    snotel_gdf = gpd.GeoDataFrame(
        data={
            "site_name": snotelmeta.site_name,
            "elev": snotelmeta.elev,
            "site_number": snotelmeta.site_number,
            "state": snotelmeta.state,
            "namestr": snotelmeta.namestr,
            "startdt": snotelmeta.startdt,
        },
        geometry=gpd.points_from_xy(snotelmeta.lon, snotelmeta.lat),
        crs="epsg:4326",
    )

    return snotel_gdf, coords, huc6, huc8


def get_wrf_avail(wrfdir):
    """!
    Read in the wrf data - WIP.

    basedir [str]: base directory for wrf data, defauls to perlmutter system,
        use '/global/project/projectdirs/' for cori system
    domain [str]: domain to read in, defaults to 'd02'
    """
    # log the bc models available
    bc_glob = glob.glob(os.path.join(wrfdir, "*_bc"))
    bcmodels = [val.split("/")[-1] for val in bc_glob]
    assert len(bcmodels) > 0, f"No BC models found in {wrfdir}"
    console.log("Available BC Models:", bcmodels)
    console.log("run get_wrf_data(wrfdir,model) with the name of the model you want to load")
    return

def get_wrf_data(wrfdir, model, variant):
    """
    TODO - fix model variable assignment using a dictionary
    """
    # change the model
    var = "snow"
    mod_historical = model +'_'+ variant + '_historical_bc'
    mod_future = model +'_' + variant+ '_ssp370_bc'
    gcm = mod_historical
    date_start_pd, date_end_pd = [1980, 1, 1], [2013, 12, 31]  # 30 years, historical
    model = "hist"
    modeldir = os.path.join(wrfdir, gcm , 'postprocess')
    print(modeldir)
    var_wrf = _wrfread_gcm(model, gcm, variant, modeldir, var, domain)
    var_wrf = screen_times_wrf(var_wrf, date_start_pd, date_end_pd)

    # future dates
    date_start_pd, date_end_pd = [2014, 1, 1], [2100, 12, 31]
    gcm = mod_future
    modeldir = os.path.join(wrfdir, gcm ,'postprocess')
    model = "ssp370"
    var_wrf_ssp370 = _wrfread_gcm(model, gcm, variant, modeldir, var, domain)
    var_wrf_ssp370 = screen_times_wrf(var_wrf_ssp370, date_start_pd, date_end_pd)

    return dict(var_wrf=var_wrf, var_wrf_ssp370=var_wrf_ssp370)


def create_wrf_df(snotel_gdf: gpd.GeoDataFrame):
    """! Create a dataframe of WRF data for each snotel site."""
    snotel_no_ak = snotel_gdf[snotel_gdf.state != "AK"]

    day1 = datetime.datetime(year=1980, day=1, month=9)
    days = []
    for i in range(42960):  # hardcoded number of days TODO fix this hardcoding
        days.append(day1 + datetime.timedelta(days=i))

    # hold the data for a dataframe
    snoteldir = os.path.join(projectdir, "snoteldata")
    entries = []
    datadir = os.path.join(projectdir, "wrfts", "ukesm1-0-ll_bc")
    for i, entry in snotel_no_ak.iterrows():
        try:
            num = entry.site_number
            name = entry.site_name.replace(" ", "").replace("(", "").replace(")", "")
            pt = [entry.geometry.x, entry.geometry.y]
            wrfpoint = np.load(os.path.join(datadir, f"wrfpoint_{name}.npy"))
            wrfbasin = np.load(os.path.join(datadir, f"wrfbasin_{name}.npy"))
            wrfpoint = pd.DataFrame(
                wrfpoint * MM_TO_IN, columns=["SWE"], index=pd.to_datetime(days)
            )
            wrfbasin = pd.DataFrame(
                wrfbasin * MM_TO_IN, columns=["SWE"], index=pd.to_datetime(days)
            )
            snotelpoint = pd.read_csv(
                os.path.join(snoteldir, f"snotel{num}.csv"),
                index_col=0,
                parse_dates=True,
            )
            wpt = get_peak_date_amt(wrfpoint)
            wbas = get_peak_date_amt(wrfbasin)
            sm = get_peak_date_amt(snotelpoint)
            entries.append(dict(name=name, wpt=wpt, wbas=wbas, sm=sm, pt=pt))
        except FileNotFoundError:
            continue
    res = gpd.GeoDataFrame(entries)
    return res
