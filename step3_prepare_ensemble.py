import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import itertools
import matplotlib

os.chdir('/Users/peterpfleiderer/Documents/Projects/gmt')

gmt_raw=da.read_nc('data/gmt_all.nc')['gmt']

# remove special runs
model_runs=sorted(gmt_raw.model_run)
for model_run in gmt_raw.model_run:
	#if model_run.split('_')[0] in ['CESM1-CAM5','BNU-ESM','bcc-csm1-1-m','CESM1-WACCM']:
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

# yearly values
gmt_year=da.DimArray(axes=[gmt_raw.style,gmt_raw.scenario,model_runs,gmt_raw.variable,np.arange(1850,2100,1)],dims=['style','scenario','model_run','variable','time'])
for style in gmt_year.style:
	for model_run in gmt_year.model_run:
		for variable in gmt_year.variable:
			for year in gmt_year.time:
				gmt_year[style,'rcp85',model_run,variable,year]=np.nanmean(gmt_all_clean[style,'rcp85',model_run,variable,year:year+1])

ds=da.Dataset({'gmt':gmt_year})
ds.write_nc('data/gmt_year.nc', mode='w')

# average all runs of one model
models=sorted(set([model_run.split('_')[0] for model_run in model_runs]))
print models
gmt_model=da.DimArray(axes=[gmt_raw.style,gmt_raw.scenario,models,gmt_raw.variable,np.arange(1850,2100,1)],dims=['style','scenario','model','variable','time'])
for model in models:
	ensemble=[model_run for model_run in model_runs if model_run.split('_')[0]==model]
	gmt_model[:,:,model,:,:]=np.nanmean(gmt_year[:,:,ensemble,:,:],axis=2)

ds=da.Dataset({'gmt':gmt_model})
ds.write_nc('data/gmt_year_model.nc', mode='w')

def running_mean_func(xx,N):
	if N==1:
		return xx
	if N!=1:
	    x=np.ma.masked_invalid(xx.copy())
	    ru_mean=x.copy()*np.nan
	    for t in range(int(N/2),len(x)-int(N/2)):
	        ru_mean[t]=np.nanmean(x[t-int(N/2):t+int(N/2)])
	    return ru_mean

# 20 year running mean values
gmt_20year=da.DimArray(axes=[gmt_raw.style,gmt_raw.scenario,model_runs,gmt_raw.variable,np.arange(1850,2100,1)],dims=['style','scenario','model_run','variable','time'])
for style in gmt_year.style:
	for model_run in gmt_year.model_run:
		for variable in gmt_year.variable:
			gmt_20year[style,'rcp85',model_run,variable,:]=running_mean_func(gmt_year[style,'rcp85',model_run,variable,:],20)

ds=da.Dataset({'gmt':gmt_20year})
ds.write_nc('data/gmt_20year.nc', mode='w')

# average all runs of one model
models=sorted(set([model_run.split('_')[0] for model_run in model_runs]))
print models
gmt_20year_model=da.DimArray(axes=[gmt_raw.style,gmt_raw.scenario,models,gmt_raw.variable,np.arange(1850,2100,1)],dims=['style','scenario','model','variable','time'])
for model in models:
	ensemble=[model_run for model_run in model_runs if model_run.split('_')[0]==model]
	gmt_20year_model[:,:,model,:,:]=np.nanmean(gmt_20year[:,:,ensemble,:,:],axis=2)

ds=da.Dataset({'gmt':gmt_20year_model})
ds.write_nc('data/gmt_20year_model.nc', mode='w')






# tmp_gmt=gmt_model.copy()
# tmp_gmt.values-=np.expand_dims(np.nanmean(tmp_gmt[:,:,:,:,1861:1880].values,axis=4),axis=4)
#
# for model in models:
# 	ensemble=[model_run for model_run in model_runs if model_run.split('_')[0]==model]
# 	tmp=gmt_model['xax','rcp85',model,'air',:]-np.nanmean(gmt_model['xax','rcp85',model,'air',1861:1880])
# 	print(model,np.nanmean(tmp[1986:2005])-np.nanmean(tmp_gmt['xax','rcp85',:,'air',1986:2005]),len(ensemble),ensemble)
#
#
# for model in models:
# 	ensemble=[model_run for model_run in model_runs if model_run.split('_')[0]==model]
# 	if len(ensemble)>1:
# 		tmp=gmt_model['xax','rcp85',model,'air',:]-np.nanmean(gmt_model['xax','rcp85',model,'air',1861:1880])
# 		print(model,(np.nanmean(tmp[1986:2005])-np.nanmean(tmp_gmt['xax','rcp85',:,'air',1986:2005]))*len(ensemble),len(ensemble))
