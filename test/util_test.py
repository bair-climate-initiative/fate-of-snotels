from fos import util


def test_get_wrf_data():
    res = util.get_wrf_data()
    assert res is not None, "WRF data not loaded"


def test_create_wrf_df():
    res = util.get_coords()
    res = util.create_wrf_df(res["snotel_gdf"])
    assert res is not None, "WRF dataframe not created"
