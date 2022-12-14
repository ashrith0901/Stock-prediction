# -*- coding: utf-8 -*-
"""stock price prediction

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1N08DIbY3D0mNZfVTxWuTQyOc5X8uYumH
"""

# Commented out IPython magic to ensure Python compatibility.
import math

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
# %matplotlib inline 

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM

tsla_df = pd.read_csv('tsla.csv')

tsla_df.head(5)

tsla_df = tsla_df.drop(['Dividends', 'Stock Splits'], axis=1)
tsla_df

# shape of the dataset = 504-rows x 6-cols

tsla_df.isnull().sum()

plt.figure(figsize=(9, 3))

sns.countplot(data = tsla_df.iloc[0:], orient='h', color = 'steelblue')          # countplot does not include 'nan' values

tsla_df.info()                                         # python treats date and datetime as object

tsla_df.describe().apply(lambda s: s.apply('{:.3f}'.format)).T                # or s.apply('{:.5f}'.format)

tsla_df.info()

tsla_df.describe().apply(lambda s: s.apply('{:.3f}'.format)).T                # or s.apply('{:.5f}'.format)

tsla_df.info()

df_close = tsla_df['Close']
df_close

tsla_df.head()

font = {'family': 'serif',
        'color':  'darkred',
        'weight': 'bold',
        'size': 16,
        }

plt.figure(figsize=(12, 8))
plt.subplot(3, 1, 1)
plt.plot(tsla_df['Open'], label='Open')
plt.plot(tsla_df['Close'], label='Close')
plt.xlabel('INDEX', fontdict=font)
plt.ylabel('OPEN v/s CLOSE', fontdict=font)
plt.legend()                                                 # legend() : it is an area describing the elements of the graph

plt.subplot(3, 1, 2)
plt.plot(tsla_df['Low'], label='Low')
plt.plot(tsla_df['High'], label='High')
plt.xlabel('INDEX', fontdict=font)
plt.ylabel("LOW v/s HIGH", fontdict=font)
plt.legend()

plt.tight_layout()                                           # tight_layout() : automatically adjusts the subplots in the area

# LSTM are sensitive to the scale of the data. MIN_MAX scaler will help to convert that data b/w 0 to 1.
# Min value = 0, Max val = 1
# X_std = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0))
# eg : (224 - 204) / (409 - 204)  ==  0.0975

scaler = MinMaxScaler(feature_range=(0,1))

# df_close is of type pandas.series i.e, 1-D of shape (504, )
# but scaling object accepts 2-D frame.
# so used np.array to change it into 2-D frame

df_close = scaler.fit_transform(np.array(df_close).reshape(-1, 1))
df_close.shape

# now the shape of df_close is (504, 1)

print(type(df_close))
font = {'family': 'serif',
        'color':  'darkred',
        'weight': 'bold',
        'size': 16,
        }

plt.figure(figsize=(12, 8))
plt.subplot(3, 1, 1)
plt.plot(df_close, label='Open')
plt.xlabel('INDEX', fontdict=font)
plt.ylabel('SCALED PRICE', fontdict=font)
plt.legend()
plt.tight_layout()

train_size = int(len(df_close)*0.70)                       # train size = 70%
test_size = len(df_close) - train_size                     # test size = 30%

train_data, test_data = df_close[0:train_size, :], df_close[train_size:len(df_close), :]

train_size, test_size

# Whenever we will have time series data, the next data is always dependent on the previous data

def create_dataset(dataset, time_step):
    dataX, dataY = [], []
    for i in range(len(dataset) - time_step - 1):
        a = dataset[i:(i+time_step), 0]
        dataX.append(a)
        dataY.append(dataset[(i+time_step), 0])
    
    return np.array(dataX), np.array(dataY)

time_step = 100
X_train, y_train = create_dataset(train_data, time_step)
X_test, y_test = create_dataset(test_data, time_step)

X_train.shape, y_train.shape

n_features = 1
X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], n_features)
X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], n_features)

# define Stacked LSTM model
# Models that input or output data sequences are called Sequential Model, eg: text stream, audio, video, time-series data etc.

model = Sequential()
model.add(LSTM(50, activation='relu', return_sequences=True, input_shape = (time_step, n_features)))
# added one LSTM model of 50 neurons
# Return sequence = True, the output of the hidden state of each neuron is used as an input to the next LSTM layer

model.add(LSTM(50, return_sequences = True, activation='relu'))
model.add(LSTM(50))
model.add(Dense(1))
# Dense layer is added to get output in format needed by the user. It is fully connected layer at the end of neural network

model.compile(loss='mean_squared_error', optimizer='adam')

model.summary()

model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=100, batch_size=64, verbose = 1)

