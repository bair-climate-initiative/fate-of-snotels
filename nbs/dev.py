"""
Temporary "notebook" for development
"""

import pandas as pd
from pathlib import Path
from fos.util import setup_plot_style
import matplotlib.pyplot as plt
import seaborn as sns
from fos.util import memory
import os
import numpy as np


## GLOBAL SETUP
dpath = "/glade/u/home/cjreed/data/ukesm"
plotpath = "/glade/u/home/cjreed/fate-of-snotels/plots/dev"
os.makedirs(plotpath, exist_ok=True)
setup_plot_style()


## HELPERS
def read_csvs(dpath: str) -> pd.DataFrame:
  dfs = list()
  for filename in dpath:
      data = pd.read_csv(filename, index_col=None, header=0)
      data['pt'] = filename.stem.split('_')[-1]
      dfs.append(data)
  df = pd.concat(dfs, axis=0, ignore_index=True)
  df = df.rename(columns={'Unnamed: 0': 'wyear'})
  return df


@memory.cache
def get_data(dpath: str) -> pd.DataFrame:  
  basins = read_csvs(Path(dpath).glob("wrfb*.csv"))
  pts = read_csvs(Path(dpath).glob("wrfp*.csv"))
  combined_df = pd.merge(pts, basins, how='left', left_on=['pt', 'wyear'], right_on=['pt', 'wyear'], suffixes=('_pt', '_basin'))
  return combined_df


def savefig(name: str):
  plt.savefig(os.path.join(plotpath, name))


def plt_err_hist(dffield, xlabel, ylabel, title, fname):
  plt.clf()
  sns.histplot(dffield)
  plt.xlabel(xlabel)
  plt.ylabel(ylabel)
  plt.title(title)
  savefig(fname)

def plt_year_err(data, title, xlab, ylab, fname):
  plt.clf()
  mean_data = data.mean()
  std_data = data.std()
  mean_data.plot()
  plt.fill_between(mean_data.index, mean_data - std_data, mean_data +  std_data, color="b", alpha=0.2);
  plt.ylabel(ylab)
  plt.xlabel(xlab)
  plt.title(title)
  savefig(fname)
  
def plot_relation(df, x, y, title, fname, c='wyear', colormap='viridis'):
  plt.clf()
  df.plot.scatter(x=x, y=y, c=c, colormap=colormap, title=title)
  plt.gca().axline((0, 0), slope=1)
  savefig(fname)
  

