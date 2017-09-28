# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 09:11:13 2017

@author: CKAN
"""
import numpy as np
import pandas as pd
import feather
from glob import glob
import os
from pathlib import Path

src_dir = str(Path(__file__).parents[1])
dlrdb_dir = str(Path(__file__).parents[2])
data_dir = os.path.join(dlrdb_dir, 'profiles')

def reduceRawProfiles(filepath = os.path.join(data_dir, 'raw')):
    """
    This function uses a rolling window to reduce all raw load profiles to hourly mean values. Monthly load profiles are then concatenated into annual profiles and returned as a dictionary object.
    The data is structured as follows:
        dict[unit:{year:[list_of_profile_ts]}]
    
    """
    p = Path(filepath)
    for unit in ['A', 'V', 'kVA', 'Hz', 'kW']:
        for child in p.iterdir():
        #create empty directory to save files
            dir_path = os.path.join(data_dir, 'hourly', unit)
            os.makedirs(dir_path, exist_ok=True)
            year = os.path.split(child)[-1]             
        #initialise empty dataframe to concatenate annual timeseries
            ts = pd.DataFrame()
        #iterate through all data files to combine 5min monthly into hourly reduced annual timeseries
            for grandchild in child.iterdir():
                try:
                    childpath = glob(os.path.join(grandchild, '*_' + unit + '.feather'))[0]
                    data = feather.read_dataframe(childpath)
                    data.Datefield = np.round(data.Datefield.astype(np.int64), -9).astype('datetime64[ns]')
                    data['Valid'] = data['Valid'].map(lambda x: x.strip()).map({'Y':True, 'N':False})
                    if unit in ['kVA','kW']:
                        hourlydata = data.groupby(['RecorderID', 'ProfileID']).apply(lambda x: x.resample('H', on='Datefield').sum())
                    elif unit in ['A','V','Hz']:
                        hourlydata = data.groupby(['RecorderID', 'ProfileID']).apply(lambda x: x.resample('H', on='Datefield').mean())
                    else:
                        print("Unit must be one of 'A', 'V', 'kVA', 'Hz', 'kW'")
                    hourlydata.reset_index(inplace=True)
                    hourlydata = hourlydata.loc[:, hourlydata.columns != 'Active']
                    ts = ts.append(hourlydata)
                    print(grandchild, unit)
                except:
                    pass #skip if feather file does not exist 
        #write to reduced data to file
            if ts.empty:
                pass
            else:
                wpath = os.path.join(dir_path, year + '_' + unit + '.feather')
                feather.write_dataframe(ts, wpath)
                print('Write success')
    return
        


