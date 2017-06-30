# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 16:03:22 2017

@author: CKAN
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from dlrdb import getData, profilePeriod, getGroups, getProfileID

## GROUPS
groups = getGroups() #get all groups
g2000 = getGroups(2000) #get groups for 2000

## PROFILES
profiles = getProfileID()
profiles2000 = getProfileID(2000)


#specify and execute query(ies)
query1 = 'SELECT * FROM [General_LR4].[dbo].[linktable] WHERE ProfileID = 12005320'
query2 = 'SELECT * FROM [General_LR4].[dbo].[linktable] WHERE AnswerID = 1004196'
query = 'SELECT pt.ProfileID \
 ,lt.AnswerID \
 ,pt.Datefield \
 ,pt.Unitsread \
 ,pt.Valid \
 ,p.RecorderID \
 ,p.Active \
 ,puom.Description \
 FROM [General_LR4].[dbo].[Profiletable] pt \
 LEFT JOIN [General_LR4].[dbo].[profiles] p ON pt.ProfileID = p.ProfileId \
	LEFT JOIN [General_LR4].[dbo].[ProfileUnitsOfMeasure] puom ON p.[Unit of measurement] = puom.UnitsID \
		LEFT JOIN [General_LR4].[dbo].[linktable] lt ON pt.ProfileID = lt.ProfileID \
WHERE (pt.ProfileID = 12005320 OR pt.ProfileID = 12005321 OR pt.ProfileID = 12005322) AND lt.AnswerID != 0 \
ORDER BY pt.Datefield, pt.ProfileID'


df = getData(querystring = query)

#subset profile on date-time
april2012 = profilePeriod(df, '2012-04-01', '2012-04-30')

#select all the average current values and sum for hourly data
AvgA = df.loc[(df['Description']=='A avg'), ['Datefield','Unitsread']]

#AvgA['ZeroA'] =  AvgA.apply(lambda x : 1 if (x['Unitsread'] == 0) else 0, axis = 1) #mark zero readings with 1
HourlyA = AvgA.resample('60Min', on='Datefield').mean()
HourlyA['2012-06-01'].plot()

profiles = pd.crosstab(index=april2012['Datefield'], columns=[april2012['RecorderID'], april2012['ProfileID'], april2012['Description']], values = april2012['Unitsread'], aggfunc = sum)