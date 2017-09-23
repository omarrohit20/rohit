# -*- coding: utf-8 -*-
"""
    Miscellaneous Functions for Regression File.
"""

from __future__ import print_function
import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.metrics import *
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
from sklearn.ensemble import BaggingRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn import neighbors
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
#from sklearn.svm import SVR
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.svm import SVC, SVR
from sklearn.qda import QDA
import os
from sklearn.grid_search import GridSearchCV
from Neural_Network import NeuralNet

import logging
from sklearn.ensemble.bagging import BaggingClassifier
log = logging.getLogger(__name__)

def load_dataset(path_directory, symbol): 
    """
        Import DataFrame from Dataset.
    """

    path = os.path.join(path_directory, symbol)

    out = pd.read_csv(path, index_col=2, parse_dates=[2])
    out.drop(out.columns[0], axis=1, inplace=True)
    #dateparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%d')
    #out = pd.read_csv(path, index_col=0, parse_dates=True)
    
    #name = path_directory + '/sp.csv'
    #sp = pd.read_csv(name, index_col=0, parse_dates=[1])
    
    #name = path_directory + '/GOOGL.csv'
    #nasdaq = pd.read_csv(name, index_col=1, parse_dates=[1])
    
    #name = path_directory + '/treasury.csv'
    #treasury = pd.read_csv(name, index_col=0, parse_dates=[1])
    
    #return [sp, nasdaq, djia, treasury, hkong, frankfurt, paris, nikkei, london, australia]
    #return [out, nasdaq, djia, frankfurt, hkong, nikkei, australia]
    return [out]    

def count_missing(dataframe):
    """
    count number of NaN in dataframe
    """
    return (dataframe.shape[0] * dataframe.shape[1]) - dataframe.count().sum()

def addFeatures(dfsource, dftarget, close, n):
    """
    operates on two columns of dataframe:
    - n >= 2
    - given Return_* computes the return of day i respect to day i-n. 
    - given AdjClose_* computes its moving average on n days

    """
    
    return_n = "PCT_change" + str(n)
    dftarget[return_n] = (dfsource[close].pct_change(n))*100
       
def addFeaturesVolChange(dfsource, dftarget, volume, n):
    return_n = "VOL_change" + str(n)
    dftarget[return_n] = (dfsource[volume].pct_change(n))*100   
 
        
# def addFeatures(dataframe, adjclose, returns, n):
#     """
#     operates on two columns of dataframe:
#     - n >= 2
#     - given Return_* computes the return of day i respect to day i-n. 
#     - given AdjClose_* computes its moving average on n days
# 
#     """
#     
#     return_n = adjclose[9:] + "Time" + str(n)
#     dataframe[return_n] = dataframe[adjclose].pct_change(n)
#     
#     roll_n = returns[7:] + "RolMean" + str(n)
#     dataframe[roll_n] = pd.rolling_mean(dataframe[returns], n)
# 
#     exp_ma = returns[7:] + "ExponentMovingAvg" + str(n)
#     dataframe[exp_ma] = pd.ewma(dataframe[returns], halflife=30)
#  
   
def mergeDataframes(datasets):
    """
        Merge Datasets into Dataframe.
    """
    return pd.concat(datasets)

    
def applyTimeLag(dataset, lags, delta):
    """
        apply time lag to return columns selected according  to delta.
        Days to lag are contained in the lads list passed as argument.
        Returns a NaN free dataset obtained cutting the lagged dataset
        at head and tail
    """
    maxLag = max(lags)

    columns = dataset.columns[::(2*max(delta)-1)]
    for column in columns:
        newcolumn = column + str(maxLag)
        dataset[newcolumn] = dataset[column].shift(maxLag)

    return dataset.iloc[maxLag:-1, :]

# CLASSIFICATION    

def prepareDataForClassification(dataset, start_test):
    """
    generates categorical to be predicted column, attach to dataframe 
    and label the categories
    """
    le = preprocessing.LabelEncoder()
    
    dataset['UpDown'] = dataset['Return_Out']
    dataset.UpDown[dataset.UpDown >= 0] = 'Up'
    dataset.UpDown[dataset.UpDown < 0] = 'Down'
    dataset.UpDown = le.fit(dataset.UpDown).transform(dataset.UpDown)
    
    features = dataset.columns[1:-1]
    X = dataset[features]    
    y = dataset.UpDown    
    
    X_train = X[X.index < start_test]
    y_train = y[y.index < start_test]    
    
    X_test = X[X.index >= start_test]    
    y_test = y[y.index >= start_test]
    
    return X_train, y_train, X_test, y_test    

