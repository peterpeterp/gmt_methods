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
models.remove('BNU-ESM')
models.remove('bcc-csm1-1-m')

gmt_=gmt_all[gmt_all.style,gmt_all.scenario,models,gmt_all.variable,gmt_all.time]

# cowtan fig 2
plt.close()
plt.figure(figsize=(7,6))
l_styles = ['-','--','-.',':']
m_styles = ['','.','o','^','*']
colormap = matplotlib.cm.get_cmap('Spectral')
colormap = [colormap(i/float(len(gmt_.model)/3)) for i in range(len(gmt_.model)/3)]
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


# cowtan fig 3
plt.close()
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

# cowtan fig 3 (anomaly to preindustrial)
plt.close()
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
plt.close()
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
plt.close()
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
