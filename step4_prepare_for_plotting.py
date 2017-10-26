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

ensemble=open('ensemble.txt','w')
for scenario in gmt_.scenario:
	ensemble.write(scenario+':\n')
	for model in sorted(gmt_.model):
		if np.isfinite(np.nanmean(gmt_['had4',scenario,model,'gmt',:])):
			ensemble.write(model+'\t')
	ensemble.write('\n')
ensemble.close()

# anomaly to preindustrial
gmt=da.DimArray(axes=[['rcp26','rcp45','rcp85'],models,['bm_pre','bm_ar5','tas_ar5','tas_pre','b_pre','b_ar5'],np.array(gmt_['had4','rcp85','HadGEM2-ES','time',:])],dims=['scenario','model','style','time'])

for style in gmt.style:
	for scenario in gmt.scenario:
		for model in gmt.model:
			# anomalies to preindustrial
			gmt[scenario,model,'tas_pre',:]=np.array(gmt_['xax',scenario,model,'air',:])-np.nanmean(gmt_['xax',scenario,model,'air',:].ix[0:240])
			gmt[scenario,model,'bm_pre',:]=np.array(gmt_['had4',scenario,model,'gmt',:])-np.nanmean(gmt_['had4',scenario,model,'gmt',:].ix[0:240])
			gmt[scenario,model,'b_pre',:]=np.array(gmt_['xax',scenario,model,'gmt',:])-np.nanmean(gmt_['xax',scenario,model,'gmt',:].ix[0:240])

			# anomalies as in AR5
			gmt[scenario,model,'tas_ar5',:]=np.array(gmt_['xax',scenario,model,'air',:])-np.nanmean(gmt_['xax',scenario,model,'air',:].ix[125*12:145*12])+0.61
			gmt[scenario,model,'bm_ar5',:]=np.array(gmt_['had4',scenario,model,'gmt',:])-np.nanmean(gmt_['had4',scenario,model,'gmt',:].ix[125*12:145*12])+0.61
			gmt[scenario,model,'b_ar5',:]=np.array(gmt_['xax',scenario,model,'gmt',:])-np.nanmean(gmt_['xax',scenario,model,'gmt',:].ix[125*12:145*12])+0.61

ref_years=gmt.time[(gmt.time>1986) & (gmt.time<2006)]
print 'warming in 1986-2006: ',np.nanmean(had4_gmt[125*12:145*12])
print 'tas: ',np.nanmean(gmt[scenario,:,'tas_pre',ref_years])
print 'bm: ',np.nanmean(gmt[scenario,:,'bm_pre',ref_years])
print 'b: ',np.nanmean(gmt[scenario,:,'b_pre',ref_years])


# quatntile stuff
styles=['tas_pre','tas_ar5','bm_pre','bm_ar5','b_pre','b_ar5']
gmt_qu=da.DimArray(axes=[['rcp26','rcp45','rcp85'],styles,styles,[1,1.5,2,2.5],[0,5,10,16.6,25,50,75,83.3,90,95,100]],dims=['scenario','x','y','level','out'])

for scenario in ['rcp85']:
	for level in gmt_qu.level:
		for x_method in styles:
			plt.clf()

			fig,axes=plt.subplots(nrows=2,ncols=4,figsize=(12,8))
			ax=axes.flatten()
			for y_method,pp in zip(styles,range(7)):
				x_=np.asarray(gmt[scenario,:,x_method,:]).reshape(47*2880)
				y_=np.asarray(gmt[scenario,:,y_method,:]).reshape(47*2880)
				idx = np.isfinite(x_) & np.isfinite(y_)
				x,y=x_[idx],y_[idx]

				tmp=np.where((y>level-0.05) & (y<level+0.05))
				y_15=y[tmp]
				x_15=x[tmp]

				for qu in gmt_qu.out:
					gmt_qu[scenario,x_method,y_method,level,qu]=np.nanpercentile(x_15,qu)

				ax[pp].plot(x,y,marker='v',color='blue',linestyle='',alpha=0.02)
				ax[pp].plot(x_15,y_15,marker='v',color='green',linestyle='',alpha=0.4)

				ax[pp].plot([gmt_qu[scenario,x_method,y_method,level,0],gmt_qu[scenario,x_method,y_method,level,100]],[0.65,0.65],color='green')
				ax[pp].fill_between([gmt_qu[scenario,x_method,y_method,level,25],gmt_qu[scenario,x_method,y_method,level,75]],[0.63,0.63],[0.67,0.67],color='green')
				ax[pp].plot([gmt_qu[scenario,x_method,y_method,level,50],gmt_qu[scenario,x_method,y_method,level,50]],[0,1.5],color='green')
				y50=gmt_qu[scenario,x_method,y_method,level,50]
				ax[pp].text(y50,0.9,str(round(y50,3)),rotation=90,verticalalignment='center',horizontalalignment='center',backgroundcolor='white',color='green')

				ax[pp].set_xlim((0.61,2.5))
				ax[pp].set_ylim((0.61,2.5))
				ax[pp].set_xlabel(x_method.replace('_',' '))
				ax[pp].set_ylabel(y_method.replace('_',' '))
				ax[pp].plot([0,5],[0,5],'k--')
				ax[pp].legend(loc='upper left')

			plt.savefig('plots/details/quantiles_'+x_method+'_'+str(level)+'.png')

# conversion table
conversion_table=open('conversion_table.txt','w')
conversion_table.write('\t'.join([' ']+['tas_ar5','tas_pre','bm_pre','bm_ar5']))
for x_method in ['tas_ar5','tas_pre','bm_pre','bm_ar5']:
	conversion_table.write('\n'+x_method+'\t')
	for y_method in ['tas_ar5','tas_pre','bm_pre','bm_ar5']:
		conversion_table.write(str(round(gmt_qu[scenario,x_method,y_method,1.5,50],2))+'\t')
conversion_table.close()

# conversion table precise
conversion_table=open('conversion_table_precise.txt','w')
conversion_table.write('\t'.join([' ']+['tas_ar5','tas_pre','bm_pre','bm_ar5']))
for x_method in ['tas_ar5','tas_pre','bm_pre','bm_ar5']:
	conversion_table.write('\n'+x_method+'\t')
	for y_method in ['tas_ar5','tas_pre','bm_pre','bm_ar5']:
		conversion_table.write(str(round(gmt_qu[scenario,x_method,y_method,1.5,50],4))+'\t')
conversion_table.close()

# conversion table full
conversion_table=open('conversion_table_SI.txt','w')
conversion_table.write('\t'.join([' ']+styles))
for x_method in ['tas_ar5','tas_pre','bm_pre','bm_ar5','b_pre','b_ar5']:
	conversion_table.write('\n'+x_method+'\t')
	for y_method in ['tas_ar5','tas_pre','bm_pre','bm_ar5','b_pre','b_ar5']:
		if y_method==x_method:
			conversion_table.write(str(round(gmt_qu[scenario,x_method,y_method,1.5,50],2))+'\t')
		else:
			conversion_table.write(str(round(gmt_qu[scenario,x_method,y_method,1.5,50],2))+' ('+str(round(gmt_qu[scenario,x_method,y_method,1.5,25],2))+'-'+str(round(gmt_qu[scenario,x_method,y_method,1.5,75],2))+')\t')
conversion_table.close()


ds=da.Dataset({'gmt':gmt})
ds.write_nc('data/gmt_plot_ready.nc', mode='w')

ds=da.Dataset({'gmt_qu':gmt_qu})
ds.write_nc('data/gmt_quantiles.nc', mode='w')
