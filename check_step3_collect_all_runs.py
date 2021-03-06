import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import pandas as pd

styles=['xax','had4']
variables=['air','gmt']


# cowtan
models=[]
runs=[]
model_runs=[]
for folder in [fl.split('/')[-1].split('.')[0] for fl in glob.glob('blend-results.160518/rcp85-xax/*')]:
	models.append(folder.split('_')[1])
	runs.append(folder.split('_')[2])
	model_runs.append(folder.split('_')[1]+'_'+folder.split('_')[2])

models=list(set(models))
runs=list(set(runs))
model_runs=list(set(model_runs))

tmp_example=pd.read_table('blend-results.160518/rcp85-xax/rcp85_ACCESS1-0_r1i1p1.temp',sep=' ',header=None)
gmt=da.DimArray(axes=[styles,['rcp85'],model_runs,variables,np.array(tmp_example[0])],dims=['style','scenario','model_run','variable','time'])

for style in gmt.style:
	print style
	folder='blend-results.160518/rcp85-'+style+'/'
	for scenario in gmt.scenario:
		for model_run in model_runs:
			try:
				tmp=pd.read_table(folder+scenario+'_'+model_run+'.temp',sep=' ',header=None)
				tmp.columns=['time','air','gmt','diff']
				time_ax=np.array(tmp['time'])
				useful_years=time_ax[(time_ax>1861) & (time_ax<2100)]
				gmt[style,scenario,model_run,'air',useful_years]=np.array(tmp['air'])[(time_ax>1861) & (time_ax<2100)]
				gmt[style,scenario,model_run,'gmt',useful_years]=np.array(tmp['gmt'])[(time_ax>1861) & (time_ax<2100)]
			except:
				print model_run

ds=da.Dataset({'gmt':gmt})
ds.write_nc('data/gmt_all_cowtan.nc', mode='w')

# richardson
models=[]
runs=[]
model_runs=[]
for folder in [fl.split('/')[-1].split('.')[0] for fl in glob.glob('SI_richardson16tcr/data/hist_rcp85/Txax/*')]:
	models.append(folder.split('_')[0])
	runs.append(folder.split('_')[1])
	model_runs.append(folder.split('_')[0]+'_'+folder.split('_')[1])

models=list(set(models))
runs=list(set(runs))
model_runs=list(set(model_runs))

tmp_example=pd.read_table('SI_richardson16tcr/data/hist_rcp85/Txax/ACCESS1-0_r1i1p1.temp',sep='\t',header=None)
gmt=da.DimArray(axes=[styles,['rcp85'],model_runs,variables,np.array(tmp_example[0])],dims=['style','scenario','model_run','variable','time'])

for style,style_name in zip(['had4','xax'],['Had4','Txax']):
	print style
	for scenario in gmt.scenario:
		for model_run in model_runs:
			try:
				tmp=pd.read_table('SI_richardson16tcr/data/hist_rcp85/'+style_name+'/'+model_run+'.temp',sep='\t',header=None)
				gmt[style,scenario,model_run,'air',np.array(tmp[0])]=np.array(tmp[1])
				gmt[style,scenario,model_run,'gmt',np.array(tmp[0])]=np.array(tmp[2])
			except:
				print model_run

ds=da.Dataset({'gmt':gmt})
ds.write_nc('data/gmt_all_richardson.nc', mode='w')
