# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 16:03:22 2017

@author: Wiebke Toussaint

This file contains functions to fetch and save data from the DLR SQL database. saveTables() saves socio-demographic data. Sensitive personal information is removed with the anonAns() function. saveProfiles() saves the load profiles for each year in a specified range.

NOTE: These functions require access to a DLR SQL database instance.
"""
import numpy as np
import pandas as pd
import feather
from glob import glob
import os
from pathlib import Path

from support import rawprofiles_dir, hourlyprofiles_dir
import obshelpers as o

def saveTables():
    """
    This function fetches tables from the SQL database and saves them as a feather object. Answer tables are anonymsed to remove all discriminating personal information of respondents.
    """
    
    groups = o.getGroups() 
    questions = o.getData('Questions')
    questionaires = o.getData('Questionaires')
    qdtype = o.getData('QDataType')
    qredundancy = o.getData('QRedundancy')
    qconstraints = o.getData('QConstraints')
    answers = o.getData('Answers')
    answers_num = o.getData('Answers_Number')
    links = o.getData('LinkTable')
    profiles = o.getData('Profiles')
    profilesummary = o.getData('ProfileSummaryTable')
    recorderinstall = o.getData('RECORDER_INSTALL_TABLE')
    
    tablenames = ['groups', 'questions', 'questionaires', 'qdtype', 'qredundancy', 'qconstraints', 'answers', 'answers_num', 'links', 'profiles' ,'profilesummary','recorderinstall']
    tabledata = [groups, questions, questionaires, qdtype, qredundancy, qconstraints, answers, answers_num, links, profiles, profilesummary, recorderinstall]
    
    o.writeTables(tablenames, tabledata)
    o.anonAns() #anonymise and save answer tables
    
def saveRawProfiles(yearstart, yearend):
    """
    This function iterates through all profiles and saves them in a ordered directory structure by year and unit.
    """
    
    if yearstart < 2009:
        for year in range(yearstart, yearend + 1):
            for unit in ['A','V']:
                o.getProfiles(year, unit)
    elif yearstart >= 2009 and yearend <= 2014:       
        for year in range(yearstart, yearend + 1):
            for unit in ['A', 'V', 'kVA', 'Hz', 'kW']:
                o.getProfiles(year, unit)
    else:
        print('Years are out of range. Please select a year start and end date between 1994 and 2014')

def reduceRawProfiles(filepath = rawprofiles_dir):
    """
    This function uses a rolling window to reduce all raw load profiles to hourly mean values. Monthly load profiles are then concatenated into annual profiles and returned as a dictionary object.
    The data is structured as follows:
        dict[unit:{year:[list_of_profile_ts]}]
    
    """
    p = Path(filepath)
    for unit in ['A', 'V', 'kVA', 'Hz', 'kW']:
        for child in p.iterdir():
        #create empty directory to save files
            dir_path = os.path.join(hourlyprofiles_dir, unit)
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
                    if unit in ['A','V','Hz','kVA','kW']:
                        hourlydata = data.groupby(['RecorderID', 'ProfileID']).resample('H', on='Datefield').mean()
                    else:
                        print("Unit must be one of 'A', 'V', 'kVA', 'Hz', 'kW'")
                    hourlydata.reset_index(inplace=True)
                    hourlydata = hourlydata.loc[:, hourlydata.columns != 'Active']
                    ts = ts.append(hourlydata)
                    print(grandchild, unit)
                except:
                    print('Could not add data for ' + str(grandchild)) #skip if feather file does not exist 
        #write to reduced data to file
            if ts.empty:
                pass
            else:
                wpath = os.path.join(dir_path, year + '_' + unit + '.feather')
                feather.write_dataframe(ts, wpath)
                print('Write success')
    return
        