#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 19 10:48:20 2020

@author: robert.tseng
"""
# =============================================================================
# import lib
# =============================================================================
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd 

def plt_win_fund_rate(funds, win_rate, players):
    f = plt.figure(figsize=(10,3), facecolor = 'black')
    ax1 = f.add_subplot(121, facecolor = 'black')
    ax2 = f.add_subplot(122, facecolor = 'black')
    max1 = max(map(abs, funds))
    ## First plot
    ax1.set_xlim([- (max1+100), max1+100])
    ax1.set_ylim([-0.5, len(players)-0.5])
    for i, row in enumerate(funds): 
        if row < 0:
            color = 'g'
        else:
            color = 'r'
        ax1.barh(i*1, row, \
                color= color, align='center',
                edgecolor='w')
        ax1.plot([- (max1+100), max1+100], [i, i],color = 'w', \
                 linestyle='dashed')
    ax1.plot([0,0], [-0.5, len(players)+0.5],color = 'w')
    ax1.set_yticks(range(0, len(players)))
    ax1.set_yticklabels(players, color = 'w')
    ax1.spines['top'].set_visible(False)
    # ax1.spines['bottom'].set_color('w')
    ax1.spines['right'].set_color('w')
    ax1.spines['left'].set_visible(False)
    ax1.set_xlabel('Funds', color = 'w')
    ax1.set_ylabel('Players', color = 'w')
    ax1.set_title('Win Funds Plot', color = 'w')
    ax1.tick_params(axis='x', color = 'w')
    [t.set_color('w') for t in ax1.xaxis.get_ticklabels()]
    ax1.xaxis.label.set_color('w')
    ## Second plot
    ax2.tick_params(axis='x', color = 'w')
    ax2.tick_params(axis='y', color = 'w')
    ax2.set_facecolor('black')       
    ax2.set_ylim([0, 1])
    ax2.set_xlabel('Game Round', color = 'w')
    ax2.set_ylabel('Win rate', color = 'w')
    ax2.plot(win_rate)
    ax2.legend(players,loc=(1.04,0))
    ax2.set_title('Win Rate plot', color = 'w')
    ax2.spines['left'].set_color('w')
    ax2.spines['right'].set_color('w')
    ax2.spines['bottom'].set_color('w')
    ax2.spines['top'].set_color('w')
    [t.set_color('w') for t in ax2.yaxis.get_ticklabels()]
    [t.set_color('w') for t in ax2.xaxis.get_ticklabels()]