# verbose    : visual representation of epoch processing(0/1/2)
# epochs     : Each time a complete/entire dataset passes through an algorithm, it is said to have completed an epoch.
# batch_size : The training data is always broken down into small batches to overcome the issue that could arise due to 
#              storage space limitations of a computer system.

# This procedure is known as an epoch when all the batches are fed into the model to train at once. 
# Another way to define an epoch is the number of passes a training dataset takes around an algorithm. 
# One pass is counted when the data set has done both forward and backward passes. 
# The number of epochs as well as batch_size is considered a hyperparameter.

train_predict = model.predict(X_train)
test_predict = model.predict(X_test)

train_predict = scaler.inverse_transform(train_predict)
y_train = y_train.reshape(y_train.shape[0], 1)
y_train = scaler.inverse_transform(y_train)
y_test = y_test.reshape(y_test.shape[0], 1)
y_test = scaler.inverse_transform(y_test)
test_predict = scaler.inverse_transform(test_predict)

font = {'family': 'serif',
        'color':  'darkred',
        'weight': 'bold',
        'size': 12,
        }

plt.figure(figsize=(12, 8))
plt.subplot(3, 1, 1)
plt.plot(y_train, label='y_train')
plt.plot(train_predict, label='train_predict')
plt.xlabel("INDEX", fontdict=font)
plt.ylabel("CLOSE PRICE", fontdict=font)
plt.legend()

math.sqrt(mean_squared_error(y_train, train_predict))

math.sqrt(mean_squared_error(y_test, test_predict))

# first 50 will be vacant
trainPredictPlot = np.empty_like(df_close)
trainPredictPlot[:, :] = np.nan
trainPredictPlot[time_step:len(train_predict)+time_step, : ] = train_predict

testPredictPlot = np.empty_like(df_close)
testPredictPlot[:, :] = np.nan
testPredictPlot[len(train_predict)+2*time_step+1:len(df_close)-1, :] = test_predict

font = {'family': 'serif',
        'color':  'darkred',
        'weight': 'bold',
        'size': 14,
        }

plt.figure(figsize=(10, 4))
plt.subplot(1, 1, 1)
plt.plot(scaler.inverse_transform(df_close), label='Actual Close')
plt.plot(trainPredictPlot, label='train_predict')
plt.plot(testPredictPlot, label='test_predict')
plt.xlabel('INDEX', fontdict=font)
plt.ylabel('CLOSE PRICE', fontdict=font)
plt.legend()                                                 # legend() : it is an area describing the elements of the graph

plt.tight_layout()                                           # tight_layout() : automatically adjusts the subplots in the area

len(test_data)

x_input = test_data[52: ].reshape(1, -1)
print(type(x_input))
print(x_input.shape)

temp_input = list(x_input)
temp_input = temp_input[0].tolist()
print(len(temp_input))
print(type(temp_input))

# predicting the next 30 days 

lst_output = []
i=0

while(i<30):
    if(len(temp_input)>100):
        x_input = np.array(temp_input[1:])
        x_input = x_input.reshape(1, -1)
        x_input = x_input.reshape((1, time_step, 1))
        y_input = model.predict(x_input, verbose=0)
        temp_input.extend(y_input[0].tolist())
        temp_input = temp_input[1:]
        lst_output.extend(y_input[0].tolist())
        i=i+1
    else:
        x_input = x_input.reshape((1, time_step, 1))
        y_input = model.predict(x_input)
        temp_input.extend(y_input[0].tolist())
        lst_output.extend(y_input[0].tolist())
        i=i+1

day_new = np.arange(1, 101)
day_pred = np.arange(101, 131)

len(df_close)

lst_df = pd.DataFrame(lst_output)

font = {'family': 'serif',
        'color':  'darkred',
        'weight': 'bold',
        'size': 14,
        }

plt.figure(figsize=(10, 3))
plt.subplot(1, 1, 1)
plt.plot(day_new, scaler.inverse_transform(df_close[404:]), label = "Actual")
plt.plot(day_pred, scaler.inverse_transform(lst_df), label = "Predicted")
plt.xlabel('INDEX', fontdict=font)
plt.ylabel('CLOSE PRICE', fontdict=font)
plt.legend()                                                 # legend() : it is an area describing the elements of the graph

plt.tight_layout()

arr = np.array(df_close[:])
arr = arr.reshape(1, -1)
temp = list(arr)
temp = temp[0].tolist()
temp.extend(lst_output)
final_df = pd.DataFrame(temp)

font = {'family': 'serif',
        'color':  'darkred',
        'weight': 'bold',
        'size': 12,
        }

plt.figure(figsize=(10, 3))
plt.subplot(1, 1, 1)
plt.plot(scaler.inverse_transform(final_df))
plt.xlabel('INDEX', fontdict=font)
plt.ylabel('CLOSE PRICE', fontdict=font)
plt.tight_layout()