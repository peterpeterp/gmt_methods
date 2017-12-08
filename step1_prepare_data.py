import os,glob,sys
from subprocess import Popen
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import dimarray as da
import pandas as pd

try:
	os.chdir('/p/projects/tumble/carls/shared_folder/gmt')
except:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/gmt')


try:
	job_id=int(os.environ.get('SLURM_ARRAY_TASK_ID'))
except:
	job_id=1

overwrite=True

folder=[fl.split('/')[-1] for fl in glob.glob('data_models/*')][job_id]
print folder
model=folder.split('_')[0]
run=folder.split('_')[1]
model_run=model+'_'+run

# # fixing
# if 'Had' not in model.split('GEM'):
# 	asdasdas

#Popen('mkdir data_models/'+model+'_'+run, shell=True).wait()
os.chdir('data_models/'+model+'_'+run+'/')


# ++++++++++++++++++++++++++++++
# + get files
# ++++++++++++++++++++++++++++++

variable={'tas':'Amon','sic':'OImon','tos':'Omon'}

def normal_procedure(model,run,scenario,selyear,group,var,overwrite):
	command='cdo -a mergetime '
	scenario_files=glob.glob('/p/projects/ipcc_pcmdi/ipcc_ar5_pcmdi/pcmdi_data/'+scenario+'/'+group+'/'+var+'/'+model+'/'+run+'/*')
	if len(scenario_files)!=0 and (os.path.isfile(var+'_'+scenario+'.nc')==False or overwrite):
		for file_name in scenario_files:
			print file_name
			command+=file_name+' '
		Popen(command+'tmp_m_'+var+'.nc',shell=True).wait()

		Popen('cdo selyear,'+selyear+' tmp_m_'+var+'.nc tmp_s_'+var+'.nc',shell=True).wait()
		Popen('cdo -O remapdis,../../blend-runnable/grid1x1.cdo tmp_s_'+var+'.nc '+var+'_'+scenario+'.nc',shell=True).wait()
		Popen('rm tmp_s_'+var+'.nc tmp_m_'+var+'.nc',shell=True).wait()
	if len(scenario_files)==0:
		info=open('delete_here','w')
		info.write('bla')
		info.close()

if model_run=='EC-EARTH_r6i1p1':
	for scenario,selyear in zip(['rcp85','historical'],['2006/2100','1850/2005']):
		for var,group in zip(variable.keys(),variable.values()):
			if scenario=='rcp85' and var=='tas':
				print scenario,var,group
				print model,run

				command='cdo -a mergetime '
				scenario_files=glob.glob('/p/projects/ipcc_pcmdi/ipcc_ar5_pcmdi/pcmdi_data/'+scenario+'/'+group+'/'+var+'/'+model+'/'+run+'/*')
				for file_name in scenario_files:
					if '205101-210012.nc' not in file_name.split('_') and '200601-205012.nc' not in file_name.split('_'):
						print file_name
						command+=file_name+' '
				Popen(command+'tmp_m_'+var+'.nc',shell=True).wait()
				Popen('cdo selyear,'+selyear+' tmp_m_'+var+'.nc tmp_s_'+var+'.nc',shell=True).wait()
				Popen('cdo -O remapdis,../../blend-runnable/grid1x1.cdo tmp_s_'+var+'.nc '+var+'_'+scenario+'.nc',shell=True).wait()
				Popen('rm tmp_s_'+var+'.nc tmp_m_'+var+'.nc',shell=True).wait()
			else:
				normal_procedure(model,run,scenario,selyear,group,var,overwrite)


elif model=='HadGEM2-AO':
	for scenario,selyear in zip(['rcp85','historical'],['2006/2100','1850/2005']):
		for var,group in zip(variable.keys(),variable.values()):
			if scenario=='rcp85' and var=='tas':
				print scenario,var,group
				print model,run

				command='cdo -a mergetime '
				scenario_files=glob.glob('/p/projects/ipcc_pcmdi/ipcc_ar5_pcmdi/pcmdi_data/'+scenario+'/'+group+'/'+var+'/'+model+'/'+run+'/*')
				for file_name in scenario_files:
					if '200601-209912.nc' not in file_name.split('_'):
						print file_name
						command+=file_name+' '
				Popen(command+'tmp_m_'+var+'.nc',shell=True).wait()
				Popen('cdo selyear,'+selyear+' tmp_m_'+var+'.nc tmp_s_'+var+'.nc',shell=True).wait()
				Popen('cdo -O remapdis,../../blend-runnable/grid1x1.cdo tmp_s_'+var+'.nc '+var+'_'+scenario+'.nc',shell=True).wait()
				Popen('rm tmp_s_'+var+'.nc tmp_m_'+var+'.nc',shell=True).wait()
			else:
				normal_procedure(model,run,scenario,selyear,group,var,overwrite)

elif 'Had' in model.split('GEM'):
	for var,group in zip(variable.keys(),variable.values()):
		scenario_files=glob.glob('/p/projects/ipcc_pcmdi/ipcc_ar5_pcmdi/pcmdi_data/historical/'+group+'/'+var+'/'+model+'/'+run+'/*')
		if '200512.nc' in [ff.split('-')[-1] for ff in scenario_files]:
			for scenario,selyear in zip(['rcp85','historical'],['2006/2100','1850/2005']):
				normal_procedure(model,run,scenario,selyear,group,var,overwrite)
		if '200512.nc' not in [ff.split('-')[-1] for ff in scenario_files]:
			for scenario,selyear in zip(['rcp85','historical'],['2005/2100','1850/2005']):
				normal_procedure(model,run,scenario,selyear,group,var,overwrite)



# all clean files
else:
	for scenario,selyear in zip(['rcp85','historical'],['2006/2100','1850/2005']):
		for var,group in zip(variable.keys(),variable.values()):
			print scenario,var,group
			print model,run
			normal_procedure(model,run,scenario,selyear,group,var,overwrite)



# ++++++++++++++++++++++++++++++
# + merge scenarios
# ++++++++++++++++++++++++++++++

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
