import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import pandas as pd
import seaborn as sns
import itertools
import matplotlib

try:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/gmt/')
except:
	os.chdir('/p/projects/tumble/carls/shared_folder/gmt/')

gmt=da.read_nc('data/gmt_all.nc')['gmt']


for style,var,title in zip(['xax','xax'],['air','gmt'],['SAT unmasked','Blended air/sea temperature, unmasked, temperature anomalies, variable ice']):
    ngood=0
    ntot=0
    plt.close()
    fig,ax=plt.subplots(nrows=2,ncols=2,figsize=(9,11))
    l_styles = ['-','--','-.',':']
    m_styles = ['','.','o','^','*']
    colormap = matplotlib.cm.get_cmap('Spectral')
    colormap = [colormap(i/float(len(gmt.model_run)/7)) for i in range(len(gmt.model_run)/7)]

    for model_run,(marker,linestyle,color) in zip(sorted(gmt.model_run),itertools.product(m_styles,l_styles, colormap)):
        if np.isfinite(np.nanmean(gmt['xax','rcp85',model_run,'gmt',:].values)):
            tmp=pd.read_table('blend-results.160518/rcp85-xax/rcp85_'+model_run+'.temp',sep=' ',header=None)
            tmp.columns=['time','air','gmt','diff']
            perc_diff=(gmt[style,'rcp85',model_run,var,1861:2100].values-np.array(tmp[var]))
            if np.nanmean(np.abs(perc_diff))<0.001:
                ax[0,0].plot(np.array(tmp['time']),perc_diff,color=color, linestyle=linestyle,marker=marker,label=model_run)
                ax[0,1].plot(range(3),color=color, linestyle=linestyle,marker=marker,label=model_run)
                ngood+=1
            else:
                ax[1,0].plot(np.array(tmp['time']),perc_diff,color=color, linestyle=linestyle,marker=marker,label=model_run)
                ax[1,1].plot(range(3),color=color, linestyle=linestyle,marker=marker,label=model_run)
            ntot+=1

    ax[0,0].set_ylim((-0.01,0.01))
    ax[0,0].set_ylabel('deviation from Cowtan2015')
    ax[0,1].axis('off')
    ax[0,1].set_ylim((-99,-98))
    ax[0,1].legend(loc='upper left',ncol=2,fontsize=8)
    ax[0,1].set_title(('mean deviation < 0.001'))

    ax[1,0].set_ylim((-1,1))
    ax[1,0].set_ylabel('deviation from Cowtan2015')
    ax[1,1].axis('off')
    ax[1,1].set_ylim((-99,-98))
    ax[1,1].legend(loc='upper left',ncol=2,fontsize=8)
    ax[1,1].set_title(('mean deviation > 0.001'))


    plt.suptitle(title)
    plt.savefig('plots/check_'+style+'_'+var+'.png')

    print ngood,ntot


for style,var,title in zip(['had4','had4'],['air','gmt'],['SAT masked','HadCRUT4 emulation']):
    ngood=0
    ntot=0
    plt.close()
    fig,ax=plt.subplots(nrows=2,ncols=2,figsize=(9,11))
    l_styles = ['-','--','-.',':']
    m_styles = ['','.','o','^','*']
    colormap = matplotlib.cm.get_cmap('Spectral')
    colormap = [colormap(i/float(len(gmt.model_run)/7)) for i in range(len(gmt.model_run)/7)]

    for model_run,(marker,linestyle,color) in zip(sorted(gmt.model_run),itertools.product(m_styles,l_styles, colormap)):
        if np.isfinite(np.nanmean(gmt['had4','rcp85',model_run,'gmt',:].values)):
            tmp=pd.read_table('blend-results.160518/rcp85-had4/rcp85_'+model_run+'.temp',sep=' ',header=None)
            tmp.columns=['time','air','gmt','diff']
            perc_diff=(gmt[style,'rcp85',model_run,var,1861:2015].values-np.array(tmp[var]))
            if np.nanmean(np.abs(perc_diff))<0.01:
                ax[0,0].plot(np.array(tmp['time']),perc_diff,color=color, linestyle=linestyle,marker=marker,label=model_run)
                ax[0,1].plot(range(3),color=color, linestyle=linestyle,marker=marker,label=model_run)
                ngood+=1
            else:
                ax[1,0].plot(np.array(tmp['time']),perc_diff,color=color, linestyle=linestyle,marker=marker,label=model_run)
                ax[1,1].plot(range(3),color=color, linestyle=linestyle,marker=marker,label=model_run)
            ntot+=1

    ax[0,0].set_ylim((-0.1,0.1))
    ax[0,0].set_ylabel('deviation from Cowtan2015')
    ax[0,1].axis('off')
    ax[0,1].set_ylim((-99,-98))
    ax[0,1].legend(loc='upper left',ncol=2,fontsize=8)
    ax[0,1].set_title(('mean deviation < 0.01'))

    ax[1,0].set_ylim((-1,1))
    ax[1,0].set_ylabel('deviation from Cowtan2015')
    ax[1,1].axis('off')
    ax[1,1].set_ylim((-99,-98))
    ax[1,1].legend(loc='upper left',ncol=2,fontsize=8)
    ax[1,1].set_title(('mean deviation > 0.01'))

    plt.suptitle(title)
    plt.savefig('plots/check_'+style+'_'+var+'.png')

    print ngood,ntot




for model_run,(marker,linestyle,color) in zip(sorted(gmt.model_run),itertools.product(m_styles,l_styles, colormap)):
    if np.isfinite(np.nanmean(gmt['xax','rcp85',model_run,'gmt',:].values)):
        tmp=pd.read_table('blend-results.160518/rcp85-xax/rcp85_'+model_run+'.temp',sep=' ',header=None)
        tmp.columns=['time','air','gmt','diff']
        perc_diff=(gmt['had4','rcp85',model_run,'air',1861:2100].values-np.array(tmp['air']))
        print model_run,np.nanmean(np.abs(perc_diff))
        print gmt['had4','rcp85',model_run,'air',1861:2100].values
        print np.array(tmp['air'])




#Masked