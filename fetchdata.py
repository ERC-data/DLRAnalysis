# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 16:03:22 2017

@author: CKAN
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import feather

from sqldlr import getData, getProfileID, getProfiles, getSampleProfiles, profilePeriod, getGroups

def saveAllProfiles(mypath, yearstart, yearend):
    "This function fetches all profile data and saves it to path as a .feather file. It will take several hours to run!"
    for i in range(yearstart, yearend + 1):
        print(i)
        df = getProfiles(i)
        path = mypath + 'p' + str(i) + '.feather'
        print(path)
        feather.write_dataframe(df, path)

def savetables(datadict): 
    #paths = ['E:\\Domestic Load Research DB\\DBTables\\' + k + '.feather' for k in files]
    keys = datadict.keys()
    for k in keys:
        data = datadict[k].fillna(np.nan, inplace = True) #feather doesn't write None type
        path = 'E:\\Domestic Load Research DB\\DBTables\\' + k + '.feather'
        feather.write_dataframe(data, path)

# EXAMPLES
## Groups
groups = getGroups() #get all groups
g2000 = getGroups(2000) #get groups for 2000

## Profiles
pids = getProfileID()
pids2000 = getProfileID(2000)
sp2000 = getSampleProfiles(2000)
#p1994 = getProfiles(1994)

# Get profiles by specifying and executing query(ies)
query = 'SELECT * FROM [General_LR4].[dbo].[linktable] WHERE ProfileID = 12005320'
df = getData(querystring = query)

#subset profile on date-time
april2012 = profilePeriod(df, '2012-04-01', '2012-04-30')

#select all the average current values and sum for hourly data
AvgA = df.loc[(df['Description']=='A avg'), ['Datefield','Unitsread']]

#AvgA['ZeroA'] =  AvgA.apply(lambda x : 1 if (x['Unitsread'] == 0) else 0, axis = 1) #mark zero readings with 1
HourlyA = AvgA.resample('60Min', on='Datefield').mean()
HourlyA['2012-06-01'].plot()

profiles = pd.crosstab(index=april2012['Datefield'], columns=[april2012['RecorderID'], april2012['ProfileID'], april2012['Description']], values = april2012['Unitsread'], aggfunc = sum)

## Saving and loading
p1994.to_csv('E:\\Domestic Load Research DB\\DBTables\\Profiles\\p1994.csv', index=False, date_format='%Y-%m-%d %H:%M') #pretty rubbish. CSV can't cope
load94 = pd.read_csv('E:\\Domestic Load Research DB\\DBTables\\Profiles\\p1994.csv', dtype={'ProfileID':'category', 'RecorderID':'category', 'UoM':'category'}, parse_dates=['Datefield'])
april1994 = profilePeriod(load94, '1994-04-01', '1994-04-30')

#super fast data storage & retrieval with feather
#NB NOT FOR LONG TERM STORAGE!!
sp95 = getSampleProfiles(1995)
p95 = getProfiles(1995)
path = 'E:\\Domestic Load Research DB\\DBTables\\Profiles\\p95.feather'
feather.write_dataframe(p95, path)
feather95 = feather.read_dataframe(path)

