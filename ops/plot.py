# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 09:56:20 2017

@author: CKAN
"""

import plotly.plotly as py
import plotly.graph_objs as go
import plotly.offline as po

data = [go.Scatter(x=A99.Unitsread[A99.ProfileID == 4838], y=A99.Datefield[A99.ProfileID == 4838])]