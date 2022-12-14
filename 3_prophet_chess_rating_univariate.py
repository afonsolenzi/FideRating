# -*- coding: utf-8 -*-
"""3-Prophet - Chess Rating Univariate.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1o41aZqLCmaKexB1NUjUr3JAFdC9dgRSB
"""

pip install ml_metrics

import numpy as np
import matplotlib.pyplot as plt
from pandas import read_csv
import math
import pandas as pd

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM, Flatten
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
#from keras.callbacks import EarlyStopping
from keras.layers import ConvLSTM2D
from prophet import Prophet
import seaborn as sns
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import ml_metrics as metrics

# load the dataset
dataframe = read_csv('/content/fiderating.csv')

dataframe.dtypes

fig, ax = plt.subplots(figsize=(6, 6))
sns.scatterplot(data=dataframe,x="GMS",y="Rating",color="k",ax=ax,)

sns.kdeplot(data=dataframe,x="GMS",y="Rating",levels=5,fill=True,alpha=0.6,cut=2,ax=ax,)

fig, ax = plt.subplots(figsize=(6, 6))
sns.scatterplot(data=dataframe,x="ratio",y="Rating",color="k",ax=ax,)

sns.kdeplot(data=dataframe,x="ratio",y="Rating",levels=5,fill=True,alpha=0.6,cut=2,ax=ax,)

l = ['niemann','keymer','sjugirov','deac','sargissian','xiong','abdusattorov','foreest','alekseenko','cheparinov',
     'dubov','parham','pons','vidit','erigaisi','bu','shankland','gukesh','liem','andreikin']


allresults = pd.DataFrame() #novo dataframe para agrupar todos os jogadores
MAE=[]
RMSE=[]
for name in l:
    
    dataset=dataframe[dataframe['Name']==name]
    df = dataset
    df['Period'] = pd.DatetimeIndex(df['Period'])
    df_new = df[['Period', 'Rating']]
    df_new.columns = ['ds', 'y']
    my_model = Prophet(interval_width=0.95)
    my_model.fit(df_new)
    future_dates = my_model.make_future_dataframe(periods=6, freq='MS')
    forecast = my_model.predict(future_dates)
    forecast['Name']=name
    forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].head()
    my_model.plot(forecast, uncertainty=True)
    metric_df = forecast.set_index('ds')[['yhat']].join(df_new.set_index('ds').y).reset_index()
    metric_df.dropna(inplace=True)  
    mae = mean_absolute_error(metric_df.y, metric_df.yhat)
    MAE.append(mae)
    rmse=metrics.rmse(metric_df.y, metric_df.yhat)
    RMSE.append(rmse)
    print(f'{name}= RMSE({rmse}),MAE({mae})')
    #dataframe com todas previsoes
    allresults = allresults.append(forecast)

allresults

allresults=allresults[['Name','yhat']]
max_ratings = allresults.groupby('Name').agg({ 'yhat':'max'})[['yhat']].reset_index()
max_ratings.sort_values('yhat', ascending=False)

prophet_results = pd.DataFrame(
    {'name': l,
     
     'MAE': MAE,
     'RMSE':RMSE
    })
prophet_results = prophet_results.sort_values(by='RMSE')
prophet_results

l=['carlsen']

allresults = pd.DataFrame() #novo dataframe para agrupar todos os jogadores
MAE=[]
RMSE=[]
for name in l:
    
    dataset=dataframe[dataframe['Name']==name]
    df = dataset
    df['Period'] = pd.DatetimeIndex(df['Period'])
    df_new = df[['Period', 'Rating']]
    df_new.columns = ['ds', 'y']
    my_model = Prophet(interval_width=0.95)
    my_model.fit(df_new)
    future_dates = my_model.make_future_dataframe(periods=24, freq='MS')
    forecast = my_model.predict(future_dates)
    forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].head()
    my_model.plot(forecast, uncertainty=True)
    metric_df = forecast.set_index('ds')[['yhat']].join(df_new.set_index('ds').y).reset_index()
    metric_df.dropna(inplace=True)
    mae = mean_absolute_error(metric_df.y, metric_df.yhat)
    MAE.append(mae)
    rmse=metrics.rmse(metric_df.y, metric_df.yhat)
    RMSE.append(rmse)
    print(f'{name}= RMSE({rmse}),MAE({mae})')
      #dataframe com todas previsoes
      allresults = allresults.append(forecast)

forecast.tail(12)

prophet_results = pd.DataFrame(
    {'name': l,
     
     'MAE': MAE,
     'RMSE':RMSE
    })
prophet_results = prophet_results.sort_values(by='RMSE')
prophet_results

forecast.tail(24)

forecast.loc[forecast['yhat'].idxmax()]

import matplotlib.pyplot as plt
fig,ax = plt.subplots()

ax.plot(forecast['ds'],forecast['yhat_upper'],label=name,color='green')
ax.plot(forecast['ds'],forecast['yhat'],label=name,color='red')
ax.plot(forecast['ds'],forecast['yhat_lower'],label=name,color='gray')

ax.set_xlabel("ds")
ax.set_ylabel("yhat")
