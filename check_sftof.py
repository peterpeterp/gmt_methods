import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import dimarray as da
import pandas as pd
from subprocess import Popen

try:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/gmt/')
except:
	os.chdir('/p/projects/tumble/carls/shared_folder/gmt/')

overwrite=True

job_id=39
style='xax'
scenario = 'rcp85'

folder=[fl.split('/')[-1] for fl in glob.glob('data_models/*')][job_id]
print folder
model=folder.split('_')[0]
run=folder.split('_')[1]

if True:
	if os.path.isfile('data_models/'+model+'_'+run+'/tas_'+scenario+'_extended.nc') and style=='had4':
		tas='data_models/'+model+'_'+run+'/tas_'+scenario+'_extended.nc'
	else:
		tas='data_models/'+model+'_'+run+'/tas_'+scenario+'.nc'

	if os.path.isfile('data_models/'+model+'_'+run+'/tos_'+scenario+'_extended.nc') and style=='had4':
		tos='data_models/'+model+'_'+run+'/tos_'+scenario+'_extended.nc'
	else:
		tos='data_models/'+model+'_'+run+'/tos_'+scenario+'.nc'

	if os.path.isfile('data_models/'+model+'_'+run+'/sic_'+scenario+'_extended.nc') and style=='had4':
		sic='data_models/'+model+'_'+run+'/sic_'+scenario+'_extended.nc'
	else:
		sic='data_models/'+model+'_'+run+'/sic_'+scenario+'.nc'

	for model_sftof in [fl.split('/')[-1].split('_')[0] for fl in glob.glob('data_models/*')]:
		sftof='sftof/'+model_sftof+'.nc'
		if os.path.isfile(sftof):
			if os.path.isfile(style+'_'+scenario+'.txt')==False or overwrite:
				Popen('python gmt_methods/ncblendmask-nc4.py '+style+' '+tas+' '+tos+' '+sic+' '+sftof+' > test/'+model+'_'+run+'_sftof_'+model_sftof+'.txt',shell=True).wait()


models=[]
for folder in [fl.split('/')[-1] for fl in glob.glob('data_models/*')]:
	models.append(folder.split('_')[0])


models=list(set(models))

tmp_example=pd.read_table('data_models/ACCESS1-0_r1i1p1/had4_rcp85.txt',sep=' ',header=None)
gmt=da.DimArray(axes=[models,np.array(tmp_example[0])],dims=['sftof_model','time'])

for sftof_model in models:
	try:
		tmp=pd.read_table('test/'+model+'_'+run+'_sftof_'+model_sftof+'.txt',sep=' ',header=None)
		tmp.columns=['time','air','gmt','diff']
		time_ax=np.array(tmp['time'])
		useful_years=time_ax[(time_ax>1850) & (time_ax<2100)]
		gmt[sftof_model,useful_years]=np.array(tmp['gmt'])[(time_ax>1850) & (time_ax<2100)]
	except:
		pass


ds=da.Dataset({'gmt':gmt})
ds.write_nc('test/gmt_sftof_test.nc', mode='w')
