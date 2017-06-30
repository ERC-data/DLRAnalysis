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
    print(df.info())
    return df

def profilePeriod(dataframe, startdate = None, enddate = None):
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
    df = dataframe.loc[(dataframe['Datefield'] >= startdate) & (dataframe['Datefield'] <= enddate)].reset_index(drop=True)
    #convert strings to category data type to reduce memory usage
    df.loc[:,['AnswerID', 'ProfileID', 'Description', 'RecorderID', 'Valid']] = df.loc[:,['AnswerID', 'ProfileID', 'Description', 'RecorderID', 'Valid']].apply(pd.Categorical)
    return df

def getGroups():
    "This function performs some massive Groups wrangling"
    groups = getData('Groups')
    groups['ParentID'].fillna(0, inplace=True)
    groups['ParentID'] = groups['ParentID'].astype('int64').astype('category')
    groups['GroupName'] = groups['GroupName'].map(lambda x: x.strip())
    
    #Deconstruct groups table apart into levels
    #LEVEL 1 GROUPS: domestic/non-domestic
    groups_level_1 = groups[groups['ParentID']==0] 
    #LEVEL 2 GROUPS: Eskom LR, NRS LR, Namibia, Clinics, Shops, Schools
    groups_level_2 = groups[groups['ParentID'].isin(groups_level_1['GroupID'])]
    #LEVLE 3 GROUPS: Years
    groups_level_3 = groups[groups['ParentID'].isin(groups_level_2['GroupID'])]
    #LEVLE 4 GROUPS: Locations
    groups_level_4 = groups[groups['ParentID'].isin(groups_level_3['GroupID'])]
    
    #Slim down the group levels to only include columns requried for merging
    g1 = groups.loc[groups['ParentID']==0,['GroupID','ParentID','GroupName']].reset_index(drop=True)
    g2 = groups.loc[groups['ParentID'].isin(groups_level_1['GroupID']), ['GroupID','ParentID','GroupName']].reset_index(drop=True)
    g3 = groups.loc[groups['ParentID'].isin(groups_level_2['GroupID']), ['GroupID','ParentID','GroupName']].reset_index(drop=True)
    
    #Reconstruct group levels as one pretty, multi-index table
    recon3 = pd.merge(groups_level_4, g3, left_on ='ParentID', right_on = 'GroupID' , how='left', suffixes = ['_4','_3'])
    recon2 = pd.merge(recon3, g2, left_on ='ParentID_3', right_on = 'GroupID' , how='left', suffixes = ['_3','_2'])
    recon1 = pd.merge(recon2, g1, left_on ='ParentID', right_on = 'GroupID' , how='left', suffixes = ['_2','_1'])
    prettyg = recon1[['ContextID','GroupID_1','GroupID_2','GroupID_3','GroupID_4','GroupName_1','GroupName_2','GroupName_3','GroupName_4']]
    prettynames = ['ContextID', 'GroupID_1','GroupID_2','GroupID_3','GroupID_4','Dom_NonDom','Survey','Year','Location']
    prettyg.columns = prettynames
    
    #Create multi-index dataframe
    allgroups = prettyg.set_index(['GroupID_1','GroupID_2','GroupID_3','GroupID_4']).sort_index()
    
    return allgroups
