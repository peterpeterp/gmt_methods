import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import itertools
import matplotlib
import seaborn as sns

def running_mean_func(xx,N):
	if N==1:
		return xx
	if N!=1:
	    x=np.ma.masked_invalid(xx.copy())
	    ru_mean=x.copy()*np.nan
	    for t in range(int(N/2),len(x)-int(N/2)):
	        ru_mean[t]=np.nanmean(x[t-int(N/2):t+int(N/2)])
	    return ru_mean


gmt=da.read_nc('data/gmt_plot_ready.nc')['gmt']
gmt_qu=da.read_nc('data/gmt_quantiles.nc')['gmt_qu']

time_ax=da.DimArray(axes=[np.array(gmt.time)],dims=['time'])
time_ax[:]=gmt.time

dat=open('data/Had4_gmt.txt','r').read()
had4=[]
for line in dat.split('\n')[::2]:
	for anom in line.split(' ')[2:-1]:
		if anom!='':
			had4.append(float(anom))

# get HadCRUT4 for 1861-2016
had4_gmt_=np.array(had4[11*12:-12])
had4_gmt__=had4_gmt_-np.nanmean(had4_gmt_[125*12:145*12])+0.61
had4_gmt=da.DimArray(axes=[np.array(gmt.time[0:1872])],dims=['time'])
had4_gmt[:]=had4_gmt__

#print np.nanmean(np.array(had4_gmt_-np.nanmean(had4_gmt_[0:240]))[125*12:145*12])

# FIG SI 1
plot_dict={
	'tas_pre':{'l_color':'orange','color':'darkorange','longname':'$\mathregular{GMT_{SAT}}$','pos':0.65,'lsty':'-'},
	'tas_ar5':{'l_color':'xyan','color':'darkcyan','longname':'$\mathregular{GMT_{AR5}}$','pos':0.65,'lsty':'--'},
	'bm_pre':{'l_color':'cornflowerblue','color':sns.color_palette()[0],'longname':'$\mathregular{GMT_{BM\_CMIP5}}$','pos':0.75,'lsty':'-'},
	'bm_ar5':{'l_color':'tomato','color':sns.color_palette()[2],'longname':'$\mathregular{GMT_{BM\_CMIP5\_ref}}$','pos':0.85,'lsty':':'},
}
plt.clf()
fig,axes=plt.subplots(nrows=1,ncols=2,figsize=(10,5))
ax=axes.flatten()

all_hist=time_ax[time_ax<2017]
before_1996=time_ax[time_ax<1996]
after_1996=time_ax[time_ax>1996]
before_1986=time_ax[time_ax<1986]
after_1986=time_ax[(time_ax>1986) & (time_ax<2017)]

ax[0].plot(time_ax[all_hist],running_mean_func(had4_gmt,12),'gray',lw=2,alpha=0.6,label='HadCRUT4')
for method in ['tas_pre','bm_pre']:
	ax[0].plot(time_ax[all_hist],running_mean_func(np.nanmean(gmt['rcp85',:,method,all_hist],axis=0),12),label=plot_dict[method]['longname'],color=plot_dict[method]['color'])
for method in ['tas_ar5','bm_ar5']:
	ax[0].plot(time_ax[before_1996],running_mean_func(had4_gmt[before_1996],12),label=plot_dict[method]['longname'],color=plot_dict[method]['color'],linestyle=plot_dict[method]['lsty'])
	ax[0].plot(time_ax.ix[135*12:1871],running_mean_func(np.nanmean(gmt['rcp85',:,method,:],axis=0)[135*12:1871],12),color=plot_dict[method]['color'],linestyle=plot_dict[method]['lsty'])

ax[0].set_ylim((-0.4,1.3))
ax[0].set_xlim((1861,2014))
ax[0].plot([1996,1996],[-0.4,1.5],color='k')
ax[0].set_ylabel('$\mathregular{GMT}$ $\mathregular{[^\circ C]}$')
ax[0].legend(loc='upper left',fontsize=10)

for method in ['tas_pre','bm_pre']:
	ax[1].plot(time_ax[all_hist],running_mean_func(np.nanmean(gmt['rcp85',:,method,all_hist]-had4_gmt,axis=0),60),label=plot_dict[method]['longname'],color=plot_dict[method]['color'])
for method in ['tas_ar5','bm_ar5']:
	ax[1].plot(time_ax[before_1986],had4_gmt[before_1986]*0,label=plot_dict[method]['longname'],color=plot_dict[method]['color'],linestyle=plot_dict[method]['lsty'])
	ax[1].plot(time_ax.ix[125*12:1872],running_mean_func(np.nanmean(gmt['rcp85',:,method,all_hist]-had4_gmt,axis=0),60)[125*12:1872],color=plot_dict[method]['color'],linestyle=plot_dict[method]['lsty'])

#ax[1].set_ylim((-0.2,0.2))
ax[1].plot([1860,2020],[0,0],color='k')
ax[1].plot([1996,1996],[-0.2,0.2],color='k')
ax[1].set_xlim((1861,2015))
ax[1].set_ylabel('$\mathregular{GMT-GMT_{obs}}$ $\mathregular{[^\circ C]}$')
plt.tight_layout()
plt.savefig('plots/GMT_ref.png')
plt.savefig('plots/GMT_ref.pdf')
