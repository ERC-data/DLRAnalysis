#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 09:34:08 2017

@author: Wiebke Toussaint

Answer query script: This script contains functions to query and manipulate DLR survey answer sets. It references datasets that must be stored in a /data/tables subdirectory in the parent directory.

"""

import numpy as np
import pandas as pd
import feather
from glob import glob
import os
from pathlib import Path

src_dir = str(Path(__file__).parents[0])
dlrdb_dir = str(Path(__file__).parents[1])
data_dir = os.path.join(dlrdb_dir, 'data', 'tables')

def loadFeathers(filepath = data_dir):
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

def loadID(year = None, id_name = 'AnswerID'):
    """
    Subsets Answer or Profile IDs by year. Year input can be number or string. id_name is AnswerID or ProfileID.
    """
    groups = loadFeathers().get('groups')
    links = loadFeathers().get('links')
    all_ids = links[(links.GroupID != 0) & (links[id_name] != 0)]
    if year is None:
        ids = pd.Series(all_ids.loc[:, id_name].unique())
    else:      
        if isinstance(year, str):
            pass
        else:
            year = str(year)
        id_select = groups[groups.Year==year]['GroupID']
        ids = pd.Series(all_ids.loc[all_ids.GroupID.isin(id_select), id_name].unique())
    return ids

#preparing question tables
def loadQuestions(dtype = None):
    """
    This function gets all questions.
    
    """
    qu = loadFeathers().get('questions').drop(labels='lock', axis=1)
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
    qcons = loadFeathers().get('qconstraints').drop(labels='lock', axis=1)
    qu = loadQuestions(dtype)
    qdf = qu.join(qcons, 'QuestionID', rsuffix='_c') #join question constraints to questions table
    qnairids = list(loadFeathers().get('questionaires')['QuestionaireID']) #get list of valid questionaire IDs
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
def loadAnswers(dtype = None):
    """
    This function returns all answer IDs and their question responses for a selected data type. 
    If dtype is None, answer IDs and their corresponding questionaire IDs are returned instead.
    
    """
    if dtype is None:
        ans = loadFeathers().get('answers').drop(labels='lock', axis=1)
    elif dtype == 'blob':
        ans = loadFeathers().get('answers_blob_anon')
        ans.fillna(np.nan, inplace = True)
    elif dtype == 'char':
        ans = loadFeathers().get('answers_char_anon').drop(labels='lock', axis=1)
    elif dtype == 'num':
        ans = loadFeathers().get('answers_num').drop(labels='lock', axis=1)
    return ans


def answerSearch(searchterm = '', qnairid = 3, dtype = 'num'):
    """
    This function returns
    
    """
    allans = loadAnswers() #get answer IDs for questionaire IDs
    ans = loadAnswers(dtype) #retrieve all responses for data type
    questions = quSearch(searchterm, qnairid, dtype) #get column numbers for query
    result = ans[ans.AnswerID.isin(allans[allans.QuestionaireID == qnairid]['AnswerID'])] #subset responses by answer IDs
    result = result.iloc[:, [0] +  list(questions['ColumnNo'])]
    return [result, questions[['ColumnNo','Question']]]

def loadLocations(year = '2014'):
    "This function returns all survey locations for a given year."
    groups = loadFeathers().get('groups')
    locs = set(l.partition(' ')[2] for l in groups[groups.Year==year]['Location'])
    locations = sorted(list(locs))
    return locations 

def loadLang(code = None):
    """
    This function returns the language categories
    
    """
    language = dict(zip(answerSearch(qnairid=5)[0].iloc[:,1], answerSearch(qnairid=5,dtype='char')[0].iloc[:,1]))
    if code is None:
        pass
    else:
        language = language[code]
    return language

def loadAltE(code = None):
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