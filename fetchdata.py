# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 16:03:22 2017

@author: CKAN
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from dlrdb import getData

#specify and execute query(ies)
query1 = 'SELECT * FROM [General_LR4].[dbo].[linktable] WHERE ProfileID = 12005320'
query2 = 'SELECT * FROM [General_LR4].[dbo].[linktable] WHERE AnswerID = 1004196'
query = 'SELECT pt.ProfileID \
 ,pt.Datefield \
 ,pt.Unitsread \
 ,pt.Valid \
 ,p.RecorderID \
 ,p.Active \
 ,puom.Description \
 ,puom.UnitsID \
 FROM [General_LR4].[dbo].[Profiletable] pt \
 LEFT JOIN [General_LR4].[dbo].[profiles] p ON pt.ProfileID = p.ProfileId \
	LEFT JOIN [General_LR4].[dbo].[ProfileUnitsOfMeasure] puom ON p.[Unit of measurement] = puom.UnitsID \
WHERE pt.ProfileID = 12005320 OR pt.ProfileID = 12005321 OR pt.ProfileID = 12005322 \
ORDER BY pt.Datefield, pt.ProfileID'


df = getData(querystring = query)
#select all the average current values and sum for hourly data
AvgA = df.loc[(df['Description']=='A avg'), ['Datefield','Unitsread']]
#AvgA['ZeroA'] =  AvgA.apply(lambda x : 1 if (x['Unitsread'] == 0) else 0, axis = 1) #mark zero readings with 1
HourlyA = AvgA.resample('60Min', on='Datefield').mean()
HourlyA['2012-06-01'].plot()