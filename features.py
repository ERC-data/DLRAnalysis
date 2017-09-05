# -*- coding: utf-8 -*-
"""
Created on Sun Jul 23 13:59:37 2017

@author: CKAN
"""

import pandas as pd
from answers import answerSearch, getID
import feather


features = ['earn', 'water', 'roof', 'wall', 'electricity']

def featureFrame(features, year):
    "This function creates a dataframe containing the data for a set of selected features for a given year."
    data = pd.DataFrame(data = getID(year), columns=['AnswerID']) #get AnswerIDs for year
    featureqs = pd.DataFrame() #construct dataframe with feature questions
    
    for f in features:
        ans = answerSearch(f)
        d = ans[0]
        q = ans[1]
        q['feature'] = f
        newdata = d[d.AnswerID.isin(data)]
        data = pd.merge(data, newdata, on = 'AnswerID')
        featureqs = pd.concat([featureqs, q])
    featureqs.reset_index(drop=True, inplace=True)
        
    return [data, featureqs]


#mydata = featureFrame(features, 2011)[0]
#mydata = mydata.drop(['AnswerID','95'], axis=1)
#cols = ['Hi','Wa','Rm','Wm','Te']
#mydata.columns = cols

#playing with profiles
kW = feather.read_dataframe('E:\\git\\DLR_DB\\profiles\\2009\\2009-8\\2009-8_kW.feather')
kWh = kW.groupby(['UoM','RecorderID','ProfileID']).resample('1H', on='Datefield').sum()
kWd = kW.groupby(['UoM','RecorderID','ProfileID']).resample('1D', on='Datefield').sum()
kWm = kW.groupby(['UoM','RecorderID','ProfileID']).resample('1M', on='Datefield').sum()

recorder_ids = kW.RecorderID.cat.categories.tolist()

#investigating one location
def locationSummary(locstring):
    loc = kW[kW.RecorderID.str.contains(locstring.upper())]
    kwm = loc.groupby(['UoM','RecorderID','ProfileID']).resample('1M', on='Datefield').sum()
    kwm.describe()
    return loc, kwm