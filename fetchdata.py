# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 16:03:22 2017

@author: CKAN
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from dlrdb import getData, profilePeriod, getGroups, getProfileID, getProfiles, get1000Profiles, getProfilesOnly

## GROUPS
groups = getGroups() #get all groups
g2000 = getGroups(2000) #get groups for 2000

## PROFILES
profiles = getProfileID()
p2000 = getProfileID(2000)


#specify and execute query(ies)
query = 'SELECT * FROM [General_LR4].[dbo].[linktable] WHERE ProfileID = 12005320'
query2 = 'SELECT * FROM [General_LR4].[dbo].[linktable] WHERE AnswerID = 1004196'

#getting profiles
df = getData(querystring = query)

#subset profile on date-time
april2012 = profilePeriod(df, '2012-04-01', '2012-04-30')

#select all the average current values and sum for hourly data
AvgA = df.loc[(df['Description']=='A avg'), ['Datefield','Unitsread']]

#AvgA['ZeroA'] =  AvgA.apply(lambda x : 1 if (x['Unitsread'] == 0) else 0, axis = 1) #mark zero readings with 1
HourlyA = AvgA.resample('60Min', on='Datefield').mean()
HourlyA['2012-06-01'].plot()

profiles = pd.crosstab(index=april2012['Datefield'], columns=[april2012['RecorderID'], april2012['ProfileID'], april2012['Description']], values = april2012['Unitsread'], aggfunc = sum)