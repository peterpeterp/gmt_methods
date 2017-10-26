import os,glob,sys
from subprocess import Popen


variable={'tas':'Amon','sic':'OImon','tos':'Omon'}



os.chdir('data/')
for scenario in ['rcp26','rcp45','rcp85']:
	for var,group in zip(variable.keys(),variable.values()):
		print scenario,var,group
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
						if len(scenario_files)!=0 and os.path.isfile(var+'_'+scenario+'.nc')==False:
							for file in hist_files+scenario_files:
								print file
								command+=file+' '
							Popen(command+'tmp_m_'+var+'.nc',shell=True).wait()

							Popen('cdo selyear,1861/2100 tmp_m_'+var+'.nc tmp_s_'+var+'.nc',shell=True).wait()
							Popen('cdo remapdis,../../blend-runnable/grid1x1.cdo tmp_s_'+var+'.nc '+var+'_'+scenario+'.nc',shell=True).wait()
							Popen('rm tmp_s_'+var+'.nc tmp_m_'+var+'.nc',shell=True).wait()

						os.chdir('../')



# combi=open('model-run-combinations.txt','r').read()

# os.chdir('data/')
# for line in combi.splitlines():
# 	model=line.split(' ')[0]
# 	run=line.split(' ')[1]
# 	Popen('mkdir '+model+'_'+run, shell=True).wait()
# 	os.chdir(model+'_'+run+'/')
# 	for scenario in ['rcp26','rcp45','rcp85']:
# 		for var,group in zip(variable.keys(),variable.values()):
# 			command='cdo -a mergetime '
# 			hist_files=glob.glob('/p/projects/ipcc_pcmdi/ipcc_ar5_pcmdi/pcmdi_data/historical/'+group+'/'+var+'/'+model+'/'+run+'/*')
# 			scenario_files=glob.glob('/p/projects/ipcc_pcmdi/ipcc_ar5_pcmdi/pcmdi_data/'+scenario+'/'+group+'/'+var+'/'+model+'/'+run+'/*')
# 			if len(scenario_files)!=0:
# 				for file in hist_files+scenario_files:
# 					print file
# 					command+=file+' '
# 				Popen(command+'tmp_m_'+var+'.nc',shell=True).wait()

# 				Popen('cdo selyear,1861/2100 tmp_m_'+var+'.nc tmp_s_'+var+'.nc',shell=True).wait()
# 				Popen('cdo remapdis,../../blend-runnable/grid1x1.cdo tmp_s_'+var+'.nc '+var+'_'+scenario+'.nc',shell=True).wait()
# 				Popen('rm tmp_s_'+var+'.nc tmp_m_'+var+'.nc',shell=True).wait()

# 		if len(glob.glob('*'+scenario+'*'))!=3:
# 			Popen('rm '+' '.join(glob.glob('*'+scenario+'*')),shell=True).wait()

# 	os.chdir('../')
# 	# sftof=glob.glob('sftof/*'+model+'*')[0]
# 	# Popen('cdo remapdis,blend-runnable/grid1x1.cdo '+sftof+' data/'+model+'_'+run+'/sftof.nc',shell=True).wait()

# combi.close()

# for file in glob.glob('sftof/sftof_fx_*.nc'):
# 	Popen('cdo remapdis,blend-runnable/grid1x1.cdo '+file+' sftof/'+file.split('_')[2]+'.nc',shell=True).wait()
