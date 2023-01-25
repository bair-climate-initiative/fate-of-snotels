from fos import util, dirs
import os 
import xarray as xr
import pandas as pd
import geopandas as gpd

def test_gen_analysis_dataframe_for_something():
    # snotel_gdf has the snotel data    
    snotel_gdf, coords, huc6, huc8 = util.get_coords(dirs.coorddir)

    # wrfdata has historical and ssp370
    wrfdata = util.get_wrf_data(dirs.wrfdir, model = 'mpi-esm1-2-lr', variant = 'r7i1p1f1')

    # check some dimensions to make sure everything loads correctly
    assert wrfdata['var_wrf_ssp370'].shape[1:] == wrfdata['var_wrf'].shape[1:], "SSP370 and Historical data are different sizes"
    assert len(snotel_gdf) > 0, "No snotel gdf data loaded"
    assert coords.dimensions['lat'].size == wrfdata['var_wrf'].shape[1], "Coords dimensions are different from wrfdata coords"
    
    
