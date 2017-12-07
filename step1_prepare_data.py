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

for scenario,selyear in zip(['rcp85','historical'],['2006/2100','1850/2005']):
	for var,group in zip(variable.keys(),variable.values()):
		print scenario,var,group
		print model,run

		command='cdo -a mergetime '
		scenario_files=glob.glob('/p/projects/ipcc_pcmdi/ipcc_ar5_pcmdi/pcmdi_data/'+scenario+'/'+group+'/'+var+'/'+model+'/'+run+'/*')
		if len(scenario_files)!=0 and (os.path.isfile(var+'_'+scenario+'.nc')==False or overwrite):
			for file in scenario_files:
				print file
				command+=file+' '
			Popen(command+'tmp_m_'+var+'.nc',shell=True).wait()

			Popen('cdo selyear,'+selyear+' tmp_m_'+var+'.nc tmp_s_'+var+'.nc',shell=True).wait()
			Popen('cdo remapdis,../../blend-runnable/grid1x1.cdo tmp_s_'+var+'.nc '+var+'_'+scenario+'.nc',shell=True).wait()
			#Popen('rm tmp_s_'+var+'.nc tmp_m_'+var+'.nc',shell=True).wait()

			asdasd
