# -*- coding: utf-8 -*-
"""4-Keras - Chess Rating Univariate.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Q-gnV6UkLuK2ETj46YJYu3pfOAdiINCW

https://machinelearningmastery.com/tutorial-first-neural-network-python-keras/

https://stackoverflow.com/questions/69906416/forecast-future-values-with-lstm-in-python
"""

pip install ml_metrics

import numpy as np
import matplotlib.pyplot as plt
from pandas import read_csv
import math
import pandas as pd
import tensorflow as tf

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM, Flatten
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
#from keras.callbacks import EarlyStopping
from keras.layers import ConvLSTM2D
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import ml_metrics as metrics

from datetime import datetime, timedelta
from datetime import date
from dateutil.relativedelta import relativedelta
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.models import Sequential
pd.options.mode.chained_assignment = None
tf.random.set_seed(0)

# load the dataset
df = pd.read_csv('/content/fiderating.csv')

dataframe=df[df['Name']=='carlsen']
dataframe.count()

l = ['niemann','keymer','sjugirov','deac','sargissian','xiong','abdusattorov','foreest','alekseenko','cheparinov','dubov','parham','pons','vidit','erigaisi','bu','shankland','gukesh','liem','andreikin']

allresults = pd.DataFrame() #novo dataframe para agrupar todos os jogadores
MAE=[]
RMSE=[]
for name in l:
  dataframe=df[df['Name']==name]
  dataframe = dataframe[[ 'Rating']]
  dataset = dataframe[[ 'Rating']]
  #dataset['Period'] =  pd.to_datetime(dataset['Period'], format='%Y-%m-%d')


  #Convert pandas dataframe to numpy array
  dataset = dataframe.values
  dataset = dataset.astype('float32') #COnvert values to float

  #dataset = dataset.astype({'RTNG':'float'})


  #LSTM uses sigmoid and tanh that are sensitive to magnitude so values need to be normalized
  # normalize the dataset
  scaler = MinMaxScaler(feature_range=(0, 1)) #Also try QuantileTransformer
  dataset = scaler.fit_transform(dataset)


  #We cannot use random way of splitting dataset into train and test as
  #the sequence of events is important for time series.
  #So let us take first 60% values for train and the remaining 1/3 for testing
  # split into train and test sets
  train_size = int(len(dataset) * 0.66)
  test_size = len(dataset) - train_size
  train, test = dataset[0:train_size,:], dataset[train_size:len(dataset),:]

  # We cannot fit the model like we normally do for image processing where we have
  #X and Y. We need to transform our data into something that looks like X and Y values.
  # This way it can be trained on a sequence rather than indvidual datapoints. 
  # Let us convert into n number of columns for X where we feed sequence of numbers
  #then the final column as Y where we provide the next number in the sequence as output.
  # So let us convert an array of values into a dataset matrix

  # seq_size is the number of previous time steps to use as 
  # input variables to predict the next time period.

  #creates a dataset where X is the number of passengers at a given time (t, t-1, t-2...) 
  #and Y is the number of passengers at the next time (t + 1).

  def to_sequences(dataset, seq_size=1):
    x = []
    y = []

    for i in range(len(dataset)-seq_size-1):
        #print(i)
        window = dataset[i:(i+seq_size), 0]
        x.append(window)
        y.append(dataset[i+seq_size, 0])
        
    return np.array(x),np.array(y)

  seq_size = 10  # Number of time steps to look back 
  #Larger sequences (look further back) may improve forecasting.

  trainX, trainY = to_sequences(train, seq_size)
  testX, testY = to_sequences(test, seq_size)

  print("Shape of training set: {}".format(trainX.shape))
  print("Shape of test set: {}".format(testX.shape))

  #########################################################
  #ConvLSTM
  #The layer expects input as a sequence of two-dimensional images, 
  #therefore the shape of input data must be: [samples, timesteps, rows, columns, features]

  trainX = trainX.reshape((trainX.shape[0], 1, 1, 1, seq_size))
  testX = testX.reshape((testX.shape[0], 1, 1, 1, seq_size))

  model = Sequential()
  model.add(ConvLSTM2D(filters=64, kernel_size=(1,1), activation='relu', input_shape=(1, 1, 1, seq_size)))
  model.add(Flatten())
  model.add(Dense(32))
  model.add(Dense(1))
  model.compile(optimizer='adam', loss='mean_squared_error')
  model.summary()
  #print('Train...')



  ###############################################
  model.fit(trainX, trainY, validation_data=(testX, testY),verbose=2, epochs=100)


  # make predictions

  trainPredict = model.predict(trainX)
  testPredict = model.predict(testX)

  # invert predictions back to prescaled values
  #This is to compare with original input values
  #SInce we used minmaxscaler we can now use scaler.inverse_transform
  #to invert the transformation.
  trainPredict = scaler.inverse_transform(trainPredict)
  trainY = scaler.inverse_transform([trainY])
  testPredict = scaler.inverse_transform(testPredict)
  testY = scaler.inverse_transform([testY])

  # calculate root mean squared error
  trainScore = math.sqrt(mean_squared_error(trainY[0], trainPredict[:,0]))
  #print('Train Score: %.2f RMSE' % (trainScore))

  testScore = math.sqrt(mean_squared_error(testY[0], testPredict[:,0]))
  #print('Test Score: %.2f RMSE' % (testScore))
  RMSE.append(testScore)

  lista = trainY.tolist()[0]
  size = len(lista)
  metric_df = dataframe.tail(size)
  metric_df['yhat'] = lista
  metric_df.dropna(inplace=True)
  mae = mean_absolute_error(metric_df.Rating, metric_df.yhat)
  MAE.append(mae)

  #gerar futuras previsões
  #  data
  y = dataframe['Rating'].fillna(method='ffill')
  y = y.values.reshape(-1, 1)

  # scale the data
  scaler = MinMaxScaler(feature_range=(0, 1))
  scaler = scaler.fit(y)
  y = scaler.transform(y)

  # generate the input and output sequences
  n_lookback = 6  # length of input sequences (lookback period)
  n_forecast = 12  # length of output sequences (forecast period)

  X = []
  Y = []

  for i in range(n_lookback, len(y) - n_forecast + 1):
    X.append(y[i - n_lookback: i])
    Y.append(y[i: i + n_forecast])

  X = np.array(X)
  Y = np.array(Y)

  # fit the model
  model = Sequential()
  model.add(LSTM(units=50, return_sequences=True, input_shape=(n_lookback, 1)))
  model.add(LSTM(units=50))
  model.add(Dense(n_forecast))

  model.compile(loss='mean_squared_error', optimizer='adam')
  model.fit(X, Y, epochs=100, batch_size=32, verbose=0)

  # generate the forecasts
  X_ = y[- n_lookback:]  # last available input sequence
  X_ = X_.reshape(1, n_lookback, 1)

  Y_ = model.predict(X_).reshape(-1, 1)
  Y_ = scaler.inverse_transform(Y_)

  #criando datas para a quantidade de predições
  data =[]
  dataframe=df[df['Name']==name]
  date = dataframe.iloc[-1,2]
  format = '%Y-%m-%d'
  dt = datetime.strptime(date, format)
  for i in range(n_forecast+1):
    next_month = dt.replace(day=1) + relativedelta(months=i+1)
    data.append(next_month.strftime('%Y-%m-%d'))    

  #usando o flatten para transformar de numpy array para uma lista
  list_y = list(Y_.flatten())

  #criando um dataframe com as novas datas e as predições
  df_pred = pd.DataFrame(list(zip(data, list_y)),
               columns =['Period', 'Rating_Previsto'])
  df_pred['Name'] = name

  #concatenando com os dados originais
  df_original = dataframe[['Period','Rating','Name']]
  results = df_original.append(df_pred).set_index('Period')
  
  #dataframe com todas previsoes
  allresults = allresults.append(df_pred)

  # grafico dos dados históricos + predições
  results.plot(title='Fide Rating',figsize=(20,10))

