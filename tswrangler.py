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

src_dir = str(Path(__file__).parents[0])
dlrdb_dir = str(Path(__file__).parents[1])
data_dir = os.path.join(dlrdb_dir, 'raw_profiles')

def reduceRawProfiles(filepath = data_dir):
    """
    This function uses a rolling window to reduce all raw load profiles to hourly mean values. Monthly load profiles are then concatenated into annual profiles and returned as a dictionary object.
    The data is structured as follows:
        dict[unit:{year:[list_of_profile_ts]}]
    
    """
    p = Path(data_dir)
    profiles = {}
    for unit in ['A', 'V', 'kVA', 'Hz', 'kW']:
        profiles[unit] = {}
        for child in p.iterdir():
            ts = []
            for grandchild in child.iterdir():
                try:
                    childpath = glob(os.path.join(grandchild, '*_' + unit + '.feather'))[0]
                except:
                    pass
                data = feather.read_dataframe(childpath)
                hourlydata = data.groupby('ProfileID').apply(lambda x: x.resample('H', on='Datefield').sum())
                ts.append(hourlydata)
                print(grandchild, unit)
            profiles[unit][child] = ts
    return profiles

def saveHourlyProfiles(filepath = data_dir):
    """
    Creates folder structure and writes profile to feather file.
    
    """
    profiledict = reduceRawProfiles(filepath)
    
    for u, v in profiledict.items():
        unit = u
        dir_path = os.path.join(dlrdb_dir, 'data', 'hourly_profiles', unit)
        os.makedirs(dir_path, exist_ok=True)
        for y, z in v.items():
            year = y
            ts = pd.DataFrame(z)
            path = os.path.join(dir_path, year + '.csv')
            print(path)
            ts.to_csv(path)
            print('Write success')                
    return
        


