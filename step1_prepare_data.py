import os,glob,sys
from subprocess import Popen
try:
	job_id=int(os.environ.get('SLURM_ARRAY_TASK_ID'))
except:
	job_id=1

overwrite=True

folder=[fl.split('/')[-1] for fl in glob.glob('data_models/*')][job_id]
print folder
model=folder.split('_')[0]
run=folder.split('_')[1]

Popen('mkdir data_models/'+model+'_'+run, shell=True).wait()
os.chdir('data_models/'+model+'_'+run+'/')


variable={'tas':'Amon','sic':'OImon','tos':'Omon'}



if model_run=='EC-EARTH_r6i1p1'
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

elif 'Had' in model.split('GEM'):
	for scenario,selyear in zip(['rcp85','historical'],['2005/2100','1850/2005']):
		for var,group in zip(variable.keys(),variable.values()):
			if scenario=='rcp85' and var=='tas':
				print scenario,var,group
				print model,run

				command='cdo -a mergetime '
				scenario_files=glob.glob('/p/projects/ipcc_pcmdi/ipcc_ar5_pcmdi/pcmdi_data/'+scenario+'/'+group+'/'+var+'/'+model+'/'+run+'/*')
				for file_name in scenario_files:
					print file_name
					command+=file_name+' '
				Popen(command+'tmp_m_'+var+'.nc',shell=True).wait()
				Popen('cdo selyear,'+selyear+' tmp_m_'+var+'.nc tmp_s_'+var+'.nc',shell=True).wait()
				Popen('cdo -O remapdis,../../blend-runnable/grid1x1.cdo tmp_s_'+var+'.nc '+var+'_'+scenario+'.nc',shell=True).wait()
				Popen('rm tmp_s_'+var+'.nc tmp_m_'+var+'.nc',shell=True).wait()



# all clean files
else:
	for scenario,selyear in zip(['rcp85','historical'],['2006/2100','1850/2005']):
		for var,group in zip(variable.keys(),variable.values()):
			print scenario,var,group
			print model,run

			command='cdo -a mergetime '
			scenario_files=glob.glob('/p/projects/ipcc_pcmdi/ipcc_ar5_pcmdi/pcmdi_data/'+scenario+'/'+group+'/'+var+'/'+model+'/'+run+'/*')
			if len(scenario_files)!=0 and (os.path.isfile(var+'_'+scenario+'.nc')==False or overwrite):
				for file_name in scenario_files:
					print file_name
					command+=file_name+' '
				Popen(command+'tmp_m_'+var+'.nc',shell=True).wait()

				if model.split('d')[0]=='Ha' and scenario=='rcp85':
					selyear='2005/2100'
				Popen('cdo selyear,'+selyear+' tmp_m_'+var+'.nc tmp_s_'+var+'.nc',shell=True).wait()
				Popen('cdo -O remapdis,../../blend-runnable/grid1x1.cdo tmp_s_'+var+'.nc '+var+'_'+scenario+'.nc',shell=True).wait()
				Popen('rm tmp_s_'+var+'.nc tmp_m_'+var+'.nc',shell=True).wait()
