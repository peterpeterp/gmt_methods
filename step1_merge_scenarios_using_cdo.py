import os,glob,sys
from subprocess import Popen
import dimarray as da
import numpy as np
import pandas as pd

from netCDF4 import Dataset,netcdftime,num2date

overwrite=True

try:
	os.chdir('/p/projects/tumble/carls/shared_folder/gmt')
except:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/gmt')

try:
	job_id=int(os.environ.get('SLURM_ARRAY_TASK_ID'))
except:
	job_id=1

folder=[fl.split('/')[-1] for fl in glob.glob('data_models/*')][job_id]
print folder
model=folder.split('_')[0]
run=folder.split('_')[1]
scenario = 'rcp85'

os.chdir('data_models/'+model+'_'+run+'/')

for var in ['tas','tos','sic']:
	# clean file as example
	example_file='../../data_models/ACCESS1-0_r1i1p1/'+var+'_historical.nc'
	full_time=da.read_nc(example_file)['time'].values
	full_time_bnds=da.read_nc(example_file)['time_bnds'].values

	# read raw file
	raw_file=var+'_historical.nc'
	raw=da.read_nc(raw_file)

	# check if complete
	if raw.time[0]>18500116:
		# extend using example time axis
		time_extension=full_time[full_time<raw.time[0]]
		time_bnds_ext=full_time_bnds[full_time<raw.time[0]]
		raw_ext=np.zeros([len(time_extension),len(raw.lat),len(raw.lon)])*np.nan

		# write file
		nc_in = Dataset(example_file, "r")
		ext_file=raw_file.replace('.nc','_missing_extension.nc')
		os.system('rm '+ext_file)
		nc_out=Dataset(ext_file,"w")
		for dname, the_dim in nc_in.dimensions.iteritems():
			if dname=='time':	nc_out.createDimension(dname, len(time_extension))
			else:	nc_out.createDimension(dname, len(the_dim) if not the_dim.isunlimited() else None)
		for v_name, varin in nc_in.variables.iteritems():
			outVar = nc_out.createVariable(v_name, varin.datatype, varin.dimensions)
			outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})
			if v_name=='time':	outVar[:] = time_extension
			elif v_name=='time_bnds':	outVar[:] = time_bnds_ext
			elif v_name==var:	outVar[:] = raw_ext
			else:	outVar[:] = varin[:]
		nc_out.close()
		nc_in.close()

		Popen('cdo -O mergetime '+ext_file+' '+raw_file+' '+var+'_rcp85.nc'+' '+var+'_rcp85_merged.nc',shell=True).wait()

	else:
		Popen('cdo -O mergetime '+raw_file+' '+var+'_rcp85.nc'+' '+var+'_rcp85_merged.nc',shell=True).wait()
