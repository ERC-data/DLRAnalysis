# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 16:03:22 2017

@author: CKAN
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import feather
import support

tables = []


groups = support.getGroups() 
answers_num = support.getData('Answers_Number')
links = support.getData('LinkTable')


support.anonAns()


pids = support.getProfileID()

