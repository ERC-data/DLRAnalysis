# -*- coding: utf-8 -*-
"""
Created on Sun Jul 23 13:59:37 2017

@author: CKAN
"""

import pandas as pd
from socios import featureFrame, checkAnswer, loadID, loadTables
import feather

#Construct socio-demographic features
features = ['earn', 'water', 'roof', 'wall', 'electricity']

testfeature = featureFrame(features, 2012)

testanswercheck = checkAnswer(915, 'iron')

# NEED TO ASSOCIATE ANSWERID WITH PROFILEID

#mydata = featureFrame(features, 2011)[0]
#mydata = mydata.drop(['AnswerID','95'], axis=1)
#cols = ['Hi','Wa','Rm','Wm','Te']
#mydata.columns = cols

#playing with profiles
kW = feather.read_dataframe('E:\\git\\DLR_DB\\profiles\\raw\\2009\\2009-8\\2009-8_kW.feather')
kWh = kW.groupby(['UoM','RecorderID','ProfileID']).resample('1H', on='Datefield').sum()
kWd = kW.groupby(['UoM','RecorderID','ProfileID']).resample('1D', on='Datefield').sum()
kWm = kW.groupby(['UoM','RecorderID','ProfileID']).resample('1M', on='Datefield').sum()

recorder_ids = kW.RecorderID.cat.categories.tolist()