def main():
  df = get_data(dpath)

  # What is the difference between the pt and basic values at peak SWE?
  df['pt_basin_diff'] = (df['maxval_pt'] - df['maxval_basin'])
  df['abs_pt_basin_diff'] = df['pt_basin_diff'].abs()
  total_mae = df['pt_basin_diff'].abs().mean()
  total_mae_std = df['pt_basin_diff'].abs().std()

  ## Plotting error histogram ##  
  plt_err_hist(df['pt_basin_diff'], 'MAE(Pt - Basin) at peak SWE', 'Count', f'Average MAE: {total_mae:.1f} +/- {total_mae_std:.1f}', '1-err_hist.png')
  
  # scatterplot of pt vs basin
  plot_relation(df, 'maxval_pt', 'maxval_basin', 'Pt vs Basin SWE at Peak Week', '1-maxval_pt_vs_maxval_basin.png')
  
  # error by year
  plt_year_err(df.groupby('wyear')['abs_pt_basin_diff'], f'MAE: {total_mae:.1f} +/- {total_mae_std:.1f}', 'Water Year', f'MAE(Pt - Basin) at Peak Week', f'1-err_by_year.png')

  ## Plotting error by year

  ############################################################################################################  
  ## Simple mean correcting
  ############################################################################################################
  # Use the ratio per location from 1980-Present to determine the location-based correction factor
  max_year = 2020
  
  # find the mean difference between pt and basin for each location in the past years until max_year
  corr_factor = df[df.wyear <= max_year].groupby('pt').mean()['pt_basin_diff']

  # apply the correction factor to the pt values
  df = pd.merge(df, corr_factor, how='left', left_on='pt', right_on='pt', suffixes=('', '_corr_factor'))

  ## TODO make this into a function, since it's a common operation
  # calculate the new error by subtracting the corrected pt from the previous difference
  df['maxval_pt_hist_corr'] = df['maxval_pt'] - df['pt_basin_diff_corr_factor']
  # do not allow maxval_pt_hist_corr to be negative:
  df.loc[df['maxval_pt_hist_corr'] < 0, 'maxval_pt_hist_corr'] = 0
  
  df['pt_basin_diff_corr'] = df['maxval_pt_hist_corr'] - df['maxval_basin']
  df['abs_pt_basin_diff_corr'] = df['pt_basin_diff_corr'].abs()
  df_past_max = df[df.wyear > max_year]

  total_mae = df_past_max["abs_pt_basin_diff_corr"].mean()
  total_mae_std = df_past_max["abs_pt_basin_diff_corr"].std()
  
  plt_err_hist(df_past_max['pt_basin_diff_corr'], 'MAE(Pt - Basin) at peak SWE, Mean Corrected', 'Count', f'Average MAE: {total_mae:.1f} +/- {total_mae_std:.1f}', '2-err_hist_mean_corr.png')  
  plt_year_err(df_past_max.groupby('wyear')['abs_pt_basin_diff_corr'],f'MAE: {total_mae:.1f} +/- {total_mae_std:.1f}', 'Water Year', f'MAE(Pt - Basin) at Peak Week, Mean Corrected 1981-{max_year}', f'2-err_by_year_mean_corr-{max_year}.png')
  plot_relation(df_past_max, 'maxval_pt_hist_corr', 'maxval_basin', 'Pt vs Basin SWE at Peak Week, Historical Mean Corrected', f'2-maxval_pt_vs_maxval_basin_mean_corr-{max_year}.png')
  
  
  # what if we just predict the basin average over the 1980-{max_year} period?
  basin_avg_val = df[df.wyear <= max_year].groupby('pt').mean()['maxval_basin']
  df = pd.merge(df, basin_avg_val, how='left', left_on='pt', right_on='pt', suffixes=('', '_avg_basin'))
  df['basin_hist_avg_diff'] = df['maxval_basin_avg_basin'] - df['maxval_basin']
  df['abs_basin_hist_avg_diff'] = df['basin_hist_avg_diff'].abs()
  df_past_max = df[df.wyear > max_year]

  plt_err_hist(df_past_max['basin_hist_avg_diff'], 'MAE(Hist Basin - Basin) at peak SWE', 'Count', f'Average MAE: {total_mae:.1f} +/- {total_mae_std:.1f}', f'3-err_hist_hist-mean-{max_year}.png')
  plt_year_err(df_past_max.groupby('wyear')['abs_basin_hist_avg_diff'],f'MAE: {total_mae:.1f} +/- {total_mae_std:.1f}', 'Water Year', f'MAE(Pt - Basin) at Peak Week, Historical Pred 1981-{max_year}', f'3-err_by_year_hist_mean-{max_year}.png')
  plot_relation(df_past_max, 'maxval_basin_avg_basin', 'maxval_basin', 'Pt vs Basin SWE at Peak Week, Historical Mean Corrected', f'3-maxval_pt_vs_maxval_basin_hist_mean-{max_year}.png')
    
  
  ############################################################################################################
  ## Plotting error using a rolling mean not including the current year
  ############################################################################################################
  nroll = 5
  df['pt_basin_diff_rolling'] = df.groupby('pt')['pt_basin_diff'].transform(lambda x: x.rolling(nroll, min_periods=2, closed='right').mean())
  df['pt_basin_diff_rolling_corr'] = df['maxval_pt'] - df['pt_basin_diff_rolling']
  # do not allow maxval_pt_hist_corr to be negative:
  df.loc[df['pt_basin_diff_rolling_corr'] < 0, 'pt_basin_diff_rolling_corr'] = 0

  df['abs_pt_basin_diff_rolling_corr'] = df['pt_basin_diff_rolling_corr'].abs()

  total_mae = df["abs_pt_basin_diff_rolling_corr"].mean()
  total_mae_std = df["abs_pt_basin_diff_rolling_corr"].std()
  plt_err_hist(df['pt_basin_diff_rolling_corr'], 'MAE(Pt - Basin) at peak SWE, Rolling Mean Corrected', 'Count', f'Average MAE: {total_mae:.1f} +/- {total_mae_std:.1f}', '4-err_hist_rolling_mean_corr.png')  
  plt_year_err(df.groupby('wyear')['abs_pt_basin_diff_rolling_corr'], f'MAE: {total_mae:.1f} +/- {total_mae_std:.1f}', 'Water Year', f'MAE(Pt - Basin) at Peak Week, Rolling Mean Corr', f'4-err_by_year_mean_corr_rolling-{nroll}.png')

  ############################################################################################################
  ## Plotting error using the basin average of the last 5 years
  ############################################################################################################
  
  ## Plotting error using a simple linear regression model over time
  
  ## Plotting error using a simple linear regression model over time and spatial correction
  
  ## etc.



if __name__ == '__main__':
  main()