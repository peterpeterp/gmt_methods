import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import itertools
import matplotlib


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

# fig 2
plt.clf()
plt.figure(figsize=(7,6))
l_styles = ['-','--','-.',':']
m_styles = ['','.','o','^','*']
colormap = matplotlib.cm.get_cmap('Spectral')
colormap = [colormap(i/float(len(gmt_.model)/3)) for i in range(len(gmt_.model)/3)]
plt.clf()
for model,(marker,linestyle,color) in zip(sorted(gmt_.model),itertools.product(m_styles,l_styles, colormap)):
	print model
	tmp=gmt_['xxx']['rcp85'][model]
	plt.plot(tmp['time'].ix[:],running_mean_func(tmp['gmt'].ix[:]-tmp['air'].ix[:],12),color=color, linestyle=linestyle,marker=marker,label=model)
plt.plot([1850,2100],[0,0],'k')
plt.ylim((-0.3,0.1))
plt.xlim((1850,2100))
plt.ylabel('Temperature anomaly deg C')
plt.legend(loc='lower left',ncol=4,fontsize=7)
plt.savefig('plots/cowtan_fig2_xxx.png')


# fig 3
plt.clf()
plt.plot(gmt['xxx','rcp85','ACCESS1-0','time'],running_mean_func(np.nanmean(gmt_['xxx','rcp85',:,'gmt',:]-gmt_['xxx','rcp85',:,'air',:],axis=0),36),label='Unmasked/absolute/variable ice',color='red',linestyle='-')
plt.plot(gmt_['xxx','rcp85','ACCESS1-0','time'],running_mean_func(np.nanmean(gmt_['xax','rcp85',:,'gmt',:]-gmt_['xax','rcp85',:,'air',:],axis=0),36),label='Unmasked/anomaly/variable ice',color='blue',linestyle='-')
plt.plot(gmt_['xxx','rcp85','ACCESS1-0','time'],running_mean_func(np.nanmean(gmt_['mxx','rcp85',:,'gmt',:]-gmt_['mxx','rcp85',:,'air',:],axis=0),36),label='Masked/absolute/variable ice',color='red',linestyle='--')
plt.plot(gmt_['xxx','rcp85','ACCESS1-0','time'],running_mean_func(np.nanmean(gmt_['max','rcp85',:,'gmt',:]-gmt_['max','rcp85',:,'air',:],axis=0),36),label='Masked/anomaly/variable ice',color='blue',linestyle='--')
plt.plot(gmt_['xxx','rcp85','ACCESS1-0','time'],running_mean_func(np.nanmean(gmt_['xaf','rcp85',:,'gmt',:]-gmt_['xaf','rcp85',:,'air',:],axis=0),36),label='Unasked/absolute/fixed ice',color='green',linestyle='-')
plt.plot(gmt_['xxx','rcp85','ACCESS1-0','time'],running_mean_func(np.nanmean(gmt_['maf','rcp85',:,'gmt',:]-gmt_['maf','rcp85',:,'air',:],axis=0),36),label='Unmasked/anomaly/fixed ice',color='green',linestyle=':')
plt.plot(gmt_['xxx','rcp85','ACCESS1-0','time'],running_mean_func(np.nanmean(gmt_['had4','rcp85',:,'gmt',:]-gmt_['had4','rcp85',:,'air',:],axis=0),36),label='HadCRUT4 Method',color='black',linestyle=':')
plt.plot([1860,2014],[0,0],color='black')
plt.legend(loc='lower left')
plt.ylim((-0.07,0.05))
plt.ylabel('Temperature anomaly deg C')
plt.xlim((1860,2014))
plt.savefig('plots/cowtan_fig3.png')

gmt=gmt_all[gmt_all.style,gmt_all.scenario,models,gmt_all.variable,gmt_all.time]

# anomaly to preindustrial
for style in gmt.style:
	for scenario in gmt.scenario:
		for model in gmt.model:
			gmt[style,scenario,model,'air',:]-=np.nanmean(gmt[style,scenario,model,'air',0:240])
			gmt[style,scenario,model,'gmt',:]-=np.nanmean(gmt[style,scenario,model,'gmt',0:240])