def prepareDataForModelSelection(X_train, y_train, start_validation):
    """
    gets train set and generates a validation set splitting the train.
    The validation set is mandatory for feature and model selection.
    """
    X = X_train[X_train.index < start_validation]
    y = y_train[y_train.index < start_validation]    
    
    X_val = X_train[X_train.index >= start_validation]    
    y_val = y_train[y_train.index >= start_validation]   
    
    return X, y, X_val, y_val
  
def performClassification(X_train, y_train, X_test, y_test, method, parameters={}):
    """
        Perform Classification with the help of serveral Algorithms.
    """

    log.info('Performing %s Classification...%s', method)
    log.info('Size of train set: %s', X_train.shape)
    log.info('Size of test set: %s', X_test.shape)
    log.info('Size of train set: %s', y_train.shape)
    log.info('Size of test set: %s', y_test.shape)
    

    classifiers = [
        RandomForestClassifier(n_estimators=100, n_jobs=-1),
        neighbors.KNeighborsClassifier(),
        SVC(degree=100, C=10000, epsilon=.01),
        AdaBoostRegressor(),
        AdaBoostClassifier(**parameters)(),
        GradientBoostingClassifier(n_estimators=100),
        QDA(),
    ]

    scores = []

    for classifier in classifiers:
        scores.append(benchmark_classifier(classifier, \
            X_train, y_train, X_test, y_test))

    log.info('%s',scores)

def benchmark_classifier(clf, X_train, y_train, X_test, y_test):
    clf.fit(X_train, y_train)
    accuracy = clf.score(X_test, y_test)
    #auc = roc_auc_score(y_test, clf.predict(X_test))
    return accuracy

# REGRESSION

def performClassification(dataset, split, symbol, output_dir, forecast_out):
    """
        Performing Classification on 
        Various algorithms
    """

    predicted_values = []

    features = dataset.columns[:-1]
    
    index = int(np.floor(dataset.shape[0]*split))
    train, test, test_forecast = dataset[:index], dataset[index:-forecast_out], dataset[-forecast_out:]
    #dataset_all, test_forecast = dataset[:-forecast_out], dataset[-forecast_out:]
    #test = dataset_all.sample(frac=0.025)
    #train = dataset_all.loc[~dataset_all.index.isin(test.index)]

    log.info('-'*80)
    log.info('%s train set: %s, test set: %s', symbol, train.shape, test.shape)
    predicted_values.append(str(symbol))
    predicted_values.append(str(train.shape))
    predicted_values.append(str(test.shape))
    
    #train, test = getFeatures(train[features], \
    #    train[output], test[features], 16)

    out_params = (symbol, output_dir)

    output = dataset.columns[-1]

    classifiers = [
        RandomForestClassifier(n_estimators=100, n_jobs=-1),
        SVC(degree=100, C=10000),
        BaggingClassifier(),
        AdaBoostClassifier(),
        neighbors.KNeighborsClassifier(),
        GradientBoostingClassifier(n_estimators=100),
        #QDA(),
    ]

    for classifier in classifiers:
        model_name, forecast_set, accuracy = benchmark_classifier(classifier, \
            train, test, test_forecast, features, symbol, output, out_params)
        log.info('%s, %s, %s, %s', symbol, model_name, forecast_set, accuracy)
        predicted_values.append(str(round(forecast_set.ravel()[0], 3)))
        predicted_values.append(str(round(accuracy, 3)))
    
    return predicted_values

def performClassification(dataset, split, symbol, output_dir, forecast_out, classifier):
    predicted_values = []

    features = dataset.columns[:-1]
    
    index = int(np.floor(dataset.shape[0]*split))
    train, test, test_forecast = dataset[:index], dataset[index:-forecast_out], dataset[-forecast_out:]

    log.info('-'*80)
    log.info('%s train set: %s, test set: %s', symbol, train.shape, test.shape)

    out_params = (symbol, output_dir)
    output = dataset.columns[-1]

    model_name, forecast_set, accuracy = benchmark_classifier(classifier, \
        train, test, test_forecast, features, symbol, output, out_params)
    log.info('%s, %s, %s, %s', symbol, model_name, forecast_set, accuracy)
    predicted_values.append(str(round(forecast_set.ravel()[0], 3)))
    predicted_values.append(str(round(accuracy, 3)))

    return predicted_values

