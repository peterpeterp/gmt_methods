import os,glob,sys
from subprocess import Popen


# combi=open('model-run-combinations_rcp85.txt','w')
# models=[]
# for file in glob.glob('blend-results.160518/rcp85-had4/*'):
# 	model=file.split('_')[1]
# 	run=file.split('_')[2].split('.')[0]
# 	combi.write(model+' '+run+'\n')
# 	models.append(model)
# combi.close()
# models=set(models)

variable={'tas':'Amon','sic':'OImon','tos':'Omon'}

combi=open('model-run-combinations_rcp85.txt','r').read()
missing_tas=open('missing_tas.txt','w')
missing_tos=open('missing_tos.txt','w')
missing_sic=open('missing_sic.txt','w')
missing_sftof=open('missing_sftof.txt','w')
missing_xax=open('missing_xax.txt','w')
missing_had4=open('missing_had4.txt','w')

missing_input={'tas':missing_tas,'sic':missing_sic,'tos':missing_tos,'sftof':missing_sftof}
missing_result={'xax':missing_xax,'had4':missing_had4}

models=[]
for scenario in ['rcp85']:
	for var in variable.keys():
		missing_input[var].write('\n'+scenario+':\n\n')
	for line in combi.splitlines()[0:-1]:
		model=line.split(' ')[0]
		run=line.split(' ')[1]

		for var,group in zip(variable.keys(),variable.values()):
			if run not in [mm.split('/')[-1] for mm in glob.glob('/p/projects/ipcc_pcmdi/ipcc_ar5_pcmdi/pcmdi_data/'+scenario+'/'+group+'/'+var+'/'+model+'/*')]:
				missing_input[var].write(model+' '+run+'\n')

		models.append(model)


for model in set(models):
	if model not in [mm.split('/')[-1].split('.')[0] for mm in glob.glob('sftof/*')]:
		missing_input['sftof'].write(model+'\n')

for scenario in ['rcp85']:
	for var in missing_result.keys():
		missing_result[var].write('\n'+scenario+':\n\n')
		for line in combi.splitlines()[0:-1]:
			model=line.split(' ')[0]
			run=line.split(' ')[1]
			if var not in [mm.split('/')[-1].split('_')[0] for mm in glob.glob('data_models/'+model+'_'+run+'/*')]:
				missing_result[var].write(model+' '+run+'\n')


for text in missing_input.values()+missing_result.values():
	text.close()
