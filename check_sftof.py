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

overwrite=False

job_id=39
style='xax'
scenario = 'rcp85'

folder=[fl.split('/')[-1] for fl in glob.glob('data_models/*')][job_id]
print folder
model=folder.split('_')[0]
run=folder.split('_')[1]

models=[]
for folder in [fl.split('/')[-1] for fl in glob.glob('data_models/*')]:
	models.append(folder.split('_')[0])
models=list(set(models))

if False:
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

	for model_sftof in models:
		sftof='sftof/'+model_sftof+'.nc'
		if os.path.isfile(sftof):
			if os.path.isfile('test/'+model+'_'+run+'_sftof_'+model_sftof+'.txt')==False or overwrite:
				Popen('python gmt_methods/ncblendmask-nc4.py '+style+' '+tas+' '+tos+' '+sic+' '+sftof+' > test/'+model+'_'+run+'_sftof_'+model_sftof+'.txt',shell=True).wait()

if False:
	tmp_example=pd.read_table('data_models/ACCESS1-0_r1i1p1/had4_rcp85.txt',sep=' ',header=None)
	gmt=da.DimArray(axes=[models,np.array(tmp_example[0])],dims=['sftof_model','time'])

	for sftof_model in models:
		try:
			tmp=pd.read_table('test/'+model+'_'+run+'_sftof_'+sftof_model+'.txt',sep=' ',header=None)
			tmp.columns=['time','air','gmt','diff']
			time_ax=np.array(tmp['time'])
			useful_years=time_ax[(time_ax>1850) & (time_ax<2100)]
			gmt[sftof_model,useful_years]=np.array(tmp['gmt'])[(time_ax>1850) & (time_ax<2100)]
		except:
			pass

	ds=da.Dataset({'gmt':gmt})
	ds.write_nc('test/gmt_sftof_test.nc', mode='w')


model_run='CanESM2_r1i1p1'
gmt=da.read_nc('data/gmt_sftof_test.nc')['gmt']
for style,var,title in zip(['xax'],['air'],['Blended air/sea temperature, unmasked, temperature anomalies, variable ice']):
	plt.close()
	fig,axes=plt.subplots(nrows=9,ncols=10,figsize=(12,15))
	axes=axes.flatten()
	for sftof_model,ax,i in zip(sorted(gmt.sftof_model),axes[0:len(gmt.sftof_model)],range(len(gmt.sftof_model))):
		cowtan_file='blend-results.160518/rcp85-'+style+'/rcp85_'+model_run+'.temp'
		if np.isfinite(np.nanmean(gmt[sftof_model,:].values)) and os.path.isfile(cowtan_file):
			tmp=pd.read_table(cowtan_file,sep=' ',header=None)
			tmp.columns=['time','air','gmt','diff']
			perc_diff=(gmt[sftof_model,1861:2100].values-np.array(tmp[var]))
			ax.plot(np.array(tmp['time']),perc_diff)
			print perc_diff
		ax.text(1853,0.04,sftof_model.replace('_','\n'),fontsize=8)
		ax.set_xlim((1850,2100))
		ax.set_ylim((-0.05,0.05))
		ax.get_xaxis().set_visible(False)
		ax.set_yticks([-0.05,-0.025,0,0.025,0.05])
		if i in range(0,90,10):
			ax.set_ylabel('devaiation')
		else:
			ax.set_yticklabels(['','','','',''])

	for ax in axes[85:90]:
		ax.axis('off')

	plt.suptitle(title)
	plt.savefig('plots/check_'+style+'_'+var+'_detail_sftof.png')
