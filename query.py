# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 16:35:39 2017

@author: CKAN
"""

import pandas as pd
from answers import *

wall_material_dist = answerSearch('wall')[0].groupby(answerSearch('wall')[0].iloc[:,-1]).size()

roof_material_dist = answerSearch('roof',3)[0].groupby(answerSearch('roof',3)[0].iloc[:,-1]).size()