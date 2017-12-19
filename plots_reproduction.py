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

def yearly_anomaly(gmt_in,ref_period=[1861,1880]):
	gmt_anom=gmt_in
	# anomaly to preindustrial
	for style in gmt_anom.style:
		for scenario in gmt_anom.scenario:
			for model in gmt_anom.model_run:
				gmt_anom[style,scenario,model,'air',:]-=np.nanmean(gmt_in[style,scenario,model,'air',ref_period[0]:ref_period[1]])
				gmt_anom[style,scenario,model,'gmt',:]-=np.nanmean(gmt_in[style,scenario,model,'gmt',ref_period[0]:ref_period[1]])

	# yearly values
	gmt_year=da.DimArray(axes=[gmt_all.style,gmt_all.scenario,gmt_in.model_run,gmt_all.variable,np.arange(1850,2100,1)],dims=['style','scenario','model_run','variable','time'])
	for model in gmt_year.model_run:
		for style in gmt_year.style:
			for var in gmt_year.variable:
				for year in gmt_year.time:
					gmt_year[style,'rcp85',model,var,year]=np.nanmean(gmt_anom[style,'rcp85',model,var,year:year+1])

	return gmt_year

gmt_raw=da.read_nc('data/gmt_all_remapdis.nc')['gmt']
model_runs=sorted(gmt_raw.model_run)
for model_run in gmt_raw.model_run:
	if model_run.split('_')[0] in ['CESM1-CAM5','BNU-ESM','bcc-csm1-1-m','CESM1-WACCM']:
		model_runs.remove(model_run)
	elif np.isnan(np.nanmean(gmt_raw['xax','rcp85',model_run,'gmt',:].values)):
		model_runs.remove(model_run)

model_runs.remove('EC-EARTH_r7i1p1')
model_runs.remove('EC-EARTH_r11i1p1')
model_runs.remove('EC-EARTH_r12i1p1')
model_runs.remove('EC-EARTH_r13i1p1')
model_runs.remove('EC-EARTH_r14i1p1')

gmt_all_clean=gmt_raw[gmt_raw.style,gmt_raw.scenario,model_runs,gmt_raw.variable,gmt_raw.time]
gmt_year=yearly_anomaly(gmt_all_clean)

gmt_cowtan=da.read_nc('data/gmt_all_cowtan.nc')['gmt']
gmt_cowtan_year=yearly_anomaly(gmt_cowtan)


models=sorted(set([model_run.split('_')[0] for model_run in model_runs]))
gmt_model=da.DimArray(axes=[gmt_all.style,gmt_all.scenario,models,gmt_all.variable,np.arange(1850,2100,1)],dims=['style','scenario','model','variable','time'])
for model in models:
	ensemble=[model_run for model_run in model_runs if model_run.split('_')[0]==model]
	print model, ensemble
	gmt_model[:,:,model,:,:]=np.nanmean(gmt_year[:,:,ensemble,:,:],axis=2)

dat=open('data/Had4_gmt.txt','r').read()
had4=[]
read='yes'
for line in dat.split('\n')[::2]:
	for anom in line.split(' ')[2:-1]:
		if anom!='':
			had4.append(float(anom))

had4=np.array(had4[11*12:-12])

# richardson 1b
plt.close()
plt.figure(figsize=(6,6.5))
air=gmt_year['xax','rcp85',:,'air',:]
for style,marker,color in zip(['xax','had4'],['o','v'],['purple','blue']):
	plt.fill_between(gmt_year.time,np.nanpercentile(gmt_year[style,'rcp85',:,'gmt',:]-air,1/6.*100,axis=0),np.nanpercentile(gmt_year[style,'rcp85',:,'gmt',:]-air,5/6.*100,axis=0),color=color,alpha=0.3)
	plt.plot(gmt_year.time,np.nanpercentile(gmt_year[style,'rcp85',:,'gmt',:]-air,50,axis=0),label=style,color=color,linestyle='-',marker=marker,markersize=4)
	#plt.plot(gmt_year.time,np.nanmean(gmt_year[style,'rcp85',:,'gmt',:]-air,axis=0),label=style,color=color,linestyle='--')

for style,marker,color in zip(['xax','had4'],['o','v'],['red','green']):
	plt.plot(gmt_cowtan_year.time,np.nanmean(gmt_cowtan_year[style,'rcp85',:,'gmt',:]-gmt_cowtan_year['xax','rcp85',:,'air',:],axis=0),label=style,color=color,linestyle='-')


for style,marker,color in zip(['xax','had4'],['o','v'],['magenta','cyan']):
	plt.plot(gmt_model.time,np.nanmean(gmt_model[style,'rcp85',:,'gmt',:]-gmt_model['xax','rcp85',:,'air',:],axis=0),label=style,color=color,linestyle='-')

plt.plot([1860,2014],[0,0],color='black')
#plt.legend(loc='lower left')
plt.ylabel('delta T - delta T_air (deg C)')
plt.ylim((-0.25,0.05))
plt.xlim((1861,2016))
plt.savefig('plots/reproduction/richardson_fig1b.png')


# gmt_=gmt_all[gmt_all.style,gmt_all.scenario,model_runs,gmt_all.variable,gmt_all.time]
#
# # cowtan fig 2
# plt.close()
# fig,ax=plt.subplots(nrows=1,ncols=2,figsize=(10,6))
# l_styles = ['-','--','-.',':']
# m_styles = ['','.','o','^','*']
# colormap = matplotlib.cm.get_cmap('Spectral')
# colormap = [colormap(i/float(len(gmt_.model_run)/8)) for i in range(len(gmt_.model_run)/8)]
# for model,(marker,linestyle,color) in zip(sorted(gmt_.model_run),itertools.product(m_styles,l_styles, colormap)):
# 	print model
# 	tmp=gmt_['xax']['rcp85'][model]
# 	ax[0].plot(gmt_.time,running_mean_func(tmp['gmt'].ix[:]-tmp['air'].ix[:],12),color=color, linestyle=linestyle,marker=marker,label=model)
# 	ax[1].plot([-99],[99],label=model,color=color, linestyle=linestyle,marker=marker)
# ax[0].plot([1850,2100],[0,0],'k')
# ax[0].set_ylim((-0.3,0.1))
# ax[0].set_xlim((1850,2100))
# ax[0].set_ylabel('Temperature anomaly deg C')
#
# ax[1].axis('off')
# ax[1].set_xlim((1850,2100))
# ax[1].legend(loc='lower left',ncol=4,fontsize=7)
# plt.savefig('plots/reproduction/cowtan_fig2_xax.png')
