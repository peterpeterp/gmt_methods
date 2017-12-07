import os,glob,sys
from subprocess import Popen

variable={'tas':'Amon','sic':'OImon','tos':'Omon'}

model='HadGEM2-AO'
run='r1i1p1'

os.chdir('data_models/'+model+'_'+run+'/')

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
