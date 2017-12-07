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

for var in ['tas','tos','sic']:
	print var

	# clean files as example
	example_future=da.read_nc('data_models/ACCESS1-0_r1i1p1/'+var+'_rcp85.nc')
	example_hist=da.read_nc('data_models/ACCESS1-0_r1i1p1/'+var+'_historical.nc')

	example_time=np.concatenate((example_hist['time'].values,example_future['time'].values))
	example_time_bnds=np.concatenate((example_hist['time_bnds'].values,example_future['time_bnds'].values))

	# check historical file
	hist=da.read_nc('data_models/'+model+'_'+run+'/'+var+'_historical.nc')
	if hist.time[0]>18500116:
		# extend using example time axis
		time_extension=example_time[example_time<hist.time[0]]
		time_ext=np.concatenate((time_extension,hist.time))
		hist_ext=np.concatenate((np.zeros([len(time_extension),len(hist.lat),len(hist.lon)])*np.nan,hist[var].values))
		print len(time_extension)
	else:
		time_ext=hist.time
		hist_ext=hist[var].values

	print len(hist.time)
	print len(time_ext)
	# combine with future file
	future=da.read_nc('data_models/'+model+'_'+run+'/'+var+'_rcp85.nc')
	time_ext=np.concatenate((time_ext,future.time))
	data_ext=np.concatenate((hist_ext,future[var].values))
	print len(future.time)
	print len(time_ext)

	# check if time axis is complete
	if np.max(np.abs(time_ext-example_time))<3:

		# write file
		nc_in = Dataset('data_models/ACCESS1-0_r1i1p1/'+var+'_rcp85.nc', "r")
		nc_out=Dataset('data_models/'+model+'_'+run+'/'+var+'_rcp85_merged.nc',"w")
		for dname, the_dim in nc_in.dimensions.iteritems():
			nc_out.createDimension(dname, len(the_dim) if not the_dim.isunlimited() else None)
		for v_name, varin in nc_in.variables.iteritems():
			outVar = nc_out.createVariable(v_name, varin.datatype, varin.dimensions)
			outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})
			if v_name==var:	outVar[:] = data_ext
			else:	outVar[:] = varin[:]
		nc_out.close()
		nc_in.close()
