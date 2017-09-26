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

def loadProfiles(filepath = data_dir):
    """
    This function loads all feather tables in filepath into workspace.
    
    """
    p = Path(data_dir)
    for child in p.iterdir():
        for grandchild in child.iterdir():
            glob(os.path.join(grandchild, '*_A.feather'))
    
    files = glob(os.path.join(data_dir, '*.feather'))
    names = [f.rpartition('.')[0] for f in os.listdir(data_dir)]
    tables = {}
    for n, f in zip(names, files):
        try:
            tables[n] = feather.read_dataframe(f)
        except:
            pass
    return tables


for child in p.iterdir():
    for grandchild in child.iterdir():
        for unit in ['A', 'V', 'kVA', 'Hz', 'kW']:
            try:
                newfiles = glob(os.path.join(grandchild, '*_', unit ,'.feather'))
            except:
                pass
            print(newfiles)