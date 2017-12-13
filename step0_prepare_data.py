import os,glob,sys
from subprocess import Popen
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import dimarray as da
import pandas as pd
import collections

try:
	os.chdir('/p/projects/tumble/carls/shared_folder/gmt')
except:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/gmt')


try:
	job_id=int(os.environ.get('SLURM_ARRAY_TASK_ID'))
except:
	job_id=0

overwrite=True

folder=[fl.split('/')[-1] for fl in glob.glob('data_models/*')][job_id]
print folder
model=folder.split('_')[0]
run=folder.split('_')[1]
model_run=model+'_'+run


#Popen('mkdir data_models/'+model+'_'+run, shell=True).wait()
os.chdir('data_models/'+model+'_'+run+'/')

os.system('export SKIP_SAME_TIME=1')

# ++++++++++++++++++++++++++++++
# + get files
# ++++++++++++++++++++++++++++++

variable={'tas':'Amon','sic':'OImon','tos':'Omon'}

def normal_procedure(model,run,scenario,group,var,overwrite):
	command='cdo -a mergetime '
	hist_files=glob.glob('/p/projects/ipcc_pcmdi/ipcc_ar5_pcmdi/pcmdi_data/historical/'+group+'/'+var+'/'+model+'/'+run+'/*')
	scenario_files=glob.glob('/p/projects/ipcc_pcmdi/ipcc_ar5_pcmdi/pcmdi_data/'+scenario+'/'+group+'/'+var+'/'+model+'/'+run+'/*')
	if len(scenario_files)!=0 and (os.path.isfile(var+'_'+scenario+'.nc')==False or overwrite):
		for file_name in scenario_files+hist_files:
			print file_name
			if var in 'tos','sic':
				command+='-mul sftof_NaN1.nc '+file_name+' '
			else:
				command+=file_name+' '
		Popen(command+'tmp_m_'+var+'.nc',shell=True).wait()

		Popen('cdo selyear,1850/2099 tmp_m_'+var+'.nc tmp_s_'+var+'.nc',shell=True).wait()
		Popen('cdo -O remapdis,../../blend-runnable/grid1x1.cdo tmp_s_'+var+'.nc '+var+'_'+scenario+'_.nc',shell=True).wait()
		#Popen('cdo -O remapnn,../../blend-runnable/grid1x1.cdo tmp_s_'+var+'.nc '+var+'_'+scenario+'.nc',shell=True).wait()
		Popen('rm tmp_s_'+var+'.nc tmp_m_'+var+'.nc',shell=True).wait()
	if len(scenario_files)==0:
		info=open('delete_here','w')
		info.write('bla')
		info.close()

for scenario in ['rcp85']:
	for var,group in zip(variable.keys(),variable.values()):
		print scenario,var,group
		print model,run
		normal_procedure(model,run,scenario,group,var,overwrite)
