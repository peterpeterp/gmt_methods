import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date

#cdo -a remapnn,../blend-runnable/grid5x5.cdo -selyear,1850/2016 -selvar,temperature_anomaly CRUTEM.4.6.0.0.anomalies.nc CRU.nc
#cdo -a remapnn,../blend-runnable/grid5x5.cdo -selyear,1850/2016 -selvar,sst HadSST.3.1.1.0.median.nc SST.nc
#cdo -a remapnn,../blend-runnable/grid1x1.cdo -selyear,1850/2016 -selvar,temperature_anomaly HadCRUT.4.6.0.0.median.nc Had4.nc

# CRU
nc = Dataset('blend-runnable/CRU.nc', "r")
lats1 = nc.variables["lat"][:]
lons1 = nc.variables["lon"][:]
time = nc.variables["time"][:]
tas = nc.variables["temperature_anomaly"][:,:,:]
nc.close()

coverage=np.ma.getdata(tas[0:12,:,:])*0
ref_period=np.where((time>19850000) & (time<20150000))[0]
time_in_year=[t-int(t/10000.)*10000 for t in time[ref_period]]
month=[int(t/100.)-1 for t in time_in_year]
for i,t in zip(range(len(ref_period)),ref_period):
	coverage[month[i],:,:]+=np.ma.getmask(tas[t,:,:])
coverage[coverage>10]=np.nan

coverage=np.ma.masked_invalid(coverage)
coverage_ext=tas[0:1032,:,:].copy()
for i,m in zip(range(1032),range(12)*86):
	coverage_ext[i,:,:]=coverage[m,:,:]

tas_ext=np.concatenate((tas,coverage_ext),axis=0)

time_ext=time.copy()
for year in range(2015,2101):
	extension=time[0:12]-18610000+year*10000
	time_ext=np.concatenate((time_ext,extension))


nc_in = Dataset('blend-runnable/CRU.nc', "r")

# copy netcdf and write zoomed file
out_file='data/CRU_extended_old.nc'
os.system("rm "+out_file)
nc_out=Dataset(out_file,"w")
for dname, the_dim in nc_in.dimensions.iteritems():
	nc_out.createDimension(dname, len(the_dim) if not the_dim.isunlimited() else None)

# Copy variables
for v_name, varin in nc_in.variables.iteritems():
	print v_name
	outVar = nc_out.createVariable(v_name, varin.datatype, varin.dimensions)

	# Copy variable attributes
	outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})

	if v_name=='time':	outVar[:] = time_ext
	elif v_name=='temperature_anomaly':	outVar[:] = tas_ext

	else:	outVar[:] = varin[:]


# close the output file
nc_out.close()
nc_in.close()
print out_file

#SST
nc = Dataset('blend-runnable/SST.nc', "r")
lats1 = nc.variables["lat"][:]
lons1 = nc.variables["lon"][:]
time = nc.variables["time"][:]
tas = nc.variables["sst"][:,:,:]
nc.close()

coverage=np.ma.getdata(tas[0:12,:,:])*0
ref_period=np.where((time>19850000) & (time<20150000))[0]
time_in_year=[t-int(t/10000.)*10000 for t in time[ref_period]]
month=[int(t/100.)-1 for t in time_in_year]
for i,t in zip(range(len(ref_period)),ref_period):
	coverage[month[i],:,:]+=np.ma.getmask(tas[t,:,:])
coverage[coverage>10]=np.nan

coverage=np.ma.masked_invalid(coverage)
coverage_ext=tas[0:1032,:,:].copy()
for i,m in zip(range(1032),range(12)*86):
	coverage_ext[i,:,:]=coverage[m,:,:]

tas_ext=np.concatenate((tas,coverage_ext),axis=0)

time_ext=time.copy()
for year in range(2015,2101):
	extension=time[0:12]-18610000+year*10000
	time_ext=np.concatenate((time_ext,extension))


nc_in = Dataset('blend-runnable/SST.nc', "r")

# copy netcdf and write zoomed file
out_file='data/SST_extended_old.nc'
os.system("rm "+out_file)
nc_out=Dataset(out_file,"w")
for dname, the_dim in nc_in.dimensions.iteritems():
	nc_out.createDimension(dname, len(the_dim) if not the_dim.isunlimited() else None)

# Copy variables
for v_name, varin in nc_in.variables.iteritems():
	print v_name
	outVar = nc_out.createVariable(v_name, varin.datatype, varin.dimensions)

	# Copy variable attributes
	outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})

	if v_name=='time':	outVar[:] = time_ext
	elif v_name=='sst':	outVar[:] = tas_ext

	else:	outVar[:] = varin[:]


# close the output file
nc_out.close()
nc_in.close()
print out_file


#Had4
nc = Dataset('blend-runnable/Had4.nc', "r")
lats1 = nc.variables["lat"][:]
lons1 = nc.variables["lon"][:]
time = nc.variables["time"][:]
tas = nc.variables["temperature_anomaly"][:,:,:]
nc.close()

coverage=np.ma.getdata(tas[0:12,:,:])*0
ref_period=np.where((time>19850000) & (time<20150000))[0]
time_in_year=[t-int(t/10000.)*10000 for t in time[ref_period]]
month=[int(t/100.)-1 for t in time_in_year]
for i,t in zip(range(len(ref_period)),ref_period):
	coverage[month[i],:,:]+=np.ma.getmask(tas[t,:,:])
coverage[coverage>10]=np.nan

coverage=np.ma.masked_invalid(coverage)
coverage_ext=tas[0:1032,:,:].copy()
for i,m in zip(range(1032),range(12)*86):
	coverage_ext[i,:,:]=coverage[m,:,:]


tas_ext=np.concatenate((tas,coverage_ext),axis=0)

time_ext=time.copy()
for year in range(2015,2101):
	extension=time[0:12]-18610000+year*10000
	time_ext=np.concatenate((time_ext,extension))


nc_in = Dataset('blend-runnable/Had4.nc', "r")

# copy netcdf and write zoomed file
out_file='data/Had_extended_old.nc'
os.system("rm "+out_file)
nc_out=Dataset(out_file,"w")
for dname, the_dim in nc_in.dimensions.iteritems():
	nc_out.createDimension(dname, len(the_dim) if not the_dim.isunlimited() else None)

# Copy variables
for v_name, varin in nc_in.variables.iteritems():
	print v_name
	outVar = nc_out.createVariable(v_name, varin.datatype, varin.dimensions)

	# Copy variable attributes
	outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})

	if v_name=='time':	outVar[:] = time_ext
	elif v_name=='temperature_anomaly':	outVar[:] = tas_ext

	else:	outVar[:] = varin[:]


# close the output file
nc_out.close()
nc_in.close()
print out_file
