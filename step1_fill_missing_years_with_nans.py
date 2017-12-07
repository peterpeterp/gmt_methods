import os,glob,sys
from subprocess import Popen
import dimarray as da
import numpy as np
import pandas as pd

from netCDF4 import Dataset,netcdftime,num2date


overwrite=True

try:
	job_id=int(os.environ.get('SLURM_ARRAY_TASK_ID'))
except:
	job_id=1


folder=[fl.split('/')[-1] for fl in glob.glob('data_models/*')][job_id]
print folder
model=folder.split('_')[0]
run=folder.split('_')[1]
scenario = 'rcp85'

for var in ['tas','tos','sic']:
	# clean file as example
	example_file='data_models/ACCESS1-0_r1i1p1/'+var+'_rcp85.nc'
	full_time=da.read_nc(example_file)['time'].values

	# read raw file
	raw_file='data_models/'+model+'_'+run+'/'+var+'_'+scenario+'.nc'
	raw=da.read_nc('data_models/'+model+'_'+run+'/'+var+'_'+scenario+'.nc')

	# check if complete
	if raw.time[0]>18500116:
		os.system("mv "+raw_file+' '+raw_file.replace('.nc','_raw.nc'))

		# extend using example time axis
		time_extension=full_time[full_time<raw.time[0]]
		time_ext=np.concatenate((time_extension,raw.time))
		raw_ext=np.concatenate((np.zeros([len(time_extension),len(raw.lat),len(raw.lon)])*np.nan,raw[var].values))

		# check if time axis is complete
		if np.max(np.abs(time_ext-full_time))<3:

			# write file
			nc_in = Dataset(example_file, "r")
			nc_out=Dataset(raw_file,"w")
			for dname, the_dim in nc_in.dimensions.iteritems():
				nc_out.createDimension(dname, len(the_dim) if not the_dim.isunlimited() else None)
			for v_name, varin in nc_in.variables.iteritems():
				outVar = nc_out.createVariable(v_name, varin.datatype, varin.dimensions)
				outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})
				if v_name==var:	outVar[:] = raw_ext
				else:	outVar[:] = varin[:]
			nc_out.close()
			nc_in.close()
