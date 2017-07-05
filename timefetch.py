# -*- coding: utf-8 -*-
"""
Created on Sat Jul  1 14:11:25 2017

@author: CKAN
"""

from timeit import Timer
import numpy as np

## TIMING
def timef(function, params):
    "This function times data fetch operations. Be careful when using it, as it repeats the fetch process 3 times and each fetch obviously takes time to complete."
    "shorthand is to use %timeit in ipython interpreter"
    timequery = function + "(" + params + ")"
    setup = "from __main__ import " + function
    timefetch = Timer(timequery, setup = setup).repeat(repeat = 3, number = 1)
    meanfetch = np.mean(np.array(timefetch))
    stdfetch = np.std(np.array(timefetch))
    return meanfetch, stdfetch

## MEMORY
# To be run in ipython console
#%load_ext memory_profiler
#%load_ext memory_profiler