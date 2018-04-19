import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import itertools
import matplotlib
import seaborn as sns; sns.set()

def running_mean_func(xx,N):
	if N==1:
		return xx
	if N!=1:
	    x=np.ma.masked_invalid(xx.copy())
	    ru_mean=x.copy()*np.nan
	    for t in range(int(N/2),len(x)-int(N/2)):
	        ru_mean[t]=np.nanmean(x[t-int(N/2):t+int(N/2)])
	    return ru_mean

gmt=da.read_nc('data/gmt_plot_ready_year_model_1861-1880.nc')['gmt']
gmt_allRuns=da.read_nc('data/gmt_plot_ready_year_runs_1861-1880.nc')['gmt']

time_ax=da.DimArray(axes=[np.array(gmt.time)],dims=['time'])
time_ax[:]=gmt.time

# read HadCRUT4
dat=open('data/HadCRUT4_gmt.txt','r').read()
had4=[]
year=[]
for line in dat.split('\n')[::2]:
	year.append(line.split(' ')[1])
	had4.append(float(line.split(' ')[-1]))
# get HadCRUT4 for 1850-2016
had4_gmt_=np.array(had4[:-1])
had4_gmt=da.DimArray(axes=[np.array(gmt.time)],dims=['time'])
had4_gmt[1850:2016]=had4_gmt_
ref_ar5=gmt.time[(gmt.time>=1986) & (gmt.time<2006)]
had4_gmt[:]=had4_gmt[:]-np.nanmean(had4_gmt[ref_ar5])+0.61
#print np.nanmean(np.array(had4_gmt_-np.nanmean(had4_gmt_[0:240]))[136*12:145*12])

# FIG SI 1
plot_dict={
	'gmt_sat':{'l_color':'orange','color':'darkorange','longname':'$\mathregular{GMT_{SAT}}$','pos':0.65,'lsty':'-'},
	'gmt_ar5':{'l_color':'lawngreen','color':sns.color_palette()[1],'longname':'$\mathregular{GMT_{AR5}}$','pos':0.65,'lsty':'--'},
	'gmt_millar':{'l_color':'cornflowerblue','color':sns.color_palette()[0],'longname':'$\mathregular{GMT_{M17}}$','pos':0.75,'lsty':'-'},
	'gmt_bm':{'l_color':'tomato','color':sns.color_palette()[2],'longname':'$\mathregular{GMT_{blend-mask}}$','pos':0.85,'lsty':'-'},
}
plt.clf()
fig,axes = plt.subplots(nrows=1,ncols=3,figsize=(12,5),gridspec_kw = {'width_ratios':[2,2,1]})
ax=axes.flatten()

ax[0].plot([0,0],alpha=0,label='all models equal')
for method in ['gmt_sat','gmt_bm']:
	ax[0].plot(time_ax,running_mean_func(np.nanmean(gmt['rcp85',:,method,:]-had4_gmt,axis=0),10),label=plot_dict[method]['longname'],color=plot_dict[method]['color'])
ax[0].plot([0,0],alpha=0,label='all runs equal')
for method in ['gmt_sat','gmt_bm']:
	ax[0].plot(time_ax,running_mean_func(np.nanmean(gmt_allRuns['rcp85',:,method,:]-had4_gmt,axis=0),10),label=plot_dict[method]['longname'],color=plot_dict[method]['color'],linestyle='--')

ax[0].plot([1850,2035],[0,0],color='k')
ax[0].set_xlim((1850,2016))
#ax[0].set_ylim((-0.2,0.4))
ax[0].legend(loc='upper left',fontsize=9,ncol=2)
ax[0].text(-0.1, 1.02, 'a', transform=ax[0].transAxes,fontsize=18, fontweight='bold', va='top', ha='right')
ax[0].set_ylabel('$\mathregular{GMT-GMT_{obs}}$ $\mathregular{[^\circ C]}$')

method='gmt_sat'
ens_mean=np.nanmean(gmt['rcp85',:,method,:],axis=0)
colors=sns.hls_palette(len(gmt.model))
single_run={}
multiple_run={}
for model in sorted(gmt.model):
	ensemble=[model_run for model_run in gmt_allRuns.model if model_run.split('_')[0]==model]
	if len(ensemble)>1:
		multiple_run[model]=len(ensemble)
	else:
		single_run[model]=1

for model,color in zip(sorted(multiple_run.keys()),sns.hls_palette(len(multiple_run.keys()))):
	ax[1].plot(time_ax,running_mean_func(gmt['rcp85',model,method,:]-ens_mean,20),linewidth=multiple_run[model],alpha=0.5,color=color,label=str(multiple_run[model])+' '+model)
	ax[2].plot([-99,-9],linewidth=multiple_run[model],alpha=0.5,color=color,label=str(multiple_run[model])+' '+model)

for model,color in zip(sorted(single_run.keys()),sns.hls_palette(len(single_run.keys()))):
	ax[1].plot(time_ax,running_mean_func(gmt['rcp85',model,method,:]-ens_mean,20),linewidth=1,linestyle='--',color=color)
	ax[2].plot([-99,-9],linewidth=1,alpha=0.5,color=color,label=str(1)+' '+model)

ax[1].plot([1850,2035],[0,0],color='k')
ax[1].set_xlim((1850,2016))
ax[1].set_ylim((-0.6,0.6))
ax[1].text(-0.1, 1.02, 'b', transform=ax[1].transAxes,fontsize=18, fontweight='bold', va='top', ha='right')
ax[1].set_ylabel('$\mathregular{GMT_{model-mean}-GMT_{ensemble-mean}}$ $\mathregular{[^\circ C]}$')

ax[2].axis('off')
ax[2].set_ylim((0,1))
ax[2].legend(loc='upper left',fontsize=7,ncol=2)


plt.tight_layout()
plt.savefig('plots/Figure_SI_one_model_one_vote.png',dpi=300)
plt.savefig('plots/Figure_SI_one_model_one_vote.pdf')