# fig 3
plt.clf()
plt.plot(gmt['xxx','rcp85','ACCESS1-0','time'],running_mean_func(np.nanmean(gmt['xxx','rcp85',:,'gmt',:]-gmt['xxx','rcp85',:,'air',:],axis=0),36),label='Unmasked/absolute/variable ice',color='red',linestyle='-')
plt.plot(gmt['xxx','rcp85','ACCESS1-0','time'],running_mean_func(np.nanmean(gmt['xax','rcp85',:,'gmt',:]-gmt['xax','rcp85',:,'air',:],axis=0),36),label='Unmasked/anomaly/variable ice',color='blue',linestyle='-')
plt.plot(gmt['xxx','rcp85','ACCESS1-0','time'],running_mean_func(np.nanmean(gmt['mxx','rcp85',:,'gmt',:]-gmt['mxx','rcp85',:,'air',:],axis=0),36),label='Masked/absolute/variable ice',color='red',linestyle='--')
plt.plot(gmt['xxx','rcp85','ACCESS1-0','time'],running_mean_func(np.nanmean(gmt['max','rcp85',:,'gmt',:]-gmt['max','rcp85',:,'air',:],axis=0),36),label='Masked/anomaly/variable ice',color='blue',linestyle='--')
plt.plot(gmt['xxx','rcp85','ACCESS1-0','time'],running_mean_func(np.nanmean(gmt['xaf','rcp85',:,'gmt',:]-gmt['xaf','rcp85',:,'air',:],axis=0),36),label='Unasked/absolute/fixed ice',color='green',linestyle='-')
plt.plot(gmt['xxx','rcp85','ACCESS1-0','time'],running_mean_func(np.nanmean(gmt['maf','rcp85',:,'gmt',:]-gmt['maf','rcp85',:,'air',:],axis=0),36),label='Unmasked/anomaly/fixed ice',color='green',linestyle=':')
plt.plot(gmt['xxx','rcp85','ACCESS1-0','time'],running_mean_func(np.nanmean(gmt['had4','rcp85',:,'gmt',:]-gmt['had4','rcp85',:,'air',:],axis=0),36),label='HadCRUT4 Method',color='black',linestyle=':')
plt.plot([1860,2014],[0,0],color='black')
plt.legend(loc='lower left')
plt.ylim((-0.1,0.02))
plt.xlim((1860,2014))
plt.savefig('plots/cowtan_fig3_preindust.png')

dat=open('data/Had4_gmt.txt','r').read()
had4=[]
read='yes'
for line in dat.split('\n')[::2]:
	for anom in line.split(' ')[2:-1]:
		if anom!='':
			had4.append(float(anom))

had4=np.array(had4[11*12:-12])

# richardson 1a
plt.clf()
plt.figure(figsize=(6,7))
y=running_mean_func(had4-np.nanmean(had4[0:240]),24)
plt.plot(gmt['xxx','rcp85','ACCESS1-0','time'][0:1871],y,lw=3,color='gray',alpha=0.5)
y=running_mean_func(np.nanmean(gmt['xax','rcp85',:,'gmt',:],axis=0),24)
plt.plot(gmt['xxx','rcp85','ACCESS1-0','time'][::12],y[::12],label='Unmasked/absolute/variable ice',color='purple',linestyle='-',marker='o')
y=running_mean_func(np.nanmean(gmt['max','rcp85',:,'gmt',:],axis=0),24)
plt.plot(gmt['xxx','rcp85','ACCESS1-0','time'][::12],y[::12],label='Masked/absolute/variable ice',color='blue',linestyle='-',marker='v')
y=running_mean_func(np.nanmean(gmt['xax','rcp85',:,'air',:],axis=0),24)
plt.plot(gmt['xxx','rcp85','ACCESS1-0','time'],y,label='Unmasked/absolute/variable ice',color='red',linestyle='-')
plt.plot([1860,2014],[0,0],color='black')
plt.legend(loc='upper left')
plt.ylabel('delta T (deg C)')
plt.ylim((-0.4,1.2))
plt.xlim((1861,2016))
plt.savefig('plots/richardson_fig1a.png')

# richardson 1b
plt.clf()
plt.figure(figsize=(6,6.5))
air=running_mean_func(np.nanmean(gmt['xax','rcp85',:,'air',:],axis=0),12)
ma=running_mean_func(np.nanmean(gmt['had4','rcp85',:,'gmt',:],axis=0),12)
unma=running_mean_func(np.nanmean(gmt['xax','rcp85',:,'gmt',:],axis=0),12)
plt.plot(gmt['xxx','rcp85','ACCESS1-0','time'][::12],unma[::12]-air[::12],label='Unmasked/absolute/variable ice',color='purple',linestyle='-',marker='o',markersize=4)
plt.plot(gmt['xxx','rcp85','ACCESS1-0','time'][::12],ma[::12]-air[::12],label='Masked/absolute/variable ice',color='blue',linestyle='-',marker='v',markersize=4)
plt.plot([1860,2014],[0,0],color='black')
#plt.legend(loc='lower left')
plt.ylabel('delta T - delta T_air (deg C)')
plt.ylim((-0.25,0.05))
plt.xlim((1861,2016))
plt.savefig('plots/richardson_fig1b.png')





