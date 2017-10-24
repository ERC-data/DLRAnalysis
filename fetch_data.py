# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 16:03:22 2017

@author: Wiebke Toussaint

This file contains functions to fetch and save data from the DLR SQL database. saveTables() saves socio-demographic data. Sensitive personal information is removed with the anonAns() function. saveProfiles() saves the load profiles for each year in a specified range.

NOTE: These functions require access to a DLR SQL database instance.
"""

import fetch_support as f

def saveTables():
    """
    This function fetches tables from the SQL database and saves them as a feather object. Answer tables are anonymsed to remove all discriminating personal information of respondents.
    """
    
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
    profiles = f.getData('Profiles')
    profilesummary = f.getData('ProfileSummaryTable')
    recorderinstall = f.getData('RECORDER_INSTALL_TABLE')
    
    tablenames = ['groups', 'questions', 'questionaires', 'qdtype', 'qredundancy', 'qconstraints', 'answerid', 'answers', 'answers_num', 'links', 'profiles' ,'profilesummary','recorderinstall']
    tabledata = [groups, questions, questionaires, qdtype, qredundancy, qconstraints, answerid, answers, answers_num, links, profiles, profilesummary, recorderinstall]
    
    f.tableToFeather(tablenames, tabledata)
    f.anonAns() #anonymise and save answer tables
    
def saveRawProfiles(yearstart, yearend):
    """
    This function iterates through all profiles and saves them in a ordered directory structure by year and unit.
    """
    
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
