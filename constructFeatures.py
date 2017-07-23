# -*- coding: utf-8 -*-
"""
Created on Sun Jul 23 13:59:37 2017

@author: CKAN
"""

import pandas as pd
from answers import answerSearch
from sqldlr import getAnswerID


features = ['earn', 'water', 'roof', 'wall']

def featureFrame(features, year):
    "This function creates a dataframe containing the data for a set of selected features for a given year."
    data = pd.DataFrame(data = getAnswerID(year), columns=['AnswerID']) #get AnswerIDs for year
    featureqs = pd.DataFrame() #construct dataframe with feature questions
    
    for f in features:
        ans = answerSearch(f)
        d = ans[0]
        q = ans[1]
        q['feature'] = f
        newdata = d[d.AnswerID.isin(getAnswerID(year))]
        data = pd.merge(data, newdata, on = 'AnswerID')
        featureqs = pd.concat([featureqs, q])
    featureqs.reset_index(drop=True, inplace=True)
        
    return [data, featureqs]