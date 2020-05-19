#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Code to improve SVM
#authors: A. Ramirez-Morales and J. Salmon-Gamboa

#Main module

# python basics
import sys

# data analysis and wrangling
import numpy as np
import random as rnd
import pandas as pd

# machine learning
from sklearn.svm import SVC, LinearSVC
from sklearn.model_selection import train_test_split

# import module for data preparation
import data_preparation as dp

# import module for data utils
import data_utils as du

# import ML models for comparison
import model_comparison as mc

# make directories
sample_list = ['titanic', 'two_norm', 'cancer', 'german', 'heart', 'solar']
du.make_directories(sample_list)

# main function
def dataset(sample):

    # fetch data set (from available list)
    data_set = dp.fetch_data(sample)

    # check data
    print("Before preparation", data_set.shape)
    print(data_set.columns.values)
    print(data_set.head())
    print(data_set.tail())
    print(data_set.describe())

    # prepare data
    if sample == 'titanic':
        X,Y = dp.titanic(data_set)
    elif sample == 'two_norm':
        X,Y = dp.two_norm(data_set)
    elif sample == 'cancer':
        X,Y = dp.bCancer(data_set)
    elif sample == 'german':
        X,Y = dp.german(data_set)
    elif sample == 'heart':
        X,Y = dp.heart(data_set)
    elif sample == 'solar':
        X,Y = dp.solar(data_set)

        
    # print data after preparation
    print("After preparation", data_set.shape)
    print(X.head())

    # divide sample into train and test sample
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.4)
    print(X_train.shape, Y_train.shape)
    print(X_test.shape, Y_test.shape)
    
    # support vector machine
    # nominal
    
    weights= np.ones(len(Y_train))/len(Y_train)
    
    svc = SVC(C=150.0, kernel='rbf', gamma=10, shrinking = True, probability = True, tol = 0.001)
    svc.fit(X_train, Y_train, weights)
    Y_pred = svc.predict(X_test)
    du.metrics(sample,'svm', svc, X_train, Y_train, Y_test, X_test, Y_pred)    
    
    # comparison with other ml models (fit, predict and metrics)
    #mc.comparison(sample, X_train, Y_train, Y_test, X_test)
    
    return X_train, Y_train, X_test, Y_test


# run main function for every dataset
# for item in sample_list:
#     main(item)
 

class AdaBoostSVM:
    
    def __init__(self):
        
        self.weak_svm = ([])
        self.alphas = ([])
    
    
    def _check_X_y(self, X, y):
        
        # Validate assumptions about format of input data. Expecting response variable to be formatted as ±1
        assert set(y) == {-1, 1}
        
        # convert pandas into numpy arrays
        X = X.values
        y = y.values
        return X, y
        
    
    def svc_train(self, myKernel, C_parameter, myGamma, iniGamma, stepGamma, x_train, y_train, myWeights, count):
        
        if count == 0:
            myGamma = iniGamma
        
        while True:
            if myGamma<0:
                break

            errorOut = 0.0 
            
            svcB = SVC(C = C_parameter, kernel='rbf', gamma=1/(2*(myGamma**2)), shrinking = True, probability = True, tol = 0.001)
            svcB.fit(x_train, y_train, sample_weight=myWeights)
            y_pred = svcB.predict(x_train)
            
            for i in range(len(y_pred)):
                if (y_train[i] != y_pred[i]):                    
                    errorOut += myWeights[i]

            # require an error below 50% and avoid null errors
            if errorOut < 0.5 and errorOut != 0:
                myGamma -= stepGamma
                break
            
            myGamma -= stepGamma
            
        return myGamma, errorOut, y_pred, svcB
    
    
    def fit(self, X, y, C_parameter, gammaIni):
        
        X_train, Y_train = self._check_X_y(X, y)
        n = X.shape[0]
        weights= np.ones(n)/n
        
        gammaMin, gammaStep, gammaVar = 0.1, 0.1, 0.0
        cost, count, norm = 1, 0, 0.0
        h_list = []

        # AdaBoost loop
        while True:
            if count == 0:
                norm = 1.0
                new_weights = weights.copy()

            new_weights = new_weights/norm
        
            # call svm, weight samples, iterate sigma(gamma), get errors, obtain predicted classifier (h as an array) 
            gammaVar, error, h, learner = self.svc_train('rbf', C_parameter, gammaVar, gammaIni, gammaStep, X_train, Y_train, new_weights, count)
        
            # count how many times SVM runs
            count += 1
            
            # calculate precision
            fp,tp = 0,0
            for i in range(n):
                if(Y_train[i]!=h[i]):                
                    fp+=1
                else:
                    tp+=1      
        
            # store the predicted classes
            h_temp = h.tolist()
            h_list.append(h_temp)

            print("Error: {} Precision: {} Gamma: {} ".format(round(error,4), round(tp / (tp + fp),4), round(gammaVar+gammaStep,2)))
            # classifier weights (alpha), obtain and store
            x = (1 - error)/error
            alpha = 0.5 * np.log(x)
            self.alphas = np.append(self.alphas, alpha)
            self.weak_svm = np.append(self.weak_svm, learner)
        
            # reset weight lists
            weights = new_weights.copy()
            new_weights = ([])
            norm = 0.0
        
            # set weights for next iteration
            for i in range(n):
                x = (-1.0) * alpha * Y_train[i] * h[i]
                new_weights = np.append(new_weights, [weights[i] * np.exp(x)] )
                norm += weights[i] * np.exp(x)
        
            # do loop as long gamma > gammaMin, if gamma < 0, SVM fails exit loop
            if gammaVar < gammaMin:#) or (gammaVar < 0):
                break
        

        # h_list into array
        h_list = np.array(h_list)

        print(count,'number of classifiers')

        # Compute precision
        h_alpha = np.array([h_list[i]*self.alphas[i] for i in range(count)])

        final = ([])
        for j in range(len(h_alpha[0])):
            suma = 0.0
            for i in range(count):
                suma+=h_alpha[i][j]
            final = np.append(final, [np.sign(suma)])
            
        # final precision calculation
        final_fp, final_tp  = 0, 0
        for i in range(n):
            if(Y_train[i]!=final[i]):
                final_fp+=1
            else:
                final_tp+=1

        final_precision = final_tp / (final_fp + final_tp)
        print("Final Precision: {} ".format( round(final_precision,4)) )
        #du.metrics(sample,'svmBoosted', svcB, X_train, Y_train, Y_test, X_test, Y_predB)
        
        return self


    def predict(self, X):
        # Make predictions using already fitted model
        svm_preds = np.array([learner.predict(X) for learner in self.weak_svm])
        return np.sign(np.dot(self.alphas, svm_preds))


X_train, Y_train, X_test, Y_test = dataset('titanic')


model = AdaBoostSVM()
model.fit(X_train, Y_train, C_parameter = 150, gammaIni = 10)
y_preda = model.predict(X_test)

test_err = (model.predict(X_test) != Y_test).mean()
print(f'Test error: {test_err:.1%}')


'''
to be pasted at the beginning of the svc_train function
# check normalization 
check = 0.
for i in range(len(myWeights,)):
    check+=myWeights[i]
    
print('Check normalisation', round(check,2))'''

'''
# #weight (boost) training samples
# x_train_boosted = []
# for i in range(len(myWeights)):
#     x_train_boosted.append( x_train[i] * myWeights[i]) 
# x_train_boosted = np.array(x_train_boosted)           
'''
