# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 08:31:00 2017

@author: Wiebke Toussaint

Load Subclass Model
    based on data from DTPET up to 2009 and the GLF 
- load shape over time
- trajectory of load growth over time
- distinct name of customers whome the load subclass represents

model attributes
ATTRIBUTES
* power (kW)
* power factor
* load factor
TYPE
* hour of the day
* day type: weekday / weekend
* season: high / low

process
* exclude public holidays
* normalise all profiles in subclass by annual energy
* average annual curves to arrive at a subclass load shape
* aggregate

"""

import feather
import os
from pathlib import Path
import plotly as py
from plotly.offline import plot
import plotly.graph_objs as go
import pandas as pd
import numpy as np

import socios as s

src_dir = str(Path(__file__).parents[0])
dlrdb_dir = str(Path(__file__).parents[1])
profile_dir = os.path.join(dlrdb_dir, 'profiles', 'hourly')

def loadProfiles(year, unit):
    """
    This function loads a year's hourly unit profiles into a dataframe and returns it together with the year and unit concerned.
    
    """
    data = feather.read_dataframe(os.path.join(profile_dir, unit, str(year) + '_' + unit + '.feather')) #load data
    return data, year, unit

def shapeProfiles(annualunitprofile):
    """
    This function reshapes a year's unit profiles into a dataframe indexed by date, with profile IDs as columns and units read as values.
    annualunitprofile variable should be a pandas data frame constructed with the loadProfiles() function.
    Rows with Valid=0 are removed.
    
    The function returns a shaped dataframe indexed by hour with aggregated unit values for all profiles, the year and unit concerned.
    
    """
    data = annualunitprofile[0]
    year = annualunitprofile[1]
    unit = annualunitprofile[2]
    
    valid_data = data[data.Valid > 0] #remove invalid data - valid for 10min readings = 6, valid for 5min readings = 12
    sorted_data = valid_data.sort_values(by='Datefield') #sort by date
    sorted_data.ProfileID = sorted_data.ProfileID.apply(lambda x: str(x))
    print(data.head())
    pretty_data = sorted_data.set_index(['Datefield','ProfileID']).unstack()['Unitsread'] #reshape dataframe
    return pretty_data, year, unit

def nanAnalysis(shapedprofile, threshold = 0.95):
    """
    This function displays information about the missing values for all customers in a load profile unit year.
    shapedprofile is a dataframe that has been created with shapeProfiles.
    threshold 
    
    The function returns:
        * two graphs with summary statistics of all profiles
        * the percentage of profiles and measurement days with full observational data above the threshold value.
    """
    data = shapedprofile[0]
    year = shapedprofile[1]
    unit = shapedprofile[2]

    #prep data
    fullrows = data.count(axis=1)/data.shape[1]
    fullcols = data.count(axis=0)/data.shape[0]
    
    rowplot = go.Scatter(x=fullrows.index, y=fullrows.values)
    colplot = go.Bar(x=fullcols.index, y=fullcols.values)
#    thresh = go.Scatter(x=fullrows.index, y=threshold, mode = 'lines', name = 'threshold', line = dict(color = 'red'))
    
    fig = py.tools.make_subplots(rows=2, cols=1)
    
    fig.append_trace(rowplot, 1, 1)
    fig.append_trace(colplot, 2, 1)
#    fig.append_trace(thresh, 2, 1)
    
    plot(fig)
    
    goodhours = len(fullcols[fullcols > threshold]) / len(fullcols) * 100
    goodprofiles = len(fullrows[fullrows > threshold]) / len(fullrows) * 100
    
    print('{:.2f}% of hours have over {:.0f}% fully observed profiles.'.format(goodhours, threshold * 100))
    print('{:.2f}% of profiles have been observed over {:.0f}% of time.'.format(goodprofiles, threshold * 100))
    
    return 
    
#investigating one location
def locationSummarySum(locstring, data, interval):
    """
    Use in conjunction with socios.recorderLocations() to get locstrings for locations of interest. Sum should be used for kW and kVA profiles.
    
    """
    loc = data[data.RecorderID.str.contains(locstring.upper())]
    monthly = loc.groupby(['RecorderID','ProfileID']).resample(interval, on='Datefield').sum()
    return monthly.describe()


def locationSummaryMean(locstring, data, interval):
    """
    Use in conjunction with socios.recorderLocations() to get locstrings for locations of interest. Mean should be used for A, V and Hz profiles.
    
    """
    loc = data[data.RecorderID.str.contains(locstring.upper())]
    monthly = loc.groupby(['RecorderID','ProfileID']).resample(interval, on='Datefield').mean()
    return monthly.describe()

def getProfilePower(year):
    #get list of AnswerIDs in variable year
    a_id = s.loadID(year, id_name = 'AnswerID')
    
    #get dataframe of linkages between AnswerIDs and ProfileIDs
    links = s.loadTables().get('links')
    year_links = links[links.AnswerID.isin(a_id)]
    year_links = year_links.loc[year_links.ProfileID != 0, ['AnswerID','ProfileID']]    
    
    #get profile metadata (recorder ID, recording channel, recorder type, units of measurement)
    profiles = s.loadTables().get('profiles')
    #add AnswerID information to profiles metadata
    profile_meta = year_links.merge(profiles, left_on='ProfileID', right_on='ProfileId').drop('ProfileId', axis=1)        
    VI_profile_meta = profile_meta.loc[(profile_meta['Unit of measurement'] == 2), :] #select current profiles only
        
    #get profile data for year
    iprofile = loadProfiles(year, 'A')[0]    
    vprofile = loadProfiles(year, 'V')[0]
    
    if year < 2009: #pre-2009 recorder type is set up so that up to 12 current profiles share one voltage profile
        #get list of ProfileIDs in variable year
        p_id = s.loadID(year, id_name = 'ProfileID')
        year_profiles = profiles[profiles.ProfileId.isin(p_id)]        
        vchan = year_profiles.loc[year_profiles['Unit of measurement']==1, ['ProfileId','RecorderID']] #get metadata for voltage profiles

        iprofile = iprofile.merge(vchan, on='RecorderID', suffixes=('_i','_v'))
        iprofile.rename(columns={"ProfileId": "matchcol"}, inplace=True)        
        power = iprofile.merge(vprofile, left_on=['matchcol', 'Datefield'], right_on=['ProfileID','Datefield'], suffixes=['_i', '_v'])

    elif 2009 <= year <= 2014: #recorder type is set up so that each current profile has its own voltage profile

        vprofile['matchcol'] = vprofile['ProfileID'] + 1
        power = vprofile.merge(iprofile, left_on=['matchcol', 'Datefield'], right_on=['ProfileID','Datefield'], suffixes=['_v', '_i'])
                
    else:
        return print('Year is out of range. Please select a year between 1994 and 2014')
    
    power = power.loc[:,['RecorderID_v', 'ProfileID_v', 'Datefield', 'Unitsread_v', 'ProfileID_i', 'Unitsread_i']]
    power.columns = ['RecorderID','V_ProfileID','Datefield','V_Unitsread','I_ProfileID','I_Unitsread']
    power['kWh_calculated'] = power.V_Unitsread*power.I_Unitsread*0.001
    output = power.merge(VI_profile_meta.loc[:,['AnswerID','ProfileID']], left_on='I_ProfileID', right_on='ProfileID').drop('ProfileID', axis=1)
    
    return output

def aggClassProfile(year, class_dir = 'exp'):
    """
    This function gets the inferred class for each AnswerID and aggregates the profiles by month, day type and hour of the day.
    """
    
    dirpath = os.path.join(dlrdb_dir, 'data', 'classes', class_dir)
    filename = 'classes_' + str(year) + '.csv'
    
    #get data
    classes = pd.read_csv(os.path.join(dirpath, filename), header=None, names=['AnswerID','class'])
    profiles = getProfilePower(year)
    
    #add class label to profile IDs
    df = classes.merge(profiles, on='AnswerID')
    
    #manipulate dataframe to match DPET hourly summary output
    df['Month'] = df['Datefield'].dt.month
    daytypebins = [0, 5, 6, 7]
    daytypelabels = ['Weekday', 'Saturday', 'Sunday']
    df['DayType'] = pd.cut(df.Datefield.dt.weekday, bins = daytypebins, labels = daytypelabels, right=False, include_lowest=True)
    df['Hour'] = df['Datefield'].dt.hour
    
    grouped = df.groupby(['class','Month','DayType','Hour'])
    classprofile = grouped['kWh_calculated'].agg([np.mean, np.std]).rename(columns={'mean': 'mean_kWh','std': 'std_kWh'})
    
    return classprofile

def aggProfile(AnswerID):
    return