# -*- coding: utf-8 -*-
"""
This file contains functions to fetch data from the Domestic Load Research database. Must be run from a server with a database installation.

"""

import pandas as pd
import pyodbc 
from datetime import datetime

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

def dataPeriod(dataframe, startdate = None, enddate = None):
    "This function selects a subset of a dataframe based on a date range." 
    "Dates must be formated as 'YYYY-MM-DD'. Days start at 00:00 and end at 23:55"
    
    #print profile date info
    dataStart = dataframe['Datefield'].min()
    dataEnd = dataframe['Datefield'].max()
    print('Profile starts on %s. \nProfile ends on %s.' % (dataStart, dataEnd))
    
    #prompt for user input if no start and end dates were provided
    startdate = input('Enter period start date as YYYY-MM-DD\n') if startdate is None else startdate
    enddate = input('Enter period end date as YYYY-MM-DD\n') if enddate is None else enddate
    
    #convert start and end date user input to datetime object
    if isinstance(startdate, str):
        startdate = datetime.strptime(startdate + ' 00:00', '%Y-%m-%d %H:%M')
    if isinstance(enddate, str):
        enddate = datetime.strptime(enddate + ' 23:55', '%Y-%m-%d %H:%M')
    
    #check that input dates fall within the profile period
    if startdate > enddate :
        return print('Period start must be before period end.')
    if datetime.date(startdate) == datetime.date(dataStart): #set start date to data start to avoid time error
        startdate = dataStart
    if datetime.date(enddate) == datetime.date(dataEnd): #set end date to data end to avoid time error
        enddate = dataEnd
    if (startdate < dataStart) | (startdate > dataEnd):
        return print('This profile starts on %s and ends on %s. Choose a start date that falls within this period.' % (dataStart, dataEnd))
    if (enddate < dataStart) | (enddate > dataEnd):
        return print('This profile starts on %s and ends on %s. Choose an end date that falls within this period.' % (dataStart, dataEnd))
    
    #subset dataframe by the specified date range
    df = dataframe.loc[(dataframe['Datefield'] >= startdate) & (dataframe['Datefield'] <= enddate)]
    return df