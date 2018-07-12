import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import pandas as pd


os.chdir('/Users/peterpfleiderer/Documents/Projects/gmt')

models=[]
runs=[]
model_runs=[]
for folder in [fl.split('/')[-1].split('.')[0] for fl in glob.glob('blend-results.160518/rcp85-had4/*')]:
	models.append(folder.split('_')[1])
	runs.append(folder.split('_')[2])
	model_runs.append('_'.join(folder.split('_')[1:3]))

models=list(set(models))
runs=list(set(runs))
model_runs=list(set(model_runs))

scenarios=['rcp45','rcp85']

blended_masked=da.DimArray(axes=[scenarios,model_runs,range(1861,2100)],dims=['scenario','model_run','time'])
blended=da.DimArray(axes=[scenarios,model_runs,range(1861,2100)],dims=['scenario','model_run','time'])
tas=da.DimArray(axes=[scenarios,model_runs,range(1861,2100)],dims=['scenario','model_run','time'])

for scenario in scenarios:
	for model_run in model_runs:
		# blended-masked
		tmp=pd.read_table('blend-results.160518/rcp85-had4/rcp85_'+model_run+'.temp',sep=' ',header=None)
		tmp.columns=['time','air','gmt','diff']
		gmt=tmp['gmt']-np.mean(tmp['gmt'][:240])
		blended_masked[scenario,model_run,:2014]=np.mean(np.reshape(gmt,(len(gmt)/12,12)),axis=-1)

		# blended
		tmp=pd.read_table('blend-results.160518/rcp85-xax/rcp85_'+model_run+'.temp',sep=' ',header=None)
		tmp.columns=['time','air','gmt','diff']
		gmt=tmp['gmt']-np.mean(tmp['gmt'][:240])
		blended[scenario,model_run,:]=np.mean(np.reshape(gmt,(len(gmt)/12,12)),axis=-1)

		# tas
		tmp=pd.read_table('blend-results.160518/rcp85-xax/rcp85_'+model_run+'.temp',sep=' ',header=None)
		tmp.columns=['time','air','gmt','diff']
		gmt=tmp['air']-np.mean(tmp['air'][:240])
		tas[scenario,model_run,:]=np.mean(np.reshape(gmt,(len(gmt)/12,12)),axis=-1)


ds=da.Dataset({'blended_masked':blended_masked,'blended':blended,'tas':tas})
ds.write_nc('blend-results.160518/gmt_summary.nc', mode='w')


np.savetxt("blend-results.160518/gmt_blended-masked_rcp85.csv", np.vstack((blended_masked.time,blended_masked['rcp85'].values)).T, delimiter=",",header='year,'+','.join(blended_masked.model_run))
np.savetxt("blend-results.160518/gmt_blended_rcp85.csv", np.vstack((blended.time,blended['rcp85'].values)).T, delimiter=",",header='year,'+','.join(blended.model_run))
np.savetxt("blend-results.160518/gmt_tas_rcp85.csv", np.vstack((tas.time,tas['rcp85'].values)).T, delimiter=",",header='year,'+','.join(tas.model_run))

np.savetxt("blend-results.160518/gmt_blended-masked_rcp45.csv", np.vstack((blended_masked.time,blended_masked['rcp45'].values)).T, delimiter=",",header='year,'+','.join(blended_masked.model_run))
np.savetxt("blend-results.160518/gmt_blended_rcp45.csv", np.vstack((blended.time,blended['rcp45'].values)).T, delimiter=",",header='year,'+','.join(blended.model_run))
np.savetxt("blend-results.160518/gmt_tas_rcp45.csv", np.vstack((tas.time,tas['rcp45'].values)).T, delimiter=",",header='year,'+','.join(tas.model_run))
