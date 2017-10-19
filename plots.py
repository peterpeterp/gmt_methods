import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import itertools
import matplotlib
from scipy import stats

def running_mean_func(xx,N):
	if N==1:
		return xx
	if N!=1:
	    x=np.ma.masked_invalid(xx.copy())
	    ru_mean=x.copy()*np.nan
	    for t in range(int(N/2),len(x)-int(N/2)):
	        ru_mean[t]=np.nanmean(x[t-int(N/2):t+int(N/2)])
	    return ru_mean


gmt_all=da.read_nc('data/gmt.nc')['gmt']

models=list(gmt_all.model)
models.remove('CESM1-CAM5')
models.remove('MIROC5')
models.remove('BNU-ESM')
models.remove('bcc-csm1-1-m')

gmt_=gmt_all[gmt_all.style,gmt_all.scenario,models,gmt_all.variable,gmt_all.time]

ensemble=open('ensemble.txt','w')
for scenario in gmt.scenario:
	ensemble.write(scenario+':\n')
	for model in sorted(gmt.model):
		if np.isfinite(np.nanmean(gmt_['had4',scenario,model,'gmt',:])):
			ensemble.write(model+'\t')
	ensemble.write('\n')
ensemble.close()

gmt=da.DimArray(axes=[['rcp26','rcp45','rcp85'],models,['had4','had4_ar5','tas_ar5','tas','time'],np.arange(0,2880)],dims=['scenario','model','style','time'])

dat=open('data/Had4_gmt.txt','r').read()
had4=[]
for line in dat.split('\n')[::2]:
	for anom in line.split(' ')[2:-1]:
		if anom!='':
			had4.append(float(anom))

had4_gmt=np.array(had4[11*12:-12])
had4_gmt-=np.nanmean(had4_gmt[0:240])
had4_time=gmt_['had4','rcp85','HadGEM2-ES','time',0:1871]

# anomaly to preindustrial
for style in gmt.style:
	for scenario in gmt.scenario:
		for model in gmt.model:
			gmt[scenario,model,'tas',:]=np.array(gmt_['xax',scenario,model,'air',:])-np.nanmean(gmt_['xax',scenario,model,'air',0:240])
			gmt[scenario,model,'tas_ar5',:]=np.array(gmt[scenario,model,'tas',:])-np.nanmean(gmt[scenario,model,'tas',125*12:145*12])+np.nanmean(had4_gmt[125*12:145*12])
			#print list(gmt[scenario,model,'ar5',:])[125*12:145*12]
			gmt[scenario,model,'had4',:]=np.array(gmt_['had4',scenario,model,'gmt',:])-np.nanmean(gmt_['had4',scenario,model,'gmt',0:240])
			gmt[scenario,model,'had4_ar5',:]=np.array(gmt_['had4',scenario,model,'gmt',:])-np.nanmean(gmt_['had4',scenario,model,'gmt',125*12:145*12])+np.nanmean(had4_gmt[125*12:145*12])
			gmt[scenario,model,'time',:]=gmt_['had4',scenario,model,'time',:]

			#print np.nanmean(had4_gmt[125*12:145*12]),np.nanmean(gmt[scenario,model,'tas',125*12:145*12]),np.nanmean(gmt[scenario,model,'tas_ar5',125*12:145*12]),np.nanmean(gmt[scenario,model,'had4',125*12:145*12]),np.nanmean(gmt[scenario,model,'had4_ar5',125*12:145*12])

print np.nanmean(had4_gmt[125*12:145*12]),np.nanmean(gmt[scenario,:,'tas',125*12:145*12]),np.nanmean(gmt[scenario,:,'tas_ar5',125*12:145*12]),np.nanmean(gmt[scenario,:,'had4',125*12:145*12]),np.nanmean(gmt[scenario,:,'had4_ar5',125*12:145*12])


plt.clf()
fig,axes=plt.subplots(nrows=1,ncols=2,figsize=(12,6))
ax=axes.flatten()
year=gmt['rcp85','HadGEM2-ES','time',0:1871]