allresults

max_ratings = allresults.groupby('Name').agg({ 'Rating_Previsto':'max'})[['Rating_Previsto']].reset_index()
max_ratings.sort_values('Rating_Previsto', ascending=False)

keras_univariate_results = pd.DataFrame(
    {'name': l,
     'MAE': MAE,
     'RMSE':RMSE
    })
keras_univariate_results = keras_univariate_results.sort_values(by='MAE')
keras_univariate_results

l=['carlsen']
MAE=[]
RMSE=[]
for name in l:
  dataframe=df[df['Name']==name]
  dataframe = dataframe[[ 'Rating']]
  dataset = dataframe[[ 'Rating']]
  #dataset['Period'] =  pd.to_datetime(dataset['Period'], format='%Y-%m-%d')


  #Convert pandas dataframe to numpy array
  dataset = dataframe.values
  dataset = dataset.astype('float32') #COnvert values to float

  #dataset = dataset.astype({'RTNG':'float'})


  #LSTM uses sigmoid and tanh that are sensitive to magnitude so values need to be normalized
  # normalize the dataset
  scaler = MinMaxScaler(feature_range=(0, 1)) #Also try QuantileTransformer
  dataset = scaler.fit_transform(dataset)


  #We cannot use random way of splitting dataset into train and test as
  #the sequence of events is important for time series.
  #So let us take first 60% values for train and the remaining 1/3 for testing
  # split into train and test sets
  train_size = int(len(dataset) * 0.66)
  test_size = len(dataset) - train_size
  train, test = dataset[0:train_size,:], dataset[train_size:len(dataset),:]

  # We cannot fit the model like we normally do for image processing where we have
  #X and Y. We need to transform our data into something that looks like X and Y values.
  # This way it can be trained on a sequence rather than indvidual datapoints. 
  # Let us convert into n number of columns for X where we feed sequence of numbers
  #then the final column as Y where we provide the next number in the sequence as output.
  # So let us convert an array of values into a dataset matrix

  # seq_size is the number of previous time steps to use as 
  # input variables to predict the next time period.

  #creates a dataset where X is the number of passengers at a given time (t, t-1, t-2...) 
  #and Y is the number of passengers at the next time (t + 1).

  def to_sequences(dataset, seq_size=1):
    x = []
    y = []

    for i in range(len(dataset)-seq_size-1):
        #print(i)
        window = dataset[i:(i+seq_size), 0]
        x.append(window)
        y.append(dataset[i+seq_size, 0])
        
    return np.array(x),np.array(y)

  seq_size = 10  # Number of time steps to look back 
  #Larger sequences (look further back) may improve forecasting.

  trainX, trainY = to_sequences(train, seq_size)
  testX, testY = to_sequences(test, seq_size)

  print("Shape of training set: {}".format(trainX.shape))
  print("Shape of test set: {}".format(testX.shape))

  #########################################################
  #ConvLSTM
  #The layer expects input as a sequence of two-dimensional images, 
  #therefore the shape of input data must be: [samples, timesteps, rows, columns, features]

  trainX = trainX.reshape((trainX.shape[0], 1, 1, 1, seq_size))
  testX = testX.reshape((testX.shape[0], 1, 1, 1, seq_size))

  model = Sequential()
  model.add(ConvLSTM2D(filters=64, kernel_size=(1,1), activation='relu', input_shape=(1, 1, 1, seq_size)))
  model.add(Flatten())
  model.add(Dense(32))
  model.add(Dense(1))
  model.compile(optimizer='adam', loss='mean_squared_error')
  model.summary()
  #print('Train...')



  ###############################################
  model.fit(trainX, trainY, validation_data=(testX, testY),verbose=2, epochs=100)


  # make predictions

  trainPredict = model.predict(trainX)
  testPredict = model.predict(testX)

  # invert predictions back to prescaled values
  #This is to compare with original input values
  #SInce we used minmaxscaler we can now use scaler.inverse_transform
  #to invert the transformation.
  trainPredict = scaler.inverse_transform(trainPredict)
  trainY = scaler.inverse_transform([trainY])
  testPredict = scaler.inverse_transform(testPredict)
  testY = scaler.inverse_transform([testY])

  # calculate root mean squared error
  trainScore = math.sqrt(mean_squared_error(trainY[0], trainPredict[:,0]))
  #print('Train Score: %.2f RMSE' % (trainScore))

  testScore = math.sqrt(mean_squared_error(testY[0], testPredict[:,0]))
  #print('Test Score: %.2f RMSE' % (testScore))
  RMSE.append(testScore)

  lista = trainY.tolist()[0]
  size = len(lista)
  metric_df = dataframe.tail(size)
  metric_df['yhat'] = lista
  metric_df.dropna(inplace=True)
  mae = mean_absolute_error(metric_df.Rating, metric_df.yhat)
  MAE.append(mae)

  #gerar futuras previsões
  import numpy as np
  import pandas as pd
  import tensorflow as tf
  from datetime import datetime, timedelta
  from datetime import date
  from dateutil.relativedelta import relativedelta
  from tensorflow.keras.layers import Dense, LSTM
  from tensorflow.keras.models import Sequential
  from sklearn.preprocessing import MinMaxScaler
  pd.options.mode.chained_assignment = None
  tf.random.set_seed(0)

  #  data
  y = dataframe['Rating'].fillna(method='ffill')
  y = y.values.reshape(-1, 1)

  # scale the data
  scaler = MinMaxScaler(feature_range=(0, 1))
  scaler = scaler.fit(y)
  y = scaler.transform(y)

  # generate the input and output sequences
  n_lookback = 6  # length of input sequences (lookback period)
  n_forecast = 12  # length of output sequences (forecast period)

  X = []
  Y = []

  for i in range(n_lookback, len(y) - n_forecast + 1):
    X.append(y[i - n_lookback: i])
    Y.append(y[i: i + n_forecast])

  X = np.array(X)
  Y = np.array(Y)

  # fit the model
  model = Sequential()
  model.add(LSTM(units=50, return_sequences=True, input_shape=(n_lookback, 1)))
  model.add(LSTM(units=50))
  model.add(Dense(n_forecast))

  model.compile(loss='mean_squared_error', optimizer='adam')
  model.fit(X, Y, epochs=100, batch_size=32, verbose=0)

  # generate the forecasts
  X_ = y[- n_lookback:]  # last available input sequence
  X_ = X_.reshape(1, n_lookback, 1)

  Y_ = model.predict(X_).reshape(-1, 1)
  Y_ = scaler.inverse_transform(Y_)

  #criando datas para a quantidade de predições
  data =[]
  dataframe=df[df['Name']==name]
  date = dataframe.iloc[-1,2]
  format = '%Y-%m-%d'
  dt = datetime.strptime(date, format)
  for i in range(n_forecast+1):
    next_month = dt.replace(day=1) + relativedelta(months=i+1)
    data.append(next_month.strftime('%Y-%m-%d'))    

  #usando o flatten para transformar de numpy array para uma lista
  list_y = list(Y_.flatten())

  #criando um dataframe com as novas datas e as predições
  df_pred = pd.DataFrame(list(zip(data, list_y)),
               columns =['Date', 'Rating_Predicted'])

  #concatenando com os dados originais
  df_original = dataframe[['Period','Rating']]
  results = df_original.append(df_pred).set_index('Period')

  # grafico dos dados históricos + predições
  results.plot(title='Fide Rating',figsize=(20,10))

keras_univariate_results = pd.DataFrame(
    {'name': l,
     'MAE': MAE,
     'RMSE':RMSE
    })
keras_univariate_results = keras_univariate_results.sort_values(by='RMSE')
keras_univariate_results

df_pred
