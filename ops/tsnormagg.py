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

from socios import loadTables

src_dir = str(Path(__file__).parents[1])
dlrdb_dir = str(Path(__file__).parents[2])
data_dir = os.path.join(dlrdb_dir, 'profiles', 'hourly')

def loadProfiles(year, unit):
    """
    This function loads a year's unit profiles into a dataframe.
    
    """
    data = feather.read_dataframe(os.path.join(data_dir, unit, year + '_' + unit + '.feather')) #load data
    return data

def shapeProfiles(data):
    """
    This function reshapes a year's unit profiles into a dataframe indexed by date, with profile IDs as columns and units read as values. 'data' should be a pandas data frame constructed with the loadProfiles() function.
    Rows with Valid=0 are removed.
    
    """
    valid_data = data[data.Valid > 0] #remove invalid data - valid for 10min readings = 6, valid for 5min readings = 12
    sorted_data = valid_data.sort_values(by='Datefield') #sort by date
    sorted_data.ProfileID = sorted_data.ProfileID.apply(lambda x: str(x))
    print(data.head())
    pretty_data = sorted_data.set_index(['Datefield','ProfileID']).unstack()['Unitsread'] #reshape dataframe
    return pretty_data

def nanAnalysis(shapedProfile):
    #prep data
    fullrows = shapedProfile.count(axis=1)/shapedProfile.shape[1]
    fullcols = shapedProfile.count(axis=0)/shapedProfile.shape[0]
    
    rowplot = go.Bar(x=fullrows.index, y=fullrows.values)
    colplot = go.Bar(x=fullcols.index, y=fullcols.values)
    
    fig = py.tools.make_subplots(rows=2, cols=1)
    
    fig.append_trace(rowplot, 1, 1)
    fig.append_trace(colplot, 2, 1)
    
    plot(fig)
    
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

def getProfilePower(year ):
    iprof = loadProfiles(year, 'A')
    vprof = loadProfiles(year, 'V')
    links = loadTables().get('links')
    links = links.loc[:, ['AnswerID','ProfileID']].dropna()
    links = links[links.AnswerID != 0]
    
    ilink = iprof.merge(links, on='ProfileID')
    vlink = vprof.merge(links, on='ProfileID')