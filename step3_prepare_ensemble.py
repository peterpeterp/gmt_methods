import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import itertools
import matplotlib

gmt_raw=da.read_nc('data/gmt_all_remapdis.nc')['gmt']

# remove special runs
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

# average all runs of one model
models=sorted(set([model_run.split('_')[0] for model_run in model_runs]))
gmt_model=da.DimArray(axes=[gmt_all.style,gmt_all.scenario,models,gmt_all.variable,np.arange(1850,2100,1)],dims=['style','scenario','model','variable','time'])
for model in models:
	ensemble=[model_run for model_run in model_runs if model_run.split('_')[0]==model]
	print model, ensemble
	gmt_model[:,:,model,:,:]=np.nanmean(gmt_year[:,:,ensemble,:,:],axis=2)

ds=da.Dataset({'gmt':gmt_model})
ds.write_nc('data/gmt_model.nc', mode='w')
