#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
---------------------------------------------------------------
 Code to improve SVM
 Authors: A. Ramirez-Morales and J. Salmon-Gamboa
 ---------------------------------------------------------------
'''

#main module

# python basics
import sys
import numpy as np
import pandas as pd
import datetime

# machine learning
from sklearn.svm import SVC, LinearSVC

# class for data preparation
from data_preparation import data_preparation

# module for data utils
import data_utils as du

# ML module for comparison
import model_comparison as mc

# AdaBoost class
from boostedSVM import AdaBoostSVM, Div_AdaBoostSVM

# data visualization module
import data_visualization as dv


# start of the module
# make directories
sample_list = ['titanic', 'cancer', 'german', 'heart', 'solar','car','contra','tac_toe', 'belle2_i', 'belle2_ii']
du.make_directories(sample_list)


# get the data
data = data_preparation()

sample_list = ['titanic', 'cancer', 'german', 'heart', 'solar','car','contra','tac_toe']

# initialise loop running over datasets in sample_list for AdaBoostSVM and the other classifiers. Generates ROC curves and metrics
for sample in sample_list:
    X_train, Y_train, X_test, Y_test = data.dataset(sample,'',False,0.4)

    '''
# run single support vector machine
weights= np.ones(len(Y_train))/len(Y_train)
svc = SVC(C=150.0, kernel='rbf', gamma=1/(2*(10**2)), shrinking = True, probability = True, tol = 0.001)
svc.fit(X_train, Y_train, weights)
Y_pred = svc.predict(X_test)
du.metrics(sample,'svm', svc, X_train, Y_train, Y_test, X_test, Y_pred)
    '''

    # run AdaBoost support vector machine
    print('AdaBoost')
    model = AdaBoostSVM(C=50, gammaIni=100)

    start = datetime.datetime.now()
    model.fit(X_train, Y_train)
    end = datetime.datetime.now()
    elapsed_time = pd.DataFrame({'Elapsed time': [end - start]})

    elapsed_time.to_csv('output/' + sample +  '/' + 'AdaBoostSVM_time.csv', index=False)
    y_preda = model.predict(X_test)
    print('Analysing sample: ',sample)
    y_thresholds = model.decision_thresholds(X_test, glob_dec=True)
    TPR, FPR = du.roc_curve_adaboost(y_thresholds, Y_test)

    dv.plot_roc_curve(TPR,FPR,sample,'real',   glob_local=True)
    dv.plot_roc_curve(TPR,FPR,sample,'sorted', glob_local=True)
    print('End adaboost')

    # comparison with other ml models (fit, predict and metrics)
    mc.comparison(sample, X_train, Y_train, Y_test, X_test)
    #du.cv_metrics(model, X_train, Y_train)


# check model performance
test_pre = (model.predict(X_test) == Y_test).mean()
test_err = (model.predict(X_test) != Y_test).mean()
print(f'Test prec.: {test_pre:.1%}')
print(f'Test error: {test_err:.1%}')


# # metrics for plots
# weights, errors, precision = model.get_metrics()

# # precision plot
# dv.plot_frame(pd.DataFrame(precision*100,np.arange(precision.shape[0])),
#                            'Classifier precision', 'Classifier', 'training precision (%)', True, 0, 100,'belle2_i')
# # errors plot
# dv.plot_frame(pd.DataFrame(errors*100,np.arange(errors.shape[0])),
#                            'Classifier error', 'Classifier', 'training error (%)', True, 0, 100,'belle2_i')

# # weights plot
# dv.plot_frame(pd.DataFrame(weights[10],np.arange(weights.shape[1])),
#                            'Sample weights', 'Sample', 'weights (a.u.)', True, -0.005, 0.01,'belle2_i')    

# # grid hyper parameter 2D-plots
# matrix = du.grid_param_gauss(X_train, Y_train, X_test, Y_test, sigmin=-5, sigmax=5, cmin=0, cmax=6)
# dv.plot_2dmap(matrix,-5,5,0,6,'belle2_i')
        
# # boostrap error VS number of classiffiers calculation
# frame = du.error_number('belle2_i',myC=50,myGammaIni=10)
# dv.plot_frame(frame, 'Classifiers error', 'No. Classifiers', 'test error', False, 0, 50,'belle2_i')
