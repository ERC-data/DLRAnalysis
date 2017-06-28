# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pyodbc 


def getData(tablename = None, querystring = 'SELECT * FROM tablename'):
    "This function fetches a specified table from the DLR database and returns it as a pandas dataframe."
    
    #create connection object
    with open('cnxnstr.txt', 'r') as f: 
        cnxnstr = f.read().replace('\n', '')
    cnxn = pyodbc.connect(cnxnstr)
    cursor = cnxn.cursor()

    #specify and execute query(ies)
    if querystring == 'SELECT * FROM tablename':
        if tablename is None:
            return print('Specify a valid table from the DLR database')
        elif tablename == 'profiles':
            return print('The entire profiles table is too large to read into python in one go. Use the querystring argument to specify a profile data subset.') 
        else:
            query = 'SELECT * FROM [General_LR4].[dbo].%s' % (tablename)
    else:
        query = querystring
    cursor.execute(query)
    rows = cursor.fetchall() #fetch all query data 
    description = cursor.description #get result details
    colnames = [x[0] for x in description] #table column names
#    datatypes = [x[1] for x in description] #column data types

    #create dataframe with results
    results = []
    for row in rows:
        results.append(dict(zip(colnames, row)))
    df = pd.DataFrame(results)
    return df

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



#select all the average current values and sum for hourly data
AvgA = df.loc[(df['Description']=='A avg'), ['Datefield','Unitsread']]
#AvgA['ZeroA'] =  AvgA.apply(lambda x : 1 if (x['Unitsread'] == 0) else 0, axis = 1) #mark zero readings with 1
HourlyA = AvgA.resample('60Min', on='Datefield').sum()