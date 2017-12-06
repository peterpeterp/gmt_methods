import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import pandas as pd

models=[]
runs=[]
model_runs=[]
for folder in [fl.split('/')[-1] for fl in glob.glob('data_models/*')]:
	models.append(folder.split('_')[0])
	runs.append(folder.split('_')[1])
	model_runs.append(folder)

models=list(set(models))
runs=list(set(runs))
model_runs=list(set(model_runs))

styles=['xax','had4']

variables=['air','gmt']


tmp_example=pd.read_table('data_models/ACCESS1-0_r1i1p1/had4_rcp85_old_mask.txt',sep=' ',header=None)
gmt=da.DimArray(axes=[styles,['rcp85'],model_runs,variables,np.array(tmp_example[0])],dims=['style','scenario','model_run','variable','time'])

for style in gmt.style:
	print style
	for scenario in gmt.scenario:
		print scenario
		for model_run in model_runs:
			if len(glob.glob('data_models/'+model_run+'/*'+scenario+'*.txt'))!=0:
				#tmp=pd.read_table('data_models/'+model+'_'+run+'/'+style+'_'+scenario+'.txt',sep=' ',header=None)
				try:
					tmp=pd.read_table('data_models/'+model_run+'/'+style+'_'+scenario+'_old_mask.txt',sep=' ',header=None)
					tmp.columns=['time','air','gmt','diff']
					time_ax=np.array(tmp['time'])
					useful_years=time_ax[(time_ax>1850) & (time_ax<2100)]
					gmt[style,scenario,model_run,'air',useful_years]=np.array(tmp['air'])[(time_ax>1850) & (time_ax<2100)]
					gmt[style,scenario,model_run,'gmt',useful_years]=np.array(tmp['gmt'])[(time_ax>1850) & (time_ax<2100)]
				except:
					pass


ds=da.Dataset({'gmt':gmt})
ds.write_nc('data/gmt_all_old_mask.nc', mode='w')
