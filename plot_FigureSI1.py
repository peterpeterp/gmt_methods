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

# read HadCRUT4
dat=open('data/HadCRUT4_gmt.txt','r').read()
had4=[]
year=[]
for line in dat.split('\n')[::2]:
	year.append(line.split(' ')[0])
	for anom in line.split(' ')[1:-1]:
		if anom!='':
			had4.append(float(anom))
# get HadCRUT4 for 1850-2016
had4_gmt_=np.array(had4[:-12])
had4_gmt=da.DimArray(axes=[np.array(gmt.time[0:2004])],dims=['time'])
had4_gmt[:]=had4_gmt_
ref_ar5=gmt.time[(gmt.time>1986) & (gmt.time<2006)]
had4_gmt[:]=had4_gmt[:]-np.nanmean(had4_gmt[ref_ar5])+0.61
#print np.nanmean(np.array(had4_gmt_-np.nanmean(had4_gmt_[0:240]))[136*12:145*12])

# FIG SI 1
plot_dict={
	'gmt_sat':{'l_color':'orange','color':'darkorange','longname':'$\mathregular{GMT_{SAT}}$','pos':0.65,'lsty':'-'},
	'gmt_ar5':{'l_color':'xyan','color':'darkcyan','longname':'$\mathregular{GMT_{AR5}}$','pos':0.65,'lsty':'--'},
	'gmt_millar':{'l_color':'cornflowerblue','color':sns.color_palette()[0],'longname':'$\mathregular{GMT_{rebase-2010s}}$','pos':0.75,'lsty':'-'},
	'gmt_bm':{'l_color':'tomato','color':sns.color_palette()[2],'longname':'$\mathregular{GMT_{blend-mask}}$','pos':0.85,'lsty':'-'},
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
for method in ['gmt_sat','gmt_bm']:
	ax[0].plot(time_ax[all_hist],running_mean_func(np.nanmean(gmt['rcp85',:,method,all_hist],axis=0),12),label=plot_dict[method]['longname'],color=plot_dict[method]['color'])
for method in ['gmt_ar5']:
	ax[0].plot(time_ax.ix[146*12:2004],running_mean_func(np.nanmean(gmt['rcp85',:,method,:],axis=0)[146*12:2004],12),color=plot_dict[method]['color'],linestyle=plot_dict[method]['lsty'],label=plot_dict[method]['longname'])
# for method in ['gmt_millar']:
# 	ax[0].plot(time_ax.ix[165*12:2004],running_mean_func(np.nanmean(gmt['rcp85',:,method,:],axis=0)[165*12:2004],12),color=plot_dict[method]['color'],linestyle=plot_dict[method]['lsty'])


ax[0].set_ylim((-0.4,1.3))
ax[0].set_xlim((1850,2016))
#ax[0].plot([1996,1996],[-0.4,1.5],color='k')
ax[0].set_ylabel('$\mathregular{GMT}$ $\mathregular{[^\circ C]}$')
ax[0].legend(loc='upper left',fontsize=10)

for method in ['gmt_sat','gmt_bm']:
	ax[1].plot(time_ax[all_hist],running_mean_func(np.nanmean(gmt['rcp85',:,method,all_hist]-had4_gmt,axis=0),60),label=plot_dict[method]['longname'],color=plot_dict[method]['color'])
for method in ['gmt_ar5']:
	ax[1].plot(time_ax.ix[136*12:2004],running_mean_func(np.nanmean(gmt['rcp85',:,method,all_hist]-had4_gmt,axis=0),60)[136*12:2004],color=plot_dict[method]['color'],linestyle=plot_dict[method]['lsty'],label=plot_dict[method]['longname'])
# for method in ['gmt_millar']:
# 	ax[1].plot(time_ax.ix[160*12:2004],running_mean_func(np.nanmean(gmt['rcp85',:,method,all_hist]-had4_gmt,axis=0),60)[160*12:2004],color=plot_dict[method]['color'],linestyle=plot_dict[method]['lsty'])

#ax[1].set_ylim((-0.2,0.2))
ax[1].plot([1860,2020],[0,0],color='k')
#ax[1].plot([1996,1996],[-0.2,0.2],color='k')
ax[1].set_xlim((1850,2016))
ax[1].set_ylabel('$\mathregular{GMT-GMT_{obs}}$ $\mathregular{[^\circ C]}$')
plt.tight_layout()
plt.savefig('plots/GMT_ref.png')
plt.savefig('plots/GMT_ref.pdf')
