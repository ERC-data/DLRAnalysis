# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 16:03:22 2017

@author: Wiebke Toussaint

This file contains functions to fetch and save data from the DLR SQL database. saveTables() saves socio-demographic data. Sensitive personal information is removed with the anonAns() function. saveProfiles() saves the load profiles for each year in a specified range.

NOTE: These functions require access to a DLR SQL database instance.
"""
import pandas as pd
import os

from support import obs_dir
import observations.obshelpers as o

def saveTables():
    """
    This function fetches tables from the SQL database and saves them as a feather object. 
    """
    #get and save important tables
    groups = o.getGroups() 
    questions = o.getData('Questions')
    questionaires = o.getData('Questionaires')
    qdtype = o.getData('QDataType')
    qredundancy = o.getData('QRedundancy')
    qconstraints = o.getData('QConstraints')
    answers = o.getData('Answers')
    links = o.getData('LinkTable')
    profiles = o.getData('Profiles')
    profilesummary = o.getData('ProfileSummaryTable')
    recorderinstall = o.getData('RECORDER_INSTALL_TABLE')
    
    tablenames = ['groups', 'questions', 'questionaires', 'qdtype', 'qredundancy', 'qconstraints', 'answers', 'links', 'profiles' ,'profilesummary','recorderinstall']
    tabledata = [groups, questions, questionaires, qdtype, qredundancy, qconstraints, answers, links, profiles, profilesummary, recorderinstall]
    
    o.writeTables(tablenames, tabledata)
 
def saveAnswers():
    """
    This function fetches survey responses and anonymises them to remove all discriminating personal information of respondents. The anonymsed dataset is returned and saved as a feather object.
    Details for questions to anonymise are contained in two csv files, anonymise/blobQs.csv and anonymise/charQs.csv.
    
    """
    anstables = {'Answers_blob':'blobQs.csv', 'Answers_char':'charQs.csv', 'Answers_Number':None}    
    for k,v in anstables.items():
        a = o.getData(k) #get all answers
        if v is None:
            pass
        else:
            qs = pd.read_csv(os.path.join(obs_dir, 'anonymise', v))
            qs = qs.loc[lambda qs: qs.anonymise == 1, :]
            qanon = pd.merge(o.getData('Answers'), qs, left_on='QuestionaireID', right_on='QuestionaireID')[['AnswerID','ColumnNo','anonymise']]
            for i, rows in qanon.iterrows():
                a.set_value(a[a.AnswerID == rows.AnswerID].index[0], str(rows.ColumnNo),'a')
        
        o.writeTables([k.lower() + '_anon'],[a]) #saves answers as feather object
    return
    
def saveRawProfiles(yearstart, yearend):
    """
    This function iterates through all profiles and saves them in a ordered directory structure by year and unit.
    """
    
    if yearstart < 2009:
        for year in range(yearstart, yearend + 1):
            for unit in ['A','V']:
                for month in range(1, 13):
                    o.writeProfiles(year, month, unit)
    elif yearstart >= 2009 and yearend <= 2014:       
        for year in range(yearstart, yearend + 1):
            for unit in ['A', 'V', 'kVA', 'Hz', 'kW']:
                for month in range(1, 13):
                    o.writeProfiles(year, month, unit)
    else:
        print('Years are out of range. Please select a year start and end date between 1994 and 2014')
