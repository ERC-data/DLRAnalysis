# -*- coding: utf-8 -*-
"""

@author: Wiebke Toussaint

This file contains functions to fetch data from the Domestic Load Research SQL Server database. It must be run from a server with a DLR database installation.

The following functions are defined:
    getData 
    getProfileID
    getMetaProfiles
    profileFetchEst
    getProfiles
    getSampleProfiles
    profilePeriod
    getGroups
    getLocation
    saveTables
    saveAllProfiles
    anonAns
    
SOME EXAMPLES 

# Using getData with SQL queries:

query = 'SELECT * FROM [General_LR4].[dbo].[linktable] WHERE ProfileID = 12005320'
df = getData(querystring = query)
    
"""

import pandas as pd
import numpy as np
import pyodbc 
import feather
import os

from support import dlrdb_dir, src_dir

def getData(tablename = None, querystring = 'SELECT * FROM tablename', chunksize = 10000):
    """
    Fetches a specified table from the DLR database and returns it as a pandas dataframe.

    """
    #connection object:
    with open(os.path.join(src_dir, 'cnxnstr.txt'), 'r') as f: 
        cnxnstr = f.read().replace('\n', '')
    cnxn = pyodbc.connect(cnxnstr)
    
    #specify and execute query(ies):
    if querystring == "SELECT * FROM tablename":
        if tablename is None:
            return print('Specify a valid table from the DLR database')
        elif tablename == 'Profiletable':
            return print('The profiles table is too large to read into python in one go. Use the getProfiles() function.') 
        else:
            query = "SELECT * FROM [General_LR4].[dbo].%s" % (tablename)
    else:
        query = querystring
        
    df = pd.read_sql(query, cnxn)   #read to dataframe   
    return df

def getProfileID(year = None):
    """
    Fetches all profile IDs for a given year. None returns all profile IDs.
    
    """
    links = getData('LinkTable')
    allprofiles = links[(links.GroupID != 0) & (links.ProfileID != 0)]
    if year is None:
        return allprofiles
    #match GroupIDs to getGroups to get the profile years:
    else:
        profileid = pd.Series(allprofiles.loc[allprofiles.GroupID.isin(getGroups(year).GroupID), 'ProfileID'].unique())
    return profileid

def getMetaProfiles(year, units = None):
    """
    Fetches profile meta data. Units must be one of  V or A. From 2009 onwards kVA, Hz and kW have also been measured.
    
    """
    #list of profiles for the year:
    pids = pd.Series(map(str, getProfileID(year))) 
    #get observation metadata from the profiles table:
    metaprofiles = getData('profiles')[['Active','ProfileId','RecorderID','Unit of measurement']]
    metaprofiles['Unit of measurement'].dropna(inplace=True)
    metaprofiles = metaprofiles[metaprofiles.ProfileId.isin(pids)] #select subset of metaprofiles corresponding to query
    metaprofiles.rename(columns={'Unit of measurement':'UoM'}, inplace=True)
    metaprofiles.loc[:,['UoM', 'RecorderID']] = metaprofiles.loc[:,['UoM', 'RecorderID',]].apply(pd.Categorical)
    puom = getData('ProfileUnitsOfMeasure')
    cats = list(puom.loc[puom.UnitsID.isin(metaprofiles['UoM'].cat.categories), 'Description'])
    metaprofiles['UoM'].cat.categories = cats

    if units is None:
        plist = metaprofiles['ProfileId']
    elif units in ['V','A','kVA','kW']:
        uom = units.strip() + ' avg'
        plist = metaprofiles[metaprofiles.UoM == uom]['ProfileId']
    elif units=='Hz':
        uom = 'Hz'
        plist = metaprofiles[metaprofiles.UoM == uom]['ProfileId']
    else:
        return print('Check spelling and choose V, A, kVA, Hz or kW as units, or leave blank to get profiles of all.')
    return metaprofiles, plist