ax[0].plot(gmt['rcp85','HadGEM2-ES','time',0:1871],running_mean_func(had4_gmt,12),'gray',lw=2,alpha=0.6,label='HadCRUT4')
ax[0].plot(year,running_mean_func(np.nanmean(gmt['rcp85',:,'tas',0:1871],axis=0),12),label='SAT anomalies to preindustrial',color='darkorange')
ax[0].plot(year,running_mean_func(np.nanmean(gmt['rcp85',:,'tas_ar5',0:1871],axis=0),12),label='SAT anomalies as in AR5',color='darkblue')
ax[0].plot(year,running_mean_func(np.nanmean(gmt['rcp85',:,'had4',0:1871],axis=0),12),label='HadCRUT4 method anomalies to preindustrial',color='darkcyan')
ax[0].plot(year,running_mean_func(np.nanmean(gmt['rcp85',:,'had4_ar5',0:1871],axis=0),12),label='HadCRUT4 method anomalies as in AR5',color='darkmagenta')
ax[0].set_ylim((-0.4,1.3))
ax[0].set_xlim((1861,2014))
ax[0].plot([1996,1996],[-0.4,1.5],color='k')
ax[0].set_ylabel('$\Delta T~[^\circ]$')
ax[0].legend(loc='upper left',fontsize=10)

ax[1].plot(year,running_mean_func(np.nanmean(gmt['rcp85',:,'tas',0:1871],axis=0)-had4_gmt,240),label='SAT anomalies to preindustrial',color='darkorange')
ax[1].plot(year,running_mean_func(np.nanmean(gmt['rcp85',:,'tas_ar5',0:1871],axis=0)-had4_gmt,240),label='SAT anomalies as in AR5',color='darkblue')
ax[1].plot(year,running_mean_func(np.nanmean(gmt['rcp85',:,'had4',0:1871],axis=0)-had4_gmt,240),label='HadCRUT4 method anomalies to preindustrial',color='darkcyan')
ax[1].plot(year,running_mean_func(np.nanmean(gmt['rcp85',:,'had4_ar5',0:1871],axis=0)-had4_gmt,240),label='HadCRUT4 method anomalies as in AR5',color='darkmagenta')
ax[1].set_ylim((-0.2,0.2))
ax[1].plot([1860,2020],[0,0],color='k')
ax[1].plot([1996,1996],[-0.2,0.2],color='k')
ax[1].set_xlim((1861,2015))
ax[1].set_ylabel('$\Delta T-\Delta T_{observed}~[^\circ]$')
plt.tight_layout()
plt.savefig('plots/GMT_ref.png')
plt.savefig('plots/GMT_ref.pdf')

