import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import itertools
import matplotlib
from scipy import stats
import seaborn as sns
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import summary_table
from statsmodels.sandbox.regression.predstd import wls_prediction_std

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

dat=open('data/Had4_gmt.txt','r').read()
had4=[]
for line in dat.split('\n')[::2]:
	for anom in line.split(' ')[2:-1]:
		if anom!='':
			had4.append(float(anom))

# get HadCRUT4 for 1861-2016
had4_gmt_=np.array(had4[11*12:-12])
had4_gmt=had4_gmt_-np.nanmean(had4_gmt_[125*12:145*12])+0.61
had4_time=gmt_['had4','rcp85','HadGEM2-ES','time',0:1871]

scenario='rcp85'
gmt_millar=da.DimArray(axes=[models,np.arange(2006,2040,1),np.array(gmt_['had4','rcp85','HadGEM2-ES','time',:])],dims=['model','rebase_year','time'])
time_ax=da.DimArray(axes=[np.array(gmt_['had4','rcp85','HadGEM2-ES','time',:])],dims=['time'])
time_ax[:]=gmt_['had4','rcp85','HadGEM2-ES','time',:]

gmt=da.read_nc('data/gmt_plot_ready.nc')['gmt']

for model in gmt_.model:
	for year in gmt_millar.rebase_year:
		years=gmt_millar.time[(gmt_millar.time>year-2) & (gmt_millar.time<year+3)]
		gmt_millar[model,year,:]=gmt[scenario,model,'tas_ar5',:]
		gmt_millar[model,year,:]-=np.nanmean(gmt[scenario,model,'tas_ar5',years])
		gmt_millar[model,year,:]+=np.nanmean(gmt[scenario,model,'bm_ar5',years])


plt.clf()
for year,cl in zip(range(2006,2032,5),range(5)):
	years=gmt_millar.time[gmt_millar.time>year]
	plt.plot(time_ax[years],running_mean_func(np.nanmean(gmt_millar[:,year,years],axis=0),12),color=sns.dark_palette("purple")[cl],alpha=0.7,label=str(year+1861))
plt.plot(time_ax,running_mean_func(np.nanmean(gmt[scenario,:,'tas_ar5',:],axis=0),12),color='darkcyan')
plt.plot(time_ax,running_mean_func(np.nanmean(gmt[scenario,:,'bm_ar5',:],axis=0),12),color=sns.color_palette()[2])
plt.xlim((2006,2035))
plt.ylim((0.9,1.6))
plt.legend(loc='upper left')
plt.savefig('plots/test.png')


# quantile stuff
millar_qu=da.DimArray(axes=[gmt_millar.rebase_year,[1,1.5,2,2.5],[0,5,10,16.6,25,50,75,83.3,90,95,100]],dims=['rebase_year','level','out'])

for level in millar_qu.level:
	for year in gmt_millar.rebase_year:
		x_=np.asarray(gmt[scenario,:,'tas_ar5',:]).reshape(47*2880)
		y_=np.asarray(gmt_millar[:,year,:]).reshape(47*2880)
		idx = np.isfinite(x_) & np.isfinite(y_)
		x,y=x_[idx],y_[idx]

		tmp=np.where((y>level-0.05) & (y<level+0.05))
		y_15=y[tmp]
		x_15=x[tmp]

		for qu in millar_qu.out:
			millar_qu[year,level,qu]=np.nanpercentile(x_15,qu)

# conversion table
conversion_table=open('conversion_table_millar.txt','w')
for year in range(2006,2032,5):
	conversion_table.write(str(year)+'\t')
conversion_table.write('\n')
for year in range(2006,2032,5):
	conversion_table.write(str(round(millar_qu[year,1.5,50],2))+'\t')
conversion_table.close()
#asdas