def writeProfile(df, group_year, profile_year, profile_month, units, dlrdb_sub_dir):
    """
    Creates folder structure and saves profiles as feather file.
    """
    dir_path = os.path.join(dlrdb_dir, 'profiles', dlrdb_sub_dir, str(group_year), str(profile_year) + '-' + str(profile_month))
    os.makedirs(dir_path , exist_ok=True)
    path = os.path.join(dir_path, str(profile_year) + '-' + str(profile_month) + '_' + str(units) + '.feather')
    print(path)
    feather.write_dataframe(df, path)
    print('Write success')    

def getProfiles(year, units = 'A'):
    """
    This function fetches load profiles for one calendar year. 
    It takes the year as number and units as string:
        [A, V] for 1994 - 2008 
        [A, V, kVA, Hz, kW] for 2009 - 2014
    
    """
    ## Get metadata
    mp, plist = getMetaProfiles(year, units)
    
    ## Get profiles from server
    subquery = ', '.join(str(x) for x in plist)
    for i in range(1,13):
        try:
            query = "SELECT pt.ProfileID \
             ,pt.Datefield \
             ,pt.Unitsread \
             ,pt.Valid \
            FROM [General_LR4].[dbo].[Profiletable] pt \
            WHERE pt.ProfileID IN (" + subquery + ") AND MONTH(Datefield) =" + str(i) + " \
            ORDER BY pt.Datefield, pt.ProfileID"
            profiles = getData(querystring = query)
            #profiles['Valid'] = profiles['Valid'].map(lambda x: x.strip()).map({'Y':True, 'N':False}) #reduce memory usage
        
            #data output:    
            df = pd.merge(profiles, mp, left_on='ProfileID', right_on='ProfileId')
            df.drop('ProfileId', axis=1, inplace=True)
            #convert strings to category data type to reduce memory usage
            df.loc[:,['ProfileID','Valid']] = df.loc[:,['ProfileID','Valid']].apply(pd.Categorical)
            
            head_year = df.head(1).Datefield.dt.year[0]
            tail_year = df.tail(1).Datefield.dt.year[len(df)-1]
            profile_month = df.Datefield[0].month
            
            if head_year == tail_year: #check if dataframe contains profiles for two years
                writeProfile(df, year, head_year, profile_month, units, 'raw')
            else:
                #split dataframe into two years and save separately
                head_df = df[df.Datefield.dt.year == head_year].reset_index(drop=True)
                writeProfile(head_df, year, head_year, profile_month, units, 'raw')               
                tail_df = df[df.Datefield.dt.year == tail_year].reset_index(drop=True)
                writeProfile(tail_df, year, tail_year, profile_month, units, 'raw')
        except:
            pass
    return

def getSampleProfiles(year):
    """
    This function provides a sample of the top 1000 rows that will be returned with the getProfiles() function
    
    """
    ## Get metadata
    mp, plist = getMetaProfiles(year, units = None)
    mp = mp[0:1]
    plist = plist[0:1]
    
    ## Get profiles from server
    subquery = ', '.join(str(x) for x in plist) #' OR pt.ProfileID = '.join(plist.map(lambda x: str(x)))
    query = "SELECT TOP 1000 pt.ProfileID, pt.Datefield, pt.Unitsread, pt.Valid FROM [General_LR4].[dbo].[Profiletable] pt WHERE pt.ProfileID IN (" + subquery + ") ORDER BY pt.Datefield, pt.ProfileID"
    profiles = getData(querystring = query)
    profiles['Valid'] = profiles['Valid'].map(lambda x: x.strip()).map({'Y':True, 'N':False}) #reduce memory usage

    ## Create data output    
    df = pd.merge(profiles, mp, left_on='ProfileID', right_on='ProfileId')
    df.drop('ProfileId', axis=1, inplace=True)
    df.loc[:,['ProfileID']] = df.loc[:,['ProfileID']].apply(pd.Categorical)     #convert to category type to reduce memory
    return df

def getProfileStart(year):
    """
    This function provides the start month for profiles in a given year.
    
    """
    ## Get metadata
    mp, plist = getMetaProfiles(year, units = None)
    mp = mp[0:1]
    plist = plist[0:1]
    
    ## Get profiles from server
    subquery = ', '.join(str(x) for x in plist) #' OR pt.ProfileID = '.join(plist.map(lambda x: str(x)))
    query = "SELECT TOP 1 pt.ProfileID, pt.Datefield, pt.Unitsread, pt.Valid FROM [General_LR4].[dbo].[Profiletable] pt WHERE pt.ProfileID IN (" + subquery + ") ORDER BY pt.Datefield, pt.ProfileID"
    profiles = getData(querystring = query)
    year = profiles.loc[0, 'Datefield'].year
    month = profiles.loc[0, 'Datefield'].month
    return year, month

def getGroups(year = None):
    """
    This function performs some massive Groups wrangling
    
    """
    groups = getData('Groups')
    groups['ParentID'].fillna(0, inplace=True)
    groups['ParentID'] = groups['ParentID'].astype('int64').astype('category')
    groups['GroupName'] = groups['GroupName'].map(lambda x: x.strip())
    #TRY THIS groups['GroupName'] = groups['GroupName'].str.strip()
    
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
    
    #reconstruct group levels as one pretty, multi-index table
    recon3 = pd.merge(groups_level_4, g3, left_on ='ParentID', right_on = 'GroupID' , how='left', suffixes = ['_4','_3'])
    recon2 = pd.merge(recon3, g2, left_on ='ParentID_3', right_on = 'GroupID' , how='left', suffixes = ['_3','_2'])
    recon1 = pd.merge(recon2, g1, left_on ='ParentID', right_on = 'GroupID' , how='left', suffixes = ['_2','_1'])
    prettyg = recon1[['ContextID','GroupID_1','GroupID_2','GroupID_3','GroupID_4','GroupName_1','GroupName_2','GroupName_3','GroupName_4']]
    prettynames = ['ContextID', 'GroupID_1','GroupID_2','GroupID_3','GroupID','Dom_NonDom','Survey','Year','Location']
    prettyg.columns = prettynames
    
    #create multi-index dataframe
    allgroups = prettyg.set_index(['GroupID_1','GroupID_2','GroupID_3']).sort_index()
    
    if year is None:
        return allgroups
    #filter dataframe on year
    else:
        stryear = str(year)
        return allgroups[allgroups['Year']== stryear] 

def writeTables(names, dataframes): 
    """
    This function saves a dictionary of name:dataframe items from a list of names and a list of dataframes as feather files.
    The getData() and getGroups() functions can be used to construct the dataframes.
    
    """
    datadict = dict(zip(names, dataframes))
    for k in datadict.keys():
        if datadict[k].size == datadict[k].count().sum():
            data = datadict[k]
        else:  
            data = datadict[k].fillna(np.nan) #feather doesn't write None type
        os.makedirs(os.path.join(dlrdb_dir, 'data', 'tables') , exist_ok=True)
        path = os.path.join(dlrdb_dir, 'data', 'tables', k + '.feather')
        feather.write_dataframe(data, path)
    return
        
def anonAns():
    """
    This function fetches survey responses and anonymises them, then returns and saves the anonymsed dataset as feather object.
    The information on which questions to anonymise is contained in two csv files, blobQs.csv and charQs.csv.
    
    """
    anstables = {'Answers_blob':'blobQs.csv', 'Answers_char':'charQs.csv'}    
    for k,v in anstables.items():
        a = getData(k) #get all answers
        qs = pd.read_csv(os.path.join('anonymise', v))
        qs = qs.loc[lambda qs: qs.anonymise == 1, :]
        qanon = pd.merge(getData('Answers'), qs, left_on='QuestionaireID', right_on='QuestionaireID')[['AnswerID','ColumnNo','anonymise']]
        
        for i, rows in qanon.iterrows():
            a.set_value(a[a.AnswerID == rows.AnswerID].index[0], str(rows.ColumnNo),'a')
        
        tableToFeather([k.lower() + '_anon'],[a]) #saves answers as feather object
    return