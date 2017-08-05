#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 09:34:08 2017

@author: Wiebke Toussaint

Answer query script: This script contains functions to query and manipulate DLR survey answer sets. It references datasets that must be stored in a /data/tables subdirectory in the parent directory.

"""

import numpy as np
import feather
from glob import glob
import os
from pathlib import Path

src_dir = Path(__file__).parents[0]
dlrdb_dir = Path(__file__).parents[1]
data_dir = os.path.join(dlrdb_dir, 'data', 'tables')

def getFeathers(filepath = data_dir):
    """
    This function loads all feather tables in filepath into workspace.
    
    """
    files = glob(os.path.join(data_dir, '*.feather'))
    names = [f.rpartition('.')[0] for f in os.listdir(data_dir)]
    tables = {}
    for n, f in zip(names, files):
        try:
            tables[n] = feather.read_dataframe(f)
        except:
            pass
    return tables

#preparing question tables
def getQuestions(dtype = None):
    """
    This function gets all questions.
    
    """
    qu = getFeathers().get('questions').drop(labels='lock', axis=1)
    qu.Datatype = qu.Datatype.astype('category')
    qu.Datatype.cat.categories = ['blob','char','num']
    if dtype is None:
        pass
    else: 
        qu = qu[qu.Datatype == dtype]
    return qu

def quSearch(searchterm = '', qnairid = None, dtype = None):
    """
    Searches questions for a search term, taking questionaire ID and question data type (num, blob, char) as input. 
    A single search term can be specified as a string, or a list of search terms as list.
    
    """
    if isinstance(searchterm, list):
        pass
    else:
        searchterm = [searchterm]
    searchterm = [s.lower() for s in searchterm]
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
    result = qdf.loc[qdf.Question.str.lower().str.contains('|'.join(searchterm)), ['Question', 'Datatype','QuestionaireID', 'ColumnNo', 'Lower', 'Upper']]
    return result

def qnairQ(qnid = 3):
    """
    Creates a dict with items containing questions by type (num, blob, char).
    
    """
    d = {i : quSearch(qnairid = qnid, dtype=i) for i in ['num','blob','char']}
    return d

#preparing answer tables    
def getAnswers(dtype = None):
    """
    This function returns all answer IDs and their response sets for a selected data type. 
    If dtype is None, answer IDs and their corresponding questionaire IDs are returned instead.
    
    """
    if dtype is None:
        ans = getFeathers().get('answers').drop(labels='lock', axis=1)
    elif dtype == 'blob':
        ans = getFeathers().get('answers_blob_anon')
        ans.fillna(np.nan, inplace = True)
    elif dtype == 'char':
        ans = getFeathers().get('answers_char_anon').drop(labels='lock', axis=1)
    elif dtype == 'num':
        ans = getFeathers().get('answers_num').drop(labels='lock', axis=1)
    return ans


def answerSearch(searchterm = '', qnairid = 3, dtype = 'num'):
    """
    This function returns
    
    """
    allans = getAnswers() #get answer IDs for questionaire IDs
    ans = getAnswers(dtype) #retrieve all responses for data type
    questions = quSearch(searchterm, qnairid, dtype) #get column numbers for query
    result = ans[ans.AnswerID.isin(allans[allans.QuestionaireID == qnairid]['AnswerID'])] #subset responses by answer IDs
    result = result.iloc[:, [0] +  list(questions['ColumnNo'])]
    return [result, questions[['ColumnNo','Question']]]

def getLocations(year = '2014'):
    "This function returns all survey locations for a given year."
    groups = getFeathers().get('groups')
    locs = set(l.partition(' ')[2] for l in groups[groups.Year==year]['Location'])
    locations = sorted(list(locs))
    return locations 

def getLang(code = None):
    """
    This function returns the language categories
    
    """
    language = dict(zip(answerSearch(qnairid=5)[0].iloc[:,1], answerSearch(qnairid=5,dtype='char')[0].iloc[:,1]))
    if code is None:
        pass
    else:
        language = language[code]
    return language

def getAltE(code = None):
    """
    This function returns the alternative fuel categories.
    
    """
    altenergy = dict(zip(answerSearch(qnairid=8)[0].iloc[:,1], answerSearch(qnairid=8,dtype='char')[0].iloc[:,1]))
    if code is None:
        pass
    else:
        altenergy = altenergy[code]
    return altenergy

#QnID = ans[ans['AnswerID'] == 34]['QuestionaireID']