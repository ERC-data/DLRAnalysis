# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 16:03:22 2017

@author: CKAN
"""

import fetch_support as f
from datetime import datetime

def saveTables():
    groups = f.getGroups() 
    questions = f.getData('Questions')
    questionaires = f.getData('Questionaires')
    qdtype = f.getData('QDataType')
    qredundancy = f.getData('QRedundancy')
    qconstraints = f.getData('QConstraints')
    answerid = f.getAnswerID()
    answers = f.getData('Answers')
    answers_num = f.getData('Answers_Number')
    links = f.getData('LinkTable')
    profileid = f.getProfileID()
    profilesummary = f.getData('ProfileSummaryTable')
    
    tablenames = ['groups', 'questions', 'questionaires', 'qdtype', 'qredundancy', 'qconstraints', 'answerid', 'answers', 'answers_num', 'links', 'profileid' ,'profilesummary']
    tabledata = [groups, questions, questionaires, qdtype, qredundancy, qconstraints, answerid, answers, answers_num, links, profileid, profilesummary]
    
    f.saveTables(tablenames, tabledata)
    f.anonAns()
    
def saveProfiles(yearstart, yearend):
    if yearstart < 2009:
        for year in range(yearstart, yearend + 1):
            for unit in ['A','V']:
                f.getProfiles(year, unit)
    elif yearstart >= 2009 and yearend <= 2014:       
        for year in range(yearstart, yearend + 1):
            for unit in ['A', 'V', 'kVA', 'Hz', 'kW']:
                f.getProfiles(year, unit)
    else:
        print('Years are out of range. Please select a year start and end date between 1994 and 2014')
        
def profilePeriod(dataframe, startdate = None, enddate = None):
    """
    This function selects a subset of a profile dataframe based on a date range. Use getProfiles or upload profiles data. 
    Dates must be formated as 'YYYY-MM-DD'. Days start at 00:00 and end at 23:55
    
    """
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
    #df.loc[:,['AnswerID', 'ProfileID', 'Description', 'RecorderID', 'Valid']] = df.loc[:,['AnswerID', 'ProfileID', 'Description', 'RecorderID', 'Valid']].apply(pd.Categorical)
    return df
