# -*- coding: utf-8 -*-
"""
@author: Wiebke Toussaint

Support functions for the src module
"""

import os
from pathlib import Path

# root dir
dlrdb_dir = str(Path(__file__).parents[1])

# level 1
src_dir = str(Path(__file__).parents[0])
libpgm_dir = os.path.join(dlrdb_dir, 'libpgm')
data_dir = os.path.join(dlrdb_dir, 'data')

# level 2 & 3 DATA
rawprofiles_dir = os.path.join(data_dir, 'profiles', 'raw')
hourlyprofiles_dir = os.path.join(data_dir, 'profiles', 'hourly')
table_dir = os.path.join(data_dir, 'tables')

# level 2 & 3 INFERENCE
evidence_dir = os.path.join(libpgm_dir, 'evidence')
classes_dir = os.path.join(libpgm_dir, 'out')