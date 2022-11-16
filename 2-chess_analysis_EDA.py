# -*- coding: utf-8 -*-
"""EDA V1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1021yQihVpPlewGV1_9Fo1x0ooCLIhnk0
"""

!pip uninstall pandas-profilingy

! pip install https://github.com/pandas-profiling/pandas-profiling/archive/master.zip

import pandas as pd
import pandas_profiling
from pandas_profiling import ProfileReport
from pandas_profiling.utils.cache import cache_file

# load the dataset
fidedf = pd.read_csv('/content/fidedfv4.csv')

#define player to analyse
dataset = fidedf[fidedf['Name']=='carlsen']

dataset.head()

profile = ProfileReport(fidedf, title='Fide DF', html={'style':{'full_width':True}})

profile.to_notebook_iframe()

profile.to_file(output_file="FIDE_DATASET.html")

from google.colab import drive
drive.mount('drive')

!cp FIDE_DATASET.html "drive/My Drive/"