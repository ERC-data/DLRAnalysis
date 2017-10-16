# -*- coding: utf-8 -*-
"""
@author: Wiebke Toussaint

Support functions for the src module
"""

import os
from pathlib import Path

src_dir = str(Path(__file__).parents[0])
dlrdb_dir = str(Path(__file__).parents[1])
libpgm_dir = os.path.join(dlrdb_dir, 'libpgm')
rawprofiles_dir = os.path.join(dlrdb_dir, 'profiles', 'raw')
hourlyprofiles_dir = os.path.join(dlrdb_dir, 'profiles', 'hourly')
table_dir = os.path.join(dlrdb_dir, 'data', 'tables')
evidence_dir = os.path.join(dlrdb_dir, 'libpgm', 'evidence')
classes_dir = os.path.join(dlrdb_dir, 'libpgm', 'out')