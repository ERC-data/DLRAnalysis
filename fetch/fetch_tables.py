# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 16:03:22 2017

@author: CKAN
"""

import fetch_support as f

def tables():
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
    
def profiles(yearstart, yearend):
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