#!/bin/bash

## data loader for fate of snotel project ## 

## DATA

from fos.dirs import basedir, projectdir, snoteldir
import geopandas as gpd
import pandas as pd

'''
snotelmeta
snotel_gdf
in6s, in8s
snotel_no_ak
'''

snotelmeta = pd.read_csv(snoteldir + 'snotelmeta.csv')
huc6 = gpd.read_file(projectdir + 'spatialdata/huc6.shp')
huc8 = gpd.read_file(projectdir + 'spatialdata/huc8.shp')
snotel_gdf = gpd.GeoDataFrame(data = {'site_name':snotelmeta.site_name,
                                     'elev': snotelmeta.elev,
                                     'site_number':snotelmeta.site_number,
                                     'state':snotelmeta.state,
                                     'namestr':snotelmeta.namestr,
                                     'startdt':snotelmeta.startdt}, geometry = gpd.points_from_xy(snotelmeta.lon, snotelmeta.lat), crs = 'epsg:4326')

## time series of the difference in time between peak SWE at the grid box where the SNOTEL resides 
## and the time of peak SWE across the HUC-6 watershed in which the SNOTEL resides
in6 = []
in8 = []
for i in snotel_gdf.index:
    point = snotel_gdf[snotel_gdf.index == i].geometry[i]
    basin = huc6[huc6.contains(point)]
    k = basin.name.index[0]
    in6.append(basin.name[k])
    basin = huc8[huc8.contains(point)]
    k = basin.name.index[0]
    in8.append(basin.name[k])
in6s = pd.Series(in6)
in8s = pd.Series(in8)

snotel_no_ak = snotel_gdf[snotel_gdf.state != "AK"]
