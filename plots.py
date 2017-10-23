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

gmt=da.DimArray(axes=[['rcp26','rcp45','rcp85'],models,['bm_pre','bm_ar5','tas_ar5','tas_pre','b_pre','b_ar5','time'],np.arange(0,2880)],dims=['scenario','model','style','time'])

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
			# anomalies to preindustrial
			gmt[scenario,model,'tas_pre',:]=np.array(gmt_['xax',scenario,model,'air',:])-np.nanmean(gmt_['xax',scenario,model,'air',0:240])
			gmt[scenario,model,'bm_pre',:]=np.array(gmt_['had4',scenario,model,'gmt',:])-np.nanmean(gmt_['had4',scenario,model,'gmt',0:240])
			gmt[scenario,model,'b_pre',:]=np.array(gmt_['xax',scenario,model,'gmt',:])-np.nanmean(gmt_['xax',scenario,model,'gmt',0:240])

			# anomalies as in AR5
			gmt[scenario,model,'tas_ar5',:]=np.array(gmt_['xax',scenario,model,'air',:])-np.nanmean(gmt_['xax',scenario,model,'air',125*12:145*12])+np.nanmean(had4_gmt[125*12:145*12])
			gmt[scenario,model,'bm_ar5',:]=np.array(gmt_['had4',scenario,model,'gmt',:])-np.nanmean(gmt_['had4',scenario,model,'gmt',125*12:145*12])+np.nanmean(had4_gmt[125*12:145*12])
			gmt[scenario,model,'b_ar5',:]=np.array(gmt_['xax',scenario,model,'gmt',:])-np.nanmean(gmt_['xax',scenario,model,'gmt',125*12:145*12])+np.nanmean(had4_gmt[125*12:145*12])

			# add time
			gmt[scenario,model,'time',:]=gmt_['had4',scenario,model,'time',:]


print 'warming in 1986-2006: ',np.nanmean(had4_gmt[125*12:145*12])
print 'tas: ',np.nanmean(gmt[scenario,:,'tas_pre',125*12:145*12])
print 'bm: ',np.nanmean(gmt[scenario,:,'bm_pre',125*12:145*12])
print 'b: ',np.nanmean(gmt[scenario,:,'b_pre',125*12:145*12])

plot_dict={
	'tas_pre':{'l_color':'orange','color':'darkorange','longname':'SAT anomalies\nto preindustrial'},
	'bm_pre':{'l_color':'tomato','color':sns.color_palette()[2],'longname':'HadCRUT4 method\n anomalies to preindustrial'},
	'bm_ar5':{'l_color':'cornflowerblue','color':sns.color_palette()[0],'longname':'HadCRUT4 method\n anomalies as in AR5'},
}

# FIG 1
for scenario in ['rcp85']:
	plt.clf()
	fig,axes=plt.subplots(nrows=1,ncols=2,figsize=(12,6))
	ax=axes.flatten()

	x__=np.arange(0,5,0.01)

	for method in ['tas_pre','bm_ar5','bm_pre']:
		x_=np.asarray(gmt[scenario,:,'tas_ar5',:]).reshape(47*2880)
		y_=np.asarray(gmt[scenario,:,method,:]).reshape(47*2880)
		idx = np.isfinite(x_) & np.isfinite(y_)
		x,y=x_[idx],y_[idx]
		ax[0].scatter(x,y,color=plot_dict[method]['l_color'],marker='1',alpha=0.2)

		lr=stats.linregress(x,y)
		ax[0].plot(x__,lr[1]+x__*lr[0],color=plot_dict[method]['color'],lw=2)


		ax[0].plot([-99,-99],[-99,-99],color=plot_dict[method]['color'],lw=2,label=plot_dict[method]['longname']+'\n$\Delta T_{alt}='+str(round(lr[0],3))+'*\Delta T_{tas}'+['-','+'][int((np.sign(lr[1])+1)/2)]+str(round(abs(lr[1]),3))+'$')

		y=(1.5-lr[1])/lr[0]
		ax[0].plot([y,y],[0,1.5],color=plot_dict[method]['color'],lw=2)
		ax[0].text(y,0.8,str(round(y,3)),rotation=90,verticalalignment='center',horizontalalignment='center',backgroundcolor='white',color=plot_dict[method]['color'])

	ax[0].plot([-1,5],[-1,5],linestyle='--',color='k')
	ax[0].plot([-1,5],[1.5,1.5],linestyle='--',color='k')
	ax[0].set_ylim((0.61,2.5))
	ax[0].set_xlim((0.61,2.5))

	ax[0].set_xlabel('$\Delta T_{tas}~[^\circ C]$')
	ax[0].set_ylabel('$\Delta T_{alt}~[^\circ C]$')
	ax[0].legend(loc='upper left',fontsize=12)

	for method in ['bm_ar5','bm_pre']:
		x_=np.asarray(gmt[scenario,:,'tas_ar5',:]).reshape(47*2880)
		y_=np.asarray(gmt[scenario,:,method,:]).reshape(47*2880)
		idx = np.isfinite(x_) & np.isfinite(y_)
		x,y=x_[idx],y_[idx]

		ax[1].scatter(x,y-x,color=plot_dict[method]['l_color'],marker='1',alpha=0.2)

		lr=stats.linregress(x,y)
		ax[1].plot(x__,lr[1]+x__*lr[0]-x__,color=plot_dict[method]['color'],lw=2)

	ax[1].plot([-1,5],[0,0],linestyle='-',color='k',lw=2)
	ax[1].set_ylim((-0.5,0.5))
	ax[1].set_xlim((0.61,2.5))

	ax[1].set_xlabel('$\Delta T_{tas}~[^\circ C]$')
	ax[1].set_ylabel('$\Delta T_{alt} -\Delta T_{tas}~[^\circ C]$')

	plt.tight_layout()
	plt.savefig('plots/FIG1_'+scenario+'.png')
	plt.savefig('plots/FIG1_'+scenario+'.pdf')



# FIG SI 1
plt.clf()
fig,axes=plt.subplots(nrows=1,ncols=2,figsize=(12,6))
ax=axes.flatten()
year=gmt['rcp85','HadGEM2-ES','time',0:1871]

ax[0].plot(gmt['rcp85','HadGEM2-ES','time',0:1871],running_mean_func(had4_gmt,12),'gray',lw=2,alpha=0.6,label='HadCRUT4')
ax[0].plot(year,running_mean_func(np.nanmean(gmt['rcp85',:,'tas_pre',0:1871],axis=0),12),label='SAT anomalies to preindustrial',color='darkorange')
ax[0].plot(year,running_mean_func(np.nanmean(gmt['rcp85',:,'tas_ar5',0:1871],axis=0),12),label='SAT anomalies as in AR5',color='darkblue')
ax[0].plot(year,running_mean_func(np.nanmean(gmt['rcp85',:,'bm_pre',0:1871],axis=0),12),label='HadCRUT4 method anomalies to preindustrial',color='darkcyan')
ax[0].plot(year,running_mean_func(np.nanmean(gmt['rcp85',:,'bm_ar5',0:1871],axis=0),12),label='HadCRUT4 method anomalies as in AR5',color='darkmagenta')
ax[0].set_ylim((-0.4,1.3))
ax[0].set_xlim((1861,2014))
ax[0].plot([1996,1996],[-0.4,1.5],color='k')
ax[0].set_ylabel('$\Delta T~[^\circ]$')
ax[0].legend(loc='upper left',fontsize=10)

ax[1].plot(year,running_mean_func(np.nanmean(gmt['rcp85',:,'tas_pre',0:1871],axis=0)-had4_gmt,240),label='SAT anomalies to preindustrial',color='darkorange')
ax[1].plot(year,running_mean_func(np.nanmean(gmt['rcp85',:,'tas_ar5',0:1871],axis=0)-had4_gmt,240),label='SAT anomalies as in AR5',color='darkblue')
ax[1].plot(year,running_mean_func(np.nanmean(gmt['rcp85',:,'bm_pre',0:1871],axis=0)-had4_gmt,240),label='HadCRUT4 method anomalies to preindustrial',color='darkcyan')
ax[1].plot(year,running_mean_func(np.nanmean(gmt['rcp85',:,'bm_ar5',0:1871],axis=0)-had4_gmt,240),label='HadCRUT4 method anomalies as in AR5',color='darkmagenta')
ax[1].set_ylim((-0.2,0.2))
ax[1].plot([1860,2020],[0,0],color='k')
ax[1].plot([1996,1996],[-0.2,0.2],color='k')
ax[1].set_xlim((1861,2015))
ax[1].set_ylabel('$\Delta T-\Delta T_{observed}~[^\circ]$')
plt.tight_layout()
plt.savefig('plots/GMT_ref.png')
plt.savefig('plots/GMT_ref.pdf')






#linear regression and estimates
styles=['bm_pre','bm_ar5','tas_pre','tas_ar5','b_pre','b_ar5']
gmt_lr=da.DimArray(axes=[['rcp26','rcp45','rcp85'],styles,styles,['slope','slope_err','intercept','intercept_err','1.5_low','1.5_up','1.5','1.5_err']],dims=['scenario','x','y','out'])
gmt_qu=da.DimArray(axes=[['rcp26','rcp45','rcp85'],styles,styles,[0,5,10,16.6,25,50,75,83.3,90,95,100]],dims=['scenario','x','y','out'])

for scenario in ['rcp85']:
	for x_method in ['bm_ar5','bm_pre','tas_pre','tas_ar5','b_pre','b_ar5']:
		plt.clf()
		fig,axes=plt.subplots(nrows=2,ncols=3,figsize=(12,8))
		ax=axes.flatten()
		for y_method,pp in zip(['bm_pre','bm_ar5','tas_pre','tas_ar5','b_pre','b_ar5'],range(6)):
			x_=np.asarray(gmt[scenario,:,x_method,:]).reshape(47*2880)
			y_=np.asarray(gmt[scenario,:,y_method,:]).reshape(47*2880)
			idx = np.isfinite(x_) & np.isfinite(y_)
			x,y=x_[idx],y_[idx]
			p, V = np.polyfit(x,y, 1, cov=True)
			gmt_lr[scenario,x_method,y_method,'slope']=p[0]
			gmt_lr[scenario,x_method,y_method,'intercept']=p[1]
			gmt_lr[scenario,x_method,y_method,'slope_err']=V[0,0]
			gmt_lr[scenario,x_method,y_method,'intercept_err']=V[1,1]
			gmt_lr[scenario,x_method,y_method,'1.5_up']=(1.5-(p[1]-V[1,1]))/(p[0]-V[0,0])
			gmt_lr[scenario,x_method,y_method,'1.5_low']=(1.5-(p[1]+V[1,1]))/(p[0]+V[0,0])
			gmt_lr[scenario,x_method,y_method,'1.5']=(1.5-p[1])/p[0]
			gmt_lr[scenario,x_method,y_method,'1.5_err']=gmt_lr[scenario,x_method,y_method,'1.5_up']-gmt_lr[scenario,x_method,y_method,'1.5_low']


			tmp=np.where((y>1.45) & (y<1.55))
			y_15=y[tmp]
			x_15=x[tmp]

			for qu in gmt_qu.out:
				gmt_qu[scenario,x_method,y_method,qu]=np.nanpercentile(x_15,qu)

			ax[pp].plot(x,y,marker='v',color='blue',linestyle='')
			ax[pp].plot(x_15,y_15,marker='o',color='green',linestyle='')
			ax[pp].plot([gmt_qu[scenario,x_method,y_method,0],gmt_qu[scenario,x_method,y_method,100]],[0.65,0.65],color='green')
			ax[pp].fill_between([gmt_qu[scenario,x_method,y_method,25],gmt_qu[scenario,x_method,y_method,75]],[0.63,0.63],[0.67,0.67],color='green')
			ax[pp].plot([gmt_qu[scenario,x_method,y_method,50],gmt_qu[scenario,x_method,y_method,50]],[0,1.5],color='green')
			y50=gmt_qu[scenario,x_method,y_method,50]
			ax[pp].text(y50,0.8,str(round(y50,3)),rotation=90,verticalalignment='center',horizontalalignment='center',backgroundcolor='white',color='green')

			ax[pp].plot(x__,p[0]*x__+p[1],color='red')
			ax[pp].plot(x__,(p[0]+V[0,0])*x__+(p[1]+V[1,1]),color='red')
			ax[pp].plot(x__,(p[0]-V[0,0])*x__+(p[1]-V[1,1]),color='red')
			yy=(1.5-p[1])/p[0]
			ax[pp].plot([yy,yy],[0,1.5],color='red',label=str(round(gmt_lr[scenario,x_method,y_method,'1.5'],4))+'+/-'+str(gmt_lr[scenario,x_method,y_method,'1.5_err']))
			ax[pp].text(yy,1.1,str(round(yy,3)),rotation=90,verticalalignment='center',horizontalalignment='center',backgroundcolor='white',color='red')

			ax[pp].set_xlim((0.61,2.5))
			ax[pp].set_ylim((0.61,2.5))
			ax[pp].set_xlabel(x_method.replace('_',' '))
			ax[pp].set_ylabel(y_method.replace('_',' '))
			ax[pp].plot([0,5],[0,5],'k--')
			ax[pp].legend(loc='upper left')

		plt.savefig('plots/linear_regression_to_'+x_method+'.png')
