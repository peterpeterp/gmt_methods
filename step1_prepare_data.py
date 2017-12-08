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
	job_id=47

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
			command+=file_name+' '
		Popen(command+'tmp_m_'+var+'.nc',shell=True).wait()

		Popen('cdo selyear,1850/2099 tmp_m_'+var+'.nc tmp_s_'+var+'.nc',shell=True).wait()
		Popen('cdo -O remapdis,../../blend-runnable/grid1x1.cdo tmp_s_'+var+'.nc '+var+'_'+scenario+'.nc',shell=True).wait()
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


# ++++++++++++++++++++++++++++++
# + merge scenarios
# ++++++++++++++++++++++++++++++

for var in ['tas','tos','sic']:
	print 'checking',var

	# check file
	data=da.read_nc(var+'_rcp85.nc')
	if data.time[0]>18500117:

		# clean files as example
		example=da.read_nc('../ACCESS1-0_r1i1p1/'+var+'_rcp85.nc')
		example_time=example['time'].values
		example_time_bnds=example['time_bnds'].values

		# extend using example time axis
		time_extension=example_time[example_time<data.time[0]]
		time_ext=np.concatenate((time_extension,data.time))
		data_ext=np.concatenate((np.zeros([len(time_extension),len(data.lat),len(data.lon)])*np.nan,data[var].values))
		print len(time_extension)

		# check if time axis is complete
		if np.max(np.abs(time_ext-example_time))<3:

			# write file
			nc_in = Dataset('../ACCESS1-0_r1i1p1/'+var+'_rcp85.nc', "r")
			nc_out=Dataset(var+'_rcp85_extended.nc',"w")
			for dname, the_dim in nc_in.dimensions.iteritems():
				if dname=='time':	nc_out.createDimension(dname, len(time_ext))
				else:	nc_out.createDimension(dname, len(the_dim) if not the_dim.isunlimited() else None)
			for v_name, varin in nc_in.variables.iteritems():
				outVar = nc_out.createVariable(v_name, varin.datatype, varin.dimensions)
				outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})
				if v_name=='time':	outVar[:] = time_ext
				elif v_name=='time_bnds':	outVar[:] = example_time_bnds
				elif v_name==var:	outVar[:] = data_ext
				else:	outVar[:] = varin[:]
			nc_out.close()
			nc_in.close()
