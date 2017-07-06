#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 09:34:08 2017

@author: saintlyvi
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import feather
from sqldlr import getProfiles
import glob

def saveAllProfiles(mypath, yearstart, yearend):
    "This function fetches all profile data and saves it to path as a .feather file. It will take several hours to run!"
    for i in range(yearstart, yearend + 1):
        print(i)
        df = getProfiles(i)
        path = mypath + 'p' + str(i) + '.feather'
        print(path)
        feather.write_dataframe(df, path)

def getFeathers(filepath = 'E:\\Domestic Load Research DB\\DBTables\\'):
    "This function loads all feather tables in filepath into workspace."
    files = glob.glob(filepath + '*.feather')
    names = [f.rpartition('\\')[2].rpartition('.')[0] for f in files]
    tables = {}
    for n, f in zip(names, files):
        tables[n] = feather.read_dataframe(f)
    return tables

#preparing answer tables    
def getAnswers(dtype = None):
    "This function returns all answer IDs and their response sets for a selected data type. If dtype is None, answer IDs and their corresponding questionaire IDs are returned instead."
    if dtype is None:
        ans = getFeathers().get('answers').drop(labels='lock', axis=1)
    elif dtype == 'blob':
        ans = getFeathers().get('answersblob')
        ans.fillna(np.nan, inplace = True)
    elif dtype == 'char':
        ans = getFeathers().get('answerschar').drop(labels='lock', axis=1)
    elif dtype == 'num':
        ans = getFeathers().get('answersnum').drop(labels='lock', axis=1)
    return ans

#preparing question tables
def getQuestions(dtype = None):
    "This function gets all questions"
    qu = getFeathers().get('questions').drop(labels='lock', axis=1)
    qu.Datatype = qu.Datatype.astype('category')
    qu.Datatype.cat.categories = ['blob','char','num']
    if dtype is None:
        pass
    else: 
        qu = qu[qu.Datatype == dtype]
    return qu

def quSearch(searchterm = '', qnairid = None, dtype = None):
    qcons = getFeathers().get('qconstraints').drop(labels='lock', axis=1)
    qu = getQuestions(dtype)
    
    qdf = qu.join(qcons, 'QuestionID', rsuffix='_c') #join question constraints to questions table
    qnairids = list(getFeathers().get('questionaires')['QuestionaireID']) #get list of valid questionaire IDs
    if qnairid is None: #gets all relevant queries
        pass
    elif qnairid in qnairids: #check that ID is valid if provided
        qdf = qdf[qdf.QuestionaireID == qnairid] #subset dataframe to relevant ID
    else:
        return print('Please select a valid QuestionaireID', qnairids)
    result = qdf.loc[qdf.Question.str.lower().str.contains(searchterm)==True, ['Question', 'Datatype','QuestionaireID', 'ColumnNo', 'Lower', 'Upper']]
    return result

#split answers by questionaire
def qnairQ(qnid = 3):
    d = {i : quSearch(qnairid = qnid, dtype=i) for i in ['num','blob','char']}
    return d

def answerSearch(searchterm = '', qnairid = 3, dtype = 'num'):
    allans = getAnswers() #get answer IDs for questionaire IDs
    ans = getAnswers(dtype) #retrieve all responses for data type
    questions = quSearch(searchterm, qnairid, dtype) #get column numbers for query
    result = ans[ans.AnswerID.isin(allans[allans.QuestionaireID == qnairid]['AnswerID'])] #subset responses by answer IDs
    result = result.iloc[:, list(questions['ColumnNo'])]
    print(questions.Question)
    return result 


#QnID = ans[ans['AnswerID'] == 34]['QuestionaireID']