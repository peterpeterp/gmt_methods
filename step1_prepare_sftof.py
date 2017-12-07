import os,glob,sys
from subprocess import Popen
import dimarray as da
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date


try:
	os.chdir('/p/projects/tumble/carls/shared_folder/gmt')
except:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/gmt')

for folder in [fl.split('/')[-1] for fl in glob.glob('data_models/*')]:
	print folder
	model=folder.split('_')[0]


	if model in [ff.split('_')[-1].split('.nc')[0] for ff in glob.glob('sftof/sftof_fx_*.nc')]:
		Popen('cdo remapdis,blend-runnable/grid1x1.cdo '+file+' sftof/'+file.split('_')[2]+'.nc',shell=True).wait()

	elif model in [ff.split('/')[-1] for ff in glob.glob('/p/projects/ipcc_pcmdi/ipcc_ar5_pcmdi/pcmdi_data/historical/fx/sftlf/*')]:
		in_file=glob.glob('/p/projects/ipcc_pcmdi/ipcc_ar5_pcmdi/pcmdi_data/historical/fx/sftlf/'+model+'/*/*')[0]

		lf=da.read_nc(in_file)['sftlf']
		lf[lf>0]=np.nan
		lf[lf==0]=100
		lf[np.isfinite(lf)==False]=0

		nc_in = Dataset(in_file, "r")
		out_file='sftof/sftof_'+model+'_from_sftlft.nc'
		os.system('rm '+out_file)
		nc_out=Dataset(out_file,"w")
		for dname, the_dim in nc_in.dimensions.iteritems():
			nc_out.createDimension(dname, len(the_dim) if not the_dim.isunlimited() else None)
		for v_name, varin in nc_in.variables.iteritems():
			if v_name=='sftlf':
				v_name='sftof'
			outVar = nc_out.createVariable(v_name, varin.datatype, varin.dimensions)
			outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})
			if v_name=='sftof':	outVar[:] = lf.values
			else:	outVar[:] = varin[:]
		nc_out.close()
		nc_in.close()

		Popen('cdo remapdis,blend-runnable/grid1x1.cdo '+out_file+' sftof/'+model+'.nc',shell=True).wait()