def benchmark_classifier(model, train, test, test_forecast, features, symbol, output, \
    output_params, *args, **kwargs):
    '''
        Performs Training and Testing of the Data on the Model.
    '''

    model_name = model.__str__().split('(')[0].replace('Classifier', ' Classifier')

    symbol, output_dir = output_params

    model.fit(train[features].as_matrix(), train[output].astype(int).as_matrix(), *args, **kwargs)
    predicted_value = model.predict(test[features].as_matrix())
    
    accuracy = model.score(test[features].as_matrix(), test[output].astype(int).as_matrix())
    forecast_set = model.predict(test_forecast[features].as_matrix())
    
    plt.plot(test[output].as_matrix(), color='g', ls='--', label='Actual Value')
    plt.plot(predicted_value, color='b', ls='--', label='predicted_value Value')

    plt.xlabel('Number of Set')
    plt.ylabel('Output Value')

    plt.title(model_name)
    plt.legend(loc='best')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, str(symbol) + '_' \
        + model_name + '.png'), dpi=100)
    #plt.show()
    plt.clf()

    return model_name, forecast_set, accuracy
    
def getFeatures(X_train, y_train, X_test, num_features):
    ch2 = SelectKBest(chi2, k=5)
    X_train = ch2.fit_transform(X_train, y_train)
    X_test = ch2.transform(X_test)
    return X_train, X_test

def performRegression(dataset, split, symbol, output_dir):
    """
        Performing Regression on 
        Various algorithms
    """

    features = dataset.columns
    index = int(np.floor(dataset.shape[0]*split))
    train, test = dataset[:index], dataset[index:]
    log.info('Size of train set: %s', train.shape)
    log.info('Size of test set: %s', test.shape)
    
    #train, test = getFeatures(train[features], \
    #    train[output], test[features], 16)

    out_params = (symbol, output_dir)

    output = dataset.columns[-1]

    predicted_values = []

    classifiers = [
        RandomForestRegressor(n_estimators=10, n_jobs=-1),
        SVR(C=100000, kernel='rbf', epsilon=0.1, gamma=1, degree=2),
        BaggingRegressor(),
        AdaBoostRegressor(),
        KNeighborsRegressor(),
        GradientBoostingRegressor(),
    ]

    for classifier in classifiers:

        predicted_values.append(benchmark_model(classifier, \
            train, test, features, output, out_params))

    maxiter = 1000
    batch = 150

    classifier = NeuralNet(50, learn_rate=1e-2)

    predicted_values.append(benchmark_model(classifier, \
        train, test, features, output, out_params, \
        fine_tune=False, maxiter=maxiter, SGD=True, batch=batch, rho=0.9))
    

    log.info('-'*80)

    mean_squared_errors = []

    r2_scores = []

    for pred in predicted_values:
        mean_squared_errors.append(mean_squared_error(test[output].as_matrix(), \
            pred.as_matrix()))
        r2_scores.append(r2_score(test[output].as_matrix(), pred.as_matrix()))

    log.info('%s %s', mean_squared_errors, r2_scores)

    return mean_squared_errors, r2_scores

def performRegression(dataset, split, symbol, output_dir, forecast_out):
    """
        Performing Regression on 
        Various algorithms
    """

    predicted_values = []

    features = dataset.columns[:-1]
    
    index = int(np.floor(dataset.shape[0]*split))
    train, test, test_forecast = dataset[:index], dataset[index:-forecast_out], dataset[-forecast_out:]
    #dataset_all, test_forecast = dataset[:-forecast_out], dataset[-forecast_out:]
    #test = dataset_all.sample(frac=0.025)
    #train = dataset_all.loc[~dataset_all.index.isin(test.index)]

    log.info('-'*80)
    log.info('%s train set: %s, test set: %s', symbol, train.shape, test.shape)
    predicted_values.append(str(symbol))
    predicted_values.append(str(train.shape))
    predicted_values.append(str(test.shape))
    
    #train, test = getFeatures(train[features], \
    #    train[output], test[features], 16)

    out_params = (symbol, output_dir)

    output = dataset.columns[-1]

    classifiers = [
        RandomForestRegressor(n_estimators=10, n_jobs=-1),
        #SVR(C=1.0, cache_size=200, coef0=0.0, degree=3, epsilon=0.1, gamma='auto', kernel='rbf', max_iter=-1, shrinking=True, tol=0.001),
        MLPRegressor(solver='lbfgs', hidden_layer_sizes=(40,20)),
        BaggingRegressor(),
        AdaBoostRegressor(),
        KNeighborsRegressor(),
        GradientBoostingRegressor()
        #NeuralNet(1, learn_rate=1e-2)
    ]

    for classifier in classifiers:
        model_name, forecast_set, accuracy = benchmark_model(classifier, \
            train, test, test_forecast, features, symbol, output, out_params)
        log.info('%s, %s, %s, %s', symbol, model_name, forecast_set, accuracy)
        predicted_values.append(str(round(forecast_set.ravel()[0], 3)))
        predicted_values.append(str(round(accuracy, 3)))
    
    return predicted_values

