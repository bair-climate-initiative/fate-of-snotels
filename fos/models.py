import numpy as np 
from utils import partition_dataframe, make_time_lists
from xarray.core.dataarray import DataArray
from xarray.core.dataset import Dataset
from utils import create_xarray_data_vars

def snotel_value(forcing_split: dict, obs_split: dict, dates_lists: dict, model_params: dict = {'vars': ['SWE'], 'fvars': ['SNOTEL_SWE']}):
    """ 
    this model simicts the ouput value as the same as the SNOTEL for for all points with no change
    """
    model_name = 'snotel_value'
    vars = model_params['vars']
    fvars = model_params['fvars']
    nvars = len(fvars)
    # train the model
    # (no training needed)
    model = lambda f: f['SNOTEL_SWE'].values
    # apply the model
    y = []
    y_hat = []
    dates = []
    for j,window in enumerate(dates_lists.keys()):
        for i, var in enumerate(vars):
            y.append(obs_split[window][var].values)
            dates.append(forcing_split[window]['SNOTEL_SWE'].index)
            forcing = forcing_split[window]
            y_hat.append(model(forcing))
    y = np.concatenate(y, axis = 0).reshape(-1,nvars)
    y_hat = np.concatenate(y_hat, axis = 0).reshape(-1, nvars)
    
    model_out = create_xarray_data_vars(vars, y = y, y_hat = y_hat, dates_lists= dates_lists)

    return model_out, model_name

def snotel_with_offset(forcing_split: dict, obs_split: dict, dates_lists: dict, model_params: dict = {'vars': ['SWE'], 'fvars': ['SNOTEL_SWE']}):
    """ 
    this model simicts the ouput value as the same as the SNOTEL plus an offset learned in the training period
    """
    model_name = 'snotel_with_offset'
    vars = model_params['vars']
    fvars = model_params['fvars']
    nvars = len(fvars)
    # train the model
    offset = float(obs_split['train'].mean()- forcing_split['train']['SNOTEL_SWE'].mean())

    model = lambda f: (f['SNOTEL_SWE'] + offset)

    # apply the model
    y = []
    y_hat = []
    dates = []
    for j,window in enumerate(dates_lists.keys()):
        for i, var in enumerate(vars):
            y.append(obs_split[window][var].values)
            dates.append(forcing_split[window]['SNOTEL_SWE'].index)
            forcing = forcing_split[window]
            sim = model(forcing)
            y_hat.append(sim)
    y = np.concatenate(y, axis = 0).reshape(-1,nvars)
    y_hat = np.concatenate(y_hat, axis = 0).reshape(-1, nvars)
        
    model_out = create_xarray_data_vars(vars, y = y, y_hat = y_hat, dates_lists= dates_lists)
        
    return model_out, model_name

def training_mean(forcing_split: dict, obs_split: dict, dates_lists: dict, model_params: dict = {'vars': ['SWE'], 'fvars': ['SNOTEL_SWE']}):
    """ 
    this model simicts the ouput value as the same as the SNOTEL plus an offset learned in the training period
    """
    model_name = 'snotel_with_offset'
    vars = model_params['vars']
    # train the model
    fvars = model_params['fvars']

    nvars = len(fvars)
    train_mean = float(forcing_split['train']['SNOTEL_SWE'].mean())

    model = lambda f: f['SNOTEL_SWE'] - f['SNOTEL_SWE'] + train_mean

    # apply the model
    y = []
    y_hat = []
    dates = []
    for j,window in enumerate(dates_lists.keys()):
        for i, var in enumerate(vars):
            y.append(obs_split[window][var].values)
            dates.append(forcing_split[window]['SNOTEL_SWE'].index)
            forcing = forcing_split[window]
            sim = model(forcing)
            y_hat.append(sim)
    y = np.concatenate(y, axis = 0).reshape(-1,nvars)
    y_hat = np.concatenate(y_hat, axis = 0).reshape(-1, nvars)
        
    model_out = create_xarray_data_vars(vars, y = y, y_hat = y_hat, dates_lists= dates_lists)
        
    return model_out, model_name



from sklearn.linear_model import LinearRegression
import pandas as pd
def lin_reg(forcing_split: dict, obs_split: dict, dates_lists: dict, model_params: dict = {'vars': ['SWE'], 'fvars': ['SNOTEL_SWE']}):
    """ 
    this model simicts the ouput value as the same as the SNOTEL plus an offset learned in the training period
    """
    model_name = 'snotel_with_offset'
    vars = model_params['vars']
    fvars = model_params['fvars']
    nvars = len(fvars)

    # train the model
    # regression model on SNOTEL_SWE

    df = pd.merge(forcing_split['train'], obs_split['train'], left_index=True, right_index=True)
    res = LinearRegression().fit(df[fvars].values.reshape(-1,nvars), df[['SWE']].values)

    # apply the model
    y = []
    y_hat = []
    dates = []
    for j,window in enumerate(dates_lists.keys()):
        for i, var in enumerate(vars):
            y.append(obs_split[window][var].values)
            dates.append(forcing_split[window]['SNOTEL_SWE'].index)
            forcing = forcing_split[window][fvars].values.reshape(-1,nvars)
            sim = res.predict(forcing).flatten()
            y_hat.append(sim)
    y = np.concatenate(y, axis = 0).reshape(-1,nvars)
    y_hat = np.concatenate(y_hat, axis = 0).reshape(-1, nvars)
        
    model_out = create_xarray_data_vars(vars, y = y, y_hat = y_hat, dates_lists= dates_lists)
        
    return model_out, model_name

from sklearn.linear_model import LinearRegression
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
import numpy as np

def poly_reg(forcing_split: dict, obs_split: dict, dates_lists: dict, model_params: dict = {'vars': ['SWE'], 
                                                                                            'fvars': ['SNOTEL_SWE'],
                                                                                            'degree': 3}):
    degree = model_params['degree']
    model_name = f'polynomial {degree} regression'
    vars = model_params['vars']
    fvars = model_params['fvars']
    nvars = len(fvars)

    ## define the model
    model = Pipeline([('poly', PolynomialFeatures(degree=degree)),
                    ('linear', LinearRegression(fit_intercept=False))])

    # train the model

    # fit to an order-3 polynomial data
    x = forcing_split['train'].values
    y = obs_split['train'][vars]
    res = model.fit(x, y)

    # apply the model
    y = []
    y_hat = []
    dates = []
    for j,window in enumerate(dates_lists.keys()):
        for i, var in enumerate(vars):
            y.append(obs_split[window][var].values)
            dates.append(forcing_split[window]['SNOTEL_SWE'].index)
            forcing = forcing_split[window][fvars].values.reshape(-1,nvars)
            sim = res.predict(forcing).flatten()
            y_hat.append(sim)
    y = np.concatenate(y, axis = 0).reshape(-1,nvars)
    y_hat = np.concatenate(y_hat, axis = 0).reshape(-1, nvars)
        
    model_out = create_xarray_data_vars(vars, y = y, y_hat = y_hat, dates_lists= dates_lists)
    return model_out, model_name
        
