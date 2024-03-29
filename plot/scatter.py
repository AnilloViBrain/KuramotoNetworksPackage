#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import scipy.stats as stats
import scipy.signal as signal
import matplotlib.pyplot as plt
import matplotlib.axes as axes

#Scatter plots
def bivariable_std(datax,datay,ax,meanx_zero=0,meany_zero=0,stdx_zero=1,stdy_zero=1,mean_axis=1,cmap=plt.cm.Blues,marker='o',
                   flagstdx=False,flagstdy=False,meanzero_type='dot',relative_diference=True,labels=[''],colormap='None',cmap_scale=0.12):
    """
    Formatted 2D scatter plot to compare 2 features with the same features of the baseline case or from another class.
    
    Parameters:
    -----------
    
    datax: float 2D array
        Data matrix for the feature x.
    datay: float 2D array
        Data matrix for the feature y. Could be None to only compare one feature. 
    ax : pyplot.plot.axes
        An axes from a subplot in a matplotlib figure.
    meanx_zero: float
        Mean value of the feature x of the baseline case or from another class.
    meany_zero: float
        means of baseline data of the feature y of the baseline case or from another class.
    stdx_zero: float
        standard deviation of the feature x of the baseline data.
    stdy_zero: float
        standard deviation of of the feature y of the baseline data.
    mean_axis= int, optional
        Defines which axis is the time/samples of the data matrices **datax** and **datay** . The default is 1, which means the matrices has size N X samples.
    cmap: pyplot.plot.colormap
        A valid matplotlib colormap.
    marker: str, plot marker 
        type of marker for the data.
    flagstdx: boolean, optional 
        plot the standard deviation in the x-axis. Default is False.
    flagstdy: boolean, optional
        plot the stadard deviation in the y-axis. Default is False.
    
    relative_diference: boolean, optional 
        plot in percentages of realive error with respect the means of the baseline data. Default is true.
    labels : list
        List with the labels for names of the N patterns/subjects. 
    colormap: str, 'direct'/'None', optional
        'direct': Apply the specified cmap one by one to the N patterns. cmap must contain at less N colors.
        'None' (Default): Apply the normalized cmap, with a factor scale to make more 'pretty' the result.
    cmap_scale: float between 0 and 1, optional
        Scale factor for the markers colors. Note that with zero, all markers are the same color, with 1 the color is the less intense of the cmap.
        Default is 0.12, works well for a single color cmap and N between 5 and 10. 
    
    Returns 
    -------
    ax: matplotlib.pyplot.axes
        Axes that show the result. Usually assigned to the same in the **ax** parameter.
    """
    ###Statisitic of the data
    flag_error=0
    if datay=='None':
        meanx=np.nanmean(datax,axis=mean_axis)
        stdx=np.nanstd(datax,axis=mean_axis)
        stdy=np.zeros_like(stdx)
        meany=np.arange(len(meanx))
        flagstdy=False
    elif datax=='None':
        meany=np.nanmean(datay,axis=mean_axis)
        stdy=np.nanstd(datay,axis=mean_axis)
        stdx=np.zeros_like(stdy)
        meanx=np.arange(len(meany))
        flagstdx=False
    else:
        meanx=np.nanmean(datax,axis=mean_axis)
        stdx=np.nanstd(datax,axis=mean_axis)
        meany=np.nanmean(datay,axis=mean_axis)
        stdy=np.nanstd(datay,axis=mean_axis)
    
    if type(meanx)!=np.float64:
        data_length=len(meanx)
        if len(meanx)!=len(meany):
            flag_error=2
    else:
        data_length=1
    ###If relative difference is required
    if relative_diference:
        ##If means is zero, the increase or decrease is directly a percentage/
        if meanx_zero==0:
            meanx=meanx*100 
            stdx=stdx*100
        else:
            meanx=(meanx-meanx_zero)/(meanx_zero)*100
            stdx=(stdx)/(meanx_zero)*100
        
        if meany_zero==0:
            meany=meany*100
            stdx=stdx*100
        else:
            meany=(meany-meany_zero)/(meany_zero)*100
            stdy=(stdy)/(meany_zero)*100
        #Change baseline values to zero
        if meanx_zero==0:
            stdx_zero=stdx_zero*100
        else:
            stdx_zero=(stdx_zero)/(meanx_zero)*100
        
        if meany_zero==0:
            stdy_zero=stdy_zero*100
        else:
            stdy_zero=(stdy_zero)/(meany_zero)*100
        meanx_zero=0
        meany_zero=0
       
    
    if flag_error==0:
        if meanzero_type=='dot':
            ax.plot(meanx_zero,meany_zero,'k',marker='o',markersize=10,label='SHAM')
            if flagstdx:
                ax.plot([stdx_zero+meanx_zero,stdx_zero+meanx_zero],[np.min([meany_zero-stdy_zero,np.min(meany-stdy)]),np.max([meany_zero+stdy_zero,np.max(meany+stdy)])],'+k')
                ax.plot([meanx_zero-stdx_zero,meanx_zero-stdx_zero],[np.min([meany_zero-stdy_zero,np.min(meany-stdy)]),np.max([meany_zero+stdy_zero,np.max(meany+stdy)])],'+k')
            if flagstdy:
                ax.plot([np.min([meanx_zero-stdx_zero,np.min(meanx-stdx)]),np.max([meanx_zero+stdx_zero,np.max(meanx+stdx)])],[stdy_zero+meany_zero,stdy_zero+meany_zero],'+k')
                ax.plot([np.min([meanx_zero-stdx_zero,np.min(meanx-stdx)]),np.max([meanx_zero+stdx_zero,np.max(meanx+stdx)])],[meany_zero-stdy_zero,meany_zero-stdy_zero],'+k')
        elif meanzero_type=='line':
            ax.plot([meanx_zero,meanx_zero],[np.min([meany_zero-stdy_zero,np.min(meany-stdy)]),np.max([meany_zero+stdy_zero,np.max(meany+stdy)])],'k',linewidth=0.5,label='SHAM')
            ax.plot([np.min([meanx_zero-stdx_zero,np.min(meanx-stdx)]),np.max([meanx_zero+stdx_zero,np.max(meanx+stdx)])],[meany_zero,meany_zero],'k',linewidth=0.5)
            if flagstdx:
                ax.plot([stdx_zero+meanx_zero,stdx_zero+meanx_zero],[np.min([meany_zero-stdy_zero,np.min(meany-stdy)]),np.max([meany_zero+stdy_zero,np.max(meany+stdy)])],'k',linestyle=(0,(2,5)),linewidth=0.5)
                ax.plot([meanx_zero-stdx_zero,meanx_zero-stdx_zero],[np.min([meany_zero-stdy_zero,np.min(meany-stdy)]),np.max([meany_zero+stdy_zero,np.max(meany+stdy)])],'k',linestyle=(0,(2,5)),linewidth=0.5)
            if flagstdy:
                ax.plot([np.min([meanx_zero-stdx_zero,np.min(meanx-stdx)]),np.max([meanx_zero+stdx_zero,np.max(meanx+stdx)])],[stdy_zero+meany_zero,stdy_zero+meany_zero],'k',linestyle=(0,(2,5)),linewidth=0.5)
                ax.plot([np.min([meanx_zero-stdx_zero,np.min(meanx-stdx)]),np.max([meanx_zero+stdx_zero,np.max(meanx+stdx)])],[meany_zero-stdy_zero,meany_zero-stdy_zero],'k',linestyle=(0,(2,5)),linewidth=0.5)
        elif meanzero_type=='line_inf':
            ax.plot([meanx_zero,meanx_zero],[-500,1000],'k',linewidth=0.5,label='SHAM')
            ax.plot([-500,1000],[meany_zero,meany_zero],'k',linewidth=0.5)
            if flagstdx:
                ax.plot([stdx_zero+meanx_zero,stdx_zero+meanx_zero],[-500,1000],'k',linestyle=(0,(2,5)),linewidth=0.5)
                ax.plot([meanx_zero-stdx_zero,meanx_zero-stdx_zero],[-500,1000],'k',linestyle=(0,(2,5)),linewidth=0.5)
            if flagstdy:
                ax.plot([-500,1000],[stdy_zero+meany_zero,stdy_zero+meany_zero],'k',linestyle=(0,(2,5)),linewidth=0.5)
                ax.plot([-500,1000],[meany_zero-stdy_zero,meany_zero-stdy_zero],'k',linestyle=(0,(2,5)),linewidth=0.5)

        elif meanzero_type=='None':
            print('Not plot of the mean')

        for x,y,sx,sy,n in zip(meanx,meany,stdx,stdy,range(data_length)):
            #Multiple values (Matrix data)
            if len(labels)>1:
                if colormap=='direct':
                    ax.plot(x,y,marker=marker,color=cmap(n),markersize=6,label=labels[n])
                    if flagstdx:
                        ax.plot([x-sx,x+sx],[y,y],':',color=cmap(n),linewidth=0.5)
                    if flagstdy:
                        ax.plot([x,x],[y-sy,y+sy],':',color=cmap(n),linewidth=0.5)
                else:
                    ax.plot(x,y,marker=marker,color=cmap(1.0-n*cmap_scale),markersize=6,label=labels[n]) 
                    if flagstdx:
                        ax.plot([x-sx,x+sx],[y,y],':',color=cmap(0.8),linewidth=0.5)
                    if flagstdy:
                        ax.plot([x,x],[y-sy,y+sy],':',color=cmap(0.6),linewidth=0.5)
            else:
                #Single value (array data; shape=(N,1))
                ax.plot(x,y,marker=marker,color=cmap,markersize=6,label=labels[0])
                if flagstdx:
                    ax.plot([x-sx,x+sx],[y,y],':',color=cmap,linewidth=0.5)
                if flagstdy:
                    ax.plot([x,x],[y-sy,y+sy],':',color=cmap,linewidth=0.5)
    else:
        print("Error in the length of data,len(datax) should be equal to len(datay)")
    return ax