#     benchmark_model(classifier, \
#         train, test, test_forecast, features, symbol, output, out_params, \
#         fine_tune=False, maxiter=maxiter, SGD=True, batch=batch, rho=0.9)

def performRegression(dataset, split, symbol, output_dir, forecast_out, regressor):
    predicted_values = []
    features = dataset.columns[:-1]
    index = int(np.floor(dataset.shape[0]*split))
    train, test, test_forecast = dataset[:index], dataset[index:-forecast_out], dataset[-forecast_out:]

    log.info('-'*80)
    log.info('%s train set: %s, test set: %s', symbol, train.shape, test.shape)
    
    out_params = (symbol, output_dir)
    output = dataset.columns[-1]

    model_name, forecast_set, accuracy = benchmark_model(regressor, \
        train, test, test_forecast, features, symbol, output, out_params)
    log.info('%s, %s, %s, %s', symbol, model_name, forecast_set, accuracy)
    predicted_values.append(str(round(forecast_set.ravel()[0], 3)))
    predicted_values.append(str(round(accuracy, 3)))
    
    return predicted_values
   
def benchmark_model(model, train, test, features, output, \
    output_params, *args, **kwargs):
    '''
        Performs Training and Testing of the Data on the Model.
    '''

    model_name = model.__str__().split('(')[0].replace('Regressor', ' Regressor')
    log.info(model_name)

    '''
    if 'SVR' in model.__str__():
        tuned_parameters = [{'kernel': ['rbf', 'polynomial'], 'gamma': [1e-3, 1e-4],
                     'C': [1, 10, 100, 1000]},
                    {'kernel': ['linear'], 'C': [1, 10, 100, 1000]}]
        model = GridSearchCV(SVC(C=1), tuned_parameters, cv=5,
                       scoring='%s_weighted' % 'recall')
    '''

    symbol, output_dir = output_params

    model.fit(train[features].as_matrix(), train[output].as_matrix(), *args, **kwargs)
    predicted_value = model.predict(test[features].as_matrix())

    plt.plot(test[output].as_matrix(), color='g', ls='-', label='Actual Value')
    plt.plot(predicted_value, color='b', ls='--', label='predicted_value Value')

    plt.xlabel('Number of Set')
    plt.ylabel('Output Value')

    plt.title(model_name)
    plt.legend(loc='best')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, str(symbol) + '_' \
        + model_name + '.png'), dpi=100)
    #plt.show()
    plt.clf()

    return predicted_value

def benchmark_model(model, train, test, test_forecast, features, symbol, output, \
    output_params, *args, **kwargs):
    '''
        Performs Training and Testing of the Data on the Model.
    '''

    model_name = model.__str__().split('(')[0].replace('Regressor', ' Regressor')
    
    temp = np.ndarray((2,), buffer=np.array([0,0,0]), offset=np.int_().itemsize, dtype=int)
    if model_name == 'MLP Regressor':
        return model_name, temp, 0
    if model_name == 'AdaBoost Regressor':
        return model_name, temp, 0
    if model_name == 'GradientBoosting Regressor':
        return model_name, temp, 0

    '''
    if 'SVR' in model.__str__():
        tuned_parameters = [{'kernel': ['rbf', 'polynomial'], 'gamma': [1e-3, 1e-4],
                     'C': [1, 10, 100, 1000]},
                    {'kernel': ['linear'], 'C': [1, 10, 100, 1000]}]
        model = GridSearchCV(SVC(C=1), tuned_parameters, cv=5,
                       scoring='%s_weighted' % 'recall')
    '''

    symbol, output_dir = output_params

    model.fit(train[features].as_matrix(), train[output].as_matrix(), *args, **kwargs)
    predicted_value = model.predict(test[features].as_matrix())
    
    accuracy = model.score(test[features].as_matrix(), test[output].as_matrix())
    forecast_set = model.predict(test_forecast[features].as_matrix())
    
    plt.plot(test[output].as_matrix(), color='g', ls='--', label='Actual Value')
    plt.plot(predicted_value, color='b', ls='--', label='predicted_value Value')

    plt.xlabel('Number of Set')
    plt.ylabel('Output Value')

    plt.title(model_name)
    plt.legend(loc='best')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, str(symbol) + '_' \
        + model_name + '.png'), dpi=100)
    #plt.show()
    plt.clf()

    return model_name, forecast_set, accuracy