binned_gmt=da.DimArray(axes=[['rcp26','rcp45','rcp85'],['air','gmt'],[0,10,25,33,50,66,75,90,100],range(800)],dims=['scenario','variable','quantile','bins'])

for scenario in gmt.scenario:
	for air,i in zip(np.arange(0.,4.,0.005),range(800)):
		binned=[]
		for model in gmt.model:
			tmp_air=gmt['xxx',scenario,model,'air',:]
			tmp_gmt=gmt['had4',scenario,model,'gmt',:]
			binned+=list(tmp_gmt[np.where((tmp_air>=air) &(tmp_air<air+0.05))[0]])
		binned_gmt[scenario,'air',0,i]=air+0.025
		for qu in binned_gmt.quantile:
			binned_gmt[scenario,'gmt',qu,i]=np.nanpercentile(np.array(binned),qu)

# FIG 1
for scenario in gmt.scenario:
	plt.clf()
	for model in gmt.model:
		plt.scatter(gmt['xxx',scenario,model,'air',:],gmt['had4',scenario,model,'gmt',:],color='gray',alpha=0.1)
	plt.plot(binned_gmt[scenario,'air',0,:],binned_gmt[scenario,'gmt',50,:])
	plt.fill_between(binned_gmt[scenario,'air',0,:],binned_gmt[scenario,'gmt',25,:],binned_gmt[scenario,'gmt',75,:],alpha=0.3)
	plt.plot([-1,5],[-1,5],linestyle='--',color='k')
	air_15=binned_gmt[scenario,'air',0,np.nanargmin(abs(np.array(binned_gmt[scenario,'gmt',50,:])-1.5))]
	plt.plot([0,5],[1.5,1.5],color='red')
	plt.plot([air_15,air_15],[0,5],color='red')
	plt.ylim((0.61,2.5))
	plt.xlim((0.61,2.5))
	plt.xlabel('global mean air temperature anomaly')
	plt.ylabel('global mean temperature anomaly computed as for HadCrut')
	plt.savefig('plots/FIG1_'+scenario+'.png')


# FIG 1
for scenario in gmt.scenario:
	plt.clf()
	for model in gmt.model:
		plt.scatter(gmt['xxx',scenario,model,'air',:],gmt['had4',scenario,model,'gmt',:],color='gray',alpha=0.1)
	plt.plot(binned_gmt[scenario,'air',0,:],binned_gmt[scenario,'gmt',50,:])
	plt.fill_between(binned_gmt[scenario,'air',0,:],binned_gmt[scenario,'gmt',25,:],binned_gmt[scenario,'gmt',75,:],alpha=0.3)
	plt.plot([-1,5],[-1,5],linestyle='--',color='k')
	plt.plot([0,5],[1.5,1.5],color='red')
	air_15=binned_gmt[scenario,'air',0,np.nanargmin(abs(np.array(binned_gmt[scenario,'gmt',50,:])-1.5))]
	plt.plot([air_15,air_15],[0,5],color='red')
	air_15=binned_gmt[scenario,'air',0,np.nanargmin(abs(np.array(binned_gmt[scenario,'gmt',25,:])-1.5))]
	plt.plot([air_15,air_15],[0,5],color='red',linestyle='--')
	air_15=binned_gmt[scenario,'air',0,np.nanargmin(abs(np.array(binned_gmt[scenario,'gmt',75,:])-1.5))]
	plt.plot([air_15,air_15],[0,5],color='red',linestyle='--')
	plt.ylim((0.61,2.5))
	plt.xlim((0.61,2.5))
	plt.xlabel('global mean air temperature anomaly')
	plt.ylabel('global mean temperature anomaly computed as for HadCrut')
	plt.savefig('plots/FIG1_'+scenario+'.png')




# gmt_air=gmt.copy()
# for model in gmt.model:
# 	print model
# 	for style in gmt.style:
# 		for scenario in gmt.scenario:
# 			tmp=gmt_air[style,scenario,model,:,:].copy()
# 			gmt_air[style,scenario,model,:,:]=tmp[:,np.array(tmp['air',:]).argsort()]








# # fig 2
# for model in gmt.model:
# 	plt.clf()
# 	tmp=gmt['xxx']['rcp85'][model]
# 	plt.plot(tmp['time'].ix[:],running_mean_func(tmp['gmt'].ix[:]-tmp['air'].ix[:],12),label=model)
# 	plt.ylim((-0.3,0.1))
# 	plt.xlim((1850,2100))
# 	#plt.legend()
# 	plt.savefig('plots/fig2_xxx'+model+'.png')
#

#end