# FIG 1
for scenario in gmt.scenario:
	plt.clf()
	fig,axes=plt.subplots(nrows=1,ncols=2,figsize=(12,6))
	ax=axes.flatten()

	ax[0].grid(color='gray', linestyle='-', linewidth=1)
	x=np.arange(0,5)
	# for model in gmt.model:
	# 	ax[0].scatter(gmt[scenario,model,'tas_ar5',:],gmt[scenario,model,'tas',:],color='orange',marker='1',alpha=0.2)
	# lr=stats.linregress(np.nanmean(gmt['rcp85',:,'tas_ar5',:],axis=0),np.nanmean(gmt['rcp85',:,'tas',:],axis=0))
	# ax[0].plot(x,lr[1]+x*lr[0],color='darkorange',lw=2,label='SAT anomalies to preindustrial\n$\Delta T_{alt}='+str(round(lr[0],3))+'\Delta T_{tas}+'+str(round(lr[1],3))+'$')
	#
	# y=(1.5-lr[1])/lr[0]
	# ax[0].plot([y,y],[0,1.5],color='darkorange',lw=2)
	# ax[0].text(y,0.8,str(round(y,3)),rotation=90,verticalalignment='center',horizontalalignment='center',backgroundcolor='white',color='darkorange')

	for model in gmt.model:
		ax[0].scatter(gmt[scenario,model,'tas_ar5',:],gmt[scenario,model,'had4',:],color='cyan',marker='1',alpha=0.2)
	lr=stats.linregress(np.nanmean(gmt['rcp85',:,'tas_ar5',:],axis=0),np.nanmean(gmt['rcp85',:,'had4',:],axis=0))
	ax[0].plot(x,lr[1]+x*lr[0],color='darkcyan',lw=2,label='HadCRUT4 method anomalies to preindustrial\n$\Delta T_{alt}='+str(round(lr[0],3))+'*\Delta T_{tas}'+['-','+'][int((np.sign(lr[1])+1)/2)]+str(round(lr[1],3))+'$')

	y=(1.5-lr[1])/lr[0]
	ax[0].plot([y,y],[0,1.5],color='darkcyan',lw=2)
	ax[0].text(y,0.8,str(round(y,3)),rotation=90,verticalalignment='center',horizontalalignment='center',backgroundcolor='white',color='darkcyan')

	for model in gmt.model:
		ax[0].scatter(gmt[scenario,model,'tas_ar5',:],gmt[scenario,model,'had4_ar5',:],color='magenta',marker='2',alpha=0.2)
	lr=stats.linregress(np.nanmean(gmt['rcp85',:,'tas_ar5',:],axis=0),np.nanmean(gmt['rcp85',:,'had4_ar5',:],axis=0))
	ax[0].plot(x,lr[1]+x*lr[0],color='darkmagenta',lw=2,label='HadCRUT4 method anomalies as in AR5\n$\Delta T_{alt}='+str(round(lr[0],3))+'*\Delta T_{tas}'+['-','+'][int((np.sign(lr[1])+1)/2)]+str(round(lr[1],3))+'$')

	y=(1.5-lr[1])/lr[0]
	ax[0].plot([y,y],[0,1.5],color='darkmagenta',lw=2)
	ax[0].text(y,0.8,str(round(y,3)),rotation=90,verticalalignment='center',horizontalalignment='center',backgroundcolor='white',color='darkmagenta')

	ax[0].plot([-1,5],[-1,5],linestyle='--',color='k')
	ax[0].plot([-1,5],[1.5,1.5],linestyle='--',color='k')
	ax[0].set_ylim((0.61,2.5))
	ax[0].set_xlim((0.61,2.5))

	ax[0].set_xlabel('$\Delta T_{tas}~[^\circ C]$')
	ax[0].set_ylabel('$\Delta T_{alternative}~[^\circ C]$')
	ax[0].legend(loc='upper left',fontsize=10)

	ax[1].grid(color='gray', linestyle='-', linewidth=1)
	x=np.arange(0,5)
	for model in gmt.model:
		ax[1].scatter(gmt[scenario,model,'tas_ar5',:],gmt[scenario,model,'had4',:]-gmt[scenario,model,'tas_ar5',:],color='cyan',marker='1',alpha=0.2)
	lr=stats.linregress(np.nanmean(gmt['rcp85',:,'tas_ar5',:],axis=0),np.nanmean(gmt['rcp85',:,'had4',:],axis=0))
	ax[1].plot(x,lr[1]+x*lr[0]-x,color='darkcyan',lw=2,label='HadCRUT4 method anomalies to preindustrial')

	for model in gmt.model:
		ax[1].scatter(gmt[scenario,model,'tas_ar5',:],gmt[scenario,model,'had4_ar5',:]-gmt[scenario,model,'tas_ar5',:],color='magenta',marker='2',alpha=0.2)
	lr=stats.linregress(np.nanmean(gmt['rcp85',:,'tas_ar5',:],axis=0),np.nanmean(gmt['rcp85',:,'had4_ar5',:],axis=0))
	ax[1].plot(x,lr[1]+x*lr[0]-x,color='darkmagenta',lw=2,label='HadCRUT4 method anomalies as in AR5')

	ax[1].plot([-1,5],[0,0],linestyle='-',color='k',lw=2)
	#ax[1].plot([-1,5],[1.5,1.5],linestyle='--',color='k')
	ax[1].set_ylim((-0.5,0.5))
	ax[1].set_xlim((0.61,2.5))

	ax[1].set_xlabel('$\Delta T_{tas}~[^\circ C]$')
	ax[1].set_ylabel('$\Delta T_{alternative} -\Delta T_{tas}~[^\circ C]$')
	#ax[1].legend(loc='upper left')

	plt.tight_layout()
	plt.savefig('plots/FIG1_'+scenario+'.png')
	plt.savefig('plots/FIG1_'+scenario+'.pdf')











#
# binned_gmt=da.DimArray(axes=[['rcp26','rcp45','rcp85'],['tas','had4','ar5'],[0,10,25,33,50,66,75,90,100],range(800)],dims=['scenario','variable','quantile','bins'])
#
# for scenario in gmt.scenario:
# 	for air,i in zip(np.arange(0.,4.,0.005),range(800)):
# 		binned_had4=[]
# 		for model in gmt.model:
# 			tmp=gmt[scenario,model,:,:]
# 			binned_had4+=list(tmp['had4_ar5',np.where((tmp['tas_ar5',:]>=air) & (tmp['tas_ar5',:]<air+0.05))[0]])
# 		binned_gmt[scenario,'tas',0,i]=air+0.025
# 		for qu in binned_gmt.quantile:
# 			binned_gmt[scenario,'had4',qu,i]=np.nanpercentile(np.array(binned_had4),qu)
#
