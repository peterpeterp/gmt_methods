import os,glob,sys
from subprocess import Popen


variable={'sic':'OImon'}

overwrite=True

os.chdir('data/')
scenario='rcp85'
var='sic'
group='OImon'
for model in [file.split('/')[-1] for file in glob.glob('/p/projects/ipcc_pcmdi/ipcc_ar5_pcmdi/pcmdi_data/'+scenario+'/'+group+'/'+var+'/*')]:
	if model in [file.split('/')[-1] for file in glob.glob('/p/projects/ipcc_pcmdi/ipcc_ar5_pcmdi/pcmdi_data/historical/'+group+'/'+var+'/*')]:
		for run in [file.split('/')[-1] for file in glob.glob('/p/projects/ipcc_pcmdi/ipcc_ar5_pcmdi/pcmdi_data/'+scenario+'/'+group+'/'+var+'/'+model+'/*')]:
			if run in [file.split('/')[-1] for file in glob.glob('/p/projects/ipcc_pcmdi/ipcc_ar5_pcmdi/pcmdi_data/historical/'+group+'/'+var+'/'+model+'/*')]:
				print model,run
				Popen('mkdir '+model+'_'+run, shell=True).wait()
				os.chdir(model+'_'+run+'/')

				command='cdo -a mergetime '
				hist_files=glob.glob('/p/projects/ipcc_pcmdi/ipcc_ar5_pcmdi/pcmdi_data/historical/'+group+'/'+var+'/'+model+'/'+run+'/*')
				scenario_files=glob.glob('/p/projects/ipcc_pcmdi/ipcc_ar5_pcmdi/pcmdi_data/'+scenario+'/'+group+'/'+var+'/'+model+'/'+run+'/*')
				if len(scenario_files)!=0 and (os.path.isfile(var+'_'+scenario+'.nc')==False or overwrite):
					for file in hist_files+scenario_files:
						print file
						command+=file+' '
					Popen(command+'tmp_m_'+var+'.nc',shell=True).wait()

					Popen('cdo selyear,1850/2100 tmp_m_'+var+'.nc tmp_s_'+var+'.nc',shell=True).wait()
					Popen('cdo remapdis,../../blend-runnable/grid1x1.cdo tmp_s_'+var+'.nc '+var+'_'+scenario+'.nc',shell=True).wait()
					Popen('rm tmp_s_'+var+'.nc tmp_m_'+var+'.nc',shell=True).wait()

				os.chdir('../')
