# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 16:03:22 2017

@author: CKAN
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import feather
import extract_support

dbTables = ['Answers','Answers_Number','','','','','','','']


# save anonymised answer_blob and answer_char tables
extract_support.anonAns()


def saveAllProfiles(mypath, yearstart, yearend):
    "This function fetches all profile data and saves it to path as a .feather file. It will take several hours to run!"
    for i in range(yearstart, yearend + 1):
        print(i)
        df = extract_support.getProfiles(i)
        path = mypath + 'p' + str(i) + '.feather'
        print(path)
        feather.write_dataframe(df, path)

# EXAMPLES
## Groups
groups = extract_support.getGroups() #get all groups
g2000 = extract_support.getGroups(2000) #get groups for 2000

## Profiles
pids = extract_support.getProfileID()
pids2000 = extract_support.getProfileID(2000)
sp2000 = extract_support.getSampleProfiles(2000)
#p1994 = getProfiles(1994)

# Get profiles by specifying and executing query(ies)
query = 'SELECT * FROM [General_LR4].[dbo].[linktable] WHERE ProfileID = 12005320'
df = extract_support.getData(querystring = query)

#subset profile on date-time
april2012 = extract_support.profilePeriod(df, '2012-04-01', '2012-04-30')

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


