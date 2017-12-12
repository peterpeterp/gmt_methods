import os,glob,sys
from subprocess import Popen
import dimarray as da
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date


try:
	os.chdir('/p/projects/tumble/carls/shared_folder/gmt')
except:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/gmt')

print [ff.split('_')[-3] for ff in glob.glob('sftof/sftof_fx_*_historical_r0i0p0.nc')]

#
# for file_name in glob.glob('sftof/sftof_fx_*_historical_r0i0p0.nc'):
# 	model = file_name.split('_')[-2]
# 	Popen('cdo remapdis,blend-runnable/grid1x1.cdo '+file_name+' sftof/'+model+'_remapdis.nc',shell=True).wait()
# 	Popen('cdo remapnn,blend-runnable/grid1x1.cdo '+file_name+' sftof/'+model+'_remapnn.nc',shell=True).wait()

for file_name in glob.glob('sftof/sftof_fx_*.nc'):
	# Popen('cdo remapdis,blend-runnable/grid1x1.cdo '+file_name+' sftof/'+file_name.split('_')[2]+'_remapdis.nc',shell=True).wait()
	# Popen('cdo remapnn,blend-runnable/grid1x1.cdo '+file_name+' sftof/'+file_name.split('_')[2]+'_remapn.nc',shell=True).wait()

	Popen("cdo -expr,'sftof=(sftof<100.0)?0.0:sftof;'  sftof/"+file_name.split('_')[2]+'_remapdis.nc sftof/'+file_name.split('_')[2]+'_remapdis_0.nc',shell=True).wait()
	Popen("cdo -expr,'sftof=(sftof>0.0)?100.0:sftof;' sftof/"+file_name.split('_')[2]+'_remapdis.nc sftof/'+file_name.split('_')[2]+'_remapdis_100.nc',shell=True).wait()
	Popen("cdo -expr,'sftof=(sftof<50.0)?0.0:sftof;' -expr,'sftof=(sftof>50.0)?100.0:sftof;' sftof/"+file_name.split('_')[2]+'_remapdis.nc sftof/'+file_name.split('_')[2]+'_remapdis_50.nc',shell=True).wait()



# for model in [ff.split('/')[-1] for ff in glob.glob('/p/projects/ipcc_pcmdi/ipcc_ar5_pcmdi/pcmdi_data/historical/fx/sftlf/*')]:
# 	if model not in [ff.split('_')[-2] for ff in  glob.glob('sftof/sftof_fx_*_historical_r0i0p0.nc')]:
# 		in_file=glob.glob('/p/projects/ipcc_pcmdi/ipcc_ar5_pcmdi/pcmdi_data/historical/fx/sftlf/'+model+'/*/*')[0]
#
# 		lf=da.read_nc(in_file)['sftlf']
# 		lf[lf>0]=np.nan
# 		lf[lf==0]=100
# 		lf[np.isfinite(lf)==False]=0
#
# 		nc_in = Dataset(in_file, "r")
# 		out_file='sftof/sftof_'+model+'_from_sftlft.nc'
# 		os.system('rm '+out_file)
# 		nc_out=Dataset(out_file,"w")
# 		for dname, the_dim in nc_in.dimensions.iteritems():
# 			nc_out.createDimension(dname, len(the_dim) if not the_dim.isunlimited() else None)
# 		for v_name, varin in nc_in.variables.iteritems():
# 			if v_name=='sftlf':
# 				v_name='sftof'
# 			outVar = nc_out.createVariable(v_name, varin.datatype, varin.dimensions)
# 			outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})
# 			if v_name=='sftof':	outVar[:] = lf.values
# 			else:	outVar[:] = varin[:]
# 		nc_out.close()
# 		nc_in.close()
#
# 		Popen('cdo remapdis,blend-runnable/grid1x1.cdo '+out_file+' sftof/'+model+'_remapdis.nc',shell=True).wait()
# 		Popen('cdo remapnn,blend-runnable/grid1x1.cdo '+out_file+' sftof/'+model+'_remapnn.nc',shell=True).wait()
