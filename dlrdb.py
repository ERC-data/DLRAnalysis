# -*- coding: utf-8 -*-
"""
This file contains functions to fetch data from the Domestic Load Research database. Must be run from a server with a database installation.

"""

import pandas as pd
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

