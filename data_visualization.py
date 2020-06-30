#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# code to improve SVM
# authors: A. Ramirez-Morales and J. Salmon-Gamboa

# visualization module

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import pandas as pd

# sample plots
def plot_frame(frame,name,xlabel,ylabel,yUserRange,ymin,ymax,sample):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # plt.hist(sample, 100, density=True, label = 'Sampling')
    # plt.plot(x,y,label='Gaussian fit')
    # frame.plot()
    plt.plot(frame,label=sample)
    if yUserRange:
        plt.ylim(ymin,ymax)    
    # plt.text(0.15, 0.9,'$\mu$={}, $\sigma$={}'.format(round(1.0,1), round(1.0,1)),
    #          ha='center', va='center', transform=ax.transAxes)
    plt.legend(frameon=False)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(name)
    plt.savefig('./plots/'+name+'.pdf')
    plt.close()
