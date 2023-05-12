import matplotlib.pyplot as plt
from metrics import nse

def plot_single_sample_model_out(model_out, dates_lists, var = 'SWE', error = 'NSE'):
    obskw = {'linestyle': 'solid', 'color':'darkgrey'}
    simkw = {'linestyle': 'dashed'} 
    fig,ax = plt.subplots(1,1, figsize=(10,5))
    for i,val in enumerate(dates_lists.keys()):
        data = model_out[i]
        date =data['date']
        ax.plot(date,data[f'{val}_{var}_obs'], label=f'{val} obs', **obskw)
        ax.plot(date,data[f'{val}_{var}_sim'], label=f'{val} sim', **simkw)
    test_err = nse(obs =model_out[-1][f'test_{var}_obs'], sim = model_out[-1][f'test_{var}_sim'])
    ax.set_title(('test NSE = ', test_err))
    plt.legend()
    plt.show()
    return