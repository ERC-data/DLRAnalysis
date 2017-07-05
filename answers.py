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
from os import listdir

def getFeathers(filepath = '/home/saintlyvi/Documents/ckan/DLR/DBTables'):
    "This function"
    files = listdir(filepath)
    names = [f.split('.', 1)[0] for f in files]
    
    tables = {}
    for n, f in zip(names, files):
        tables[n] = feather.read_dataframe(filepath + '/' + f)
    return tables

#preparing answer tables    
ablob = getFeathers().get('answersblob')
ablob.fillna(np.nan, inplace = True)
achar = getFeathers().get('answerschar').drop(labels='lock', axis=1)
anum = getFeathers().get('answersnum').drop(labels='lock', axis=1)
ans = getFeathers().get('answers').drop(labels='lock', axis=1)

#preparing question tables
qu = getFeathers().get('questions').drop(labels='lock', axis=1)
qu.Datatype = qu.Datatype.astype('category')
qu.Datatype.cat.categories = ['blob','char','num']
qnair = getFeathers().get('questionaires').drop(labels='lock', axis=1)

qublob = qu[qu.Datatype == 'blob']
quchar = qu[qu.Datatype == 'char']
qunum = qu[qu.Datatype == 'num']

def quSearch(searchterm, questionsdf = qu):
    result = questionsdf.loc[questionsdf.Question.str.lower().str.find(searchterm)==0, ['Question', 'Datatype','ColumnNo']]
    return result

#split answers by questionaire
def qnairQuest(QuestionaireID):
    "This function returns a datadict with all ColumnNo:Question pairs for a particular questionaire"
    qnairids = list(getFeathers().get('questionaires')['QuestionaireID'])
    if QuestionaireID in qnairids:
        pass
    else:
        return print('Please select a valid QuestionaireID', qnairids)
    QnQs = qu[qu['QuestionaireID'] == QuestionaireID]
    Qblob = dict(zip(QnQs[QnQs.Datatype == 'blob']['ColumnNo'], QnQs[QnQs.Datatype == 'blob']['Question']))
    Qchar = dict(zip(QnQs[QnQs.Datatype == 'char']['ColumnNo'], QnQs[QnQs.Datatype == 'char']['Question']))
    Qnum = dict(zip(QnQs[QnQs.Datatype == 'num']['ColumnNo'], QnQs[QnQs.Datatype == 'num']['Question']))
    
    return {'QnID':QnID, 'Qblob':Qblob, 'Qchar':Qchar, 'Qnum':Qnum}




QnID = ans[ans['AnswerID'] == 34]['QuestionaireID']