# -*- coding: utf-8 -*-
"""
Created on Sat Jul  1 14:11:25 2017

@author: CKAN
"""

from timeit import Timer
import numpy as np
from dlrdb import getProfileID

## TIMING
def timef(function, params):
    "This function times data fetch operations. Be careful when using it, as it repeats the fetch process 3 times and each fetch obviously takes time to complete."
    timequery = function + "(" + params + ")"
    setup = "from __main__ import " + function
    timefetch = Timer(timequery, setup = setup).repeat(repeat = 3, number = 1)
    meanfetch = np.mean(np.array(timefetch))
    stdfetch = np.std(np.array(timefetch))
    
    return meanfetch, stdfetch

def profileFetchEst(year):
    
    plist = list(map(str, getProfileID(year)))
    
    profilefetch = len(plist)/60
    unitfetch = profilefetch/3
    print('It will take %f minutes to fetch all profiles from %d' % (profilefetch, year))
    print('It will take %f minutes to fetch profiles for one unit of measure' % (unitfetch))