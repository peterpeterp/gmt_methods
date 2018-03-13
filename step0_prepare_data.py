import os,glob,sys
import subprocess
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
	overwrite=True
	folder=[fl.split('/')[-1] for fl in glob.glob('data_models/*')][job_id]
	print folder
	model=folder.split('_')[0]
	run=folder.split('_')[1]
	model_run=model+'_'+run
	var_names=['tas','sic','tos']


except:
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("--overwrite",'-o', help="overwrite output files",action="store_true")
	parser.add_argument('--model','-m',help='model name',required=True)
	parser.add_argument('--run','-r' ,help='run name',required=True)
	parser.add_argument('--variable','-v' ,help='variables to prepare',nargs='+',required=False)
	args = parser.parse_args()

	if args.overwrite:
	    overwrite=True
	else:
	    overwrite=False

	model=args.model
	run=args.run

	if args.variable is not None:
		var_names=args.variable
	else:
		var_names=['tas','sic','tos']

# there seems to be some issue with cdo/1.8.0 and this script
os.system('module load cdo/1.7.0')


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
			command+=file_name+' '
		Popen(command+'tmp_m_'+var+'.nc',shell=True).wait()
		if var=='tos':
			# check if "not-ocean-cells" are missing or 273.1 as in EC-EARTH
			cdoinfo=Popen('cdo info tmp_m_'+var+'.nc',shell=True, stdout=subprocess.PIPE).stdout.read()
			# reading one line of cdo info
			# level=0 , if missing=0 the below condition is True
			# /!\ this condition might become a problem when there are other 0 appearing in the output
			if len(cdoinfo.split('\n')[1].split(' 0 '))==3:
				# change 273.15 to missing
				Popen('cdo selyear,1850/2099 -m 1.0e20 setrtomiss,273.14,273.16 tmp_m_'+var+'.nc tmp_s_'+var+'.nc',shell=True).wait()
			else:
				Popen('cdo selyear,1850/2099 tmp_m_'+var+'.nc tmp_s_'+var+'.nc',shell=True).wait()

		else:
			Popen('cdo selyear,1850/2099 tmp_m_'+var+'.nc tmp_s_'+var+'.nc',shell=True).wait()

		Popen('cdo -O remapdis,../../blend-runnable/grid1x1.cdo tmp_s_'+var+'.nc '+var+'_'+scenario+'.nc',shell=True).wait()
		#Popen('rm tmp_s_'+var+'.nc tmp_m_'+var+'.nc',shell=True).wait()
	if len(scenario_files)==0:
		info=open('delete_here','w')
		info.write('bla')
		info.close()

for scenario in ['rcp85']:
	for var in var_names:
		group=variable[var]
		print scenario,var,group
		print model,run
		normal_procedure(model,run,scenario,group,var,overwrite)
