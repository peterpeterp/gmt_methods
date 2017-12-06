import os,glob,sys
from subprocess import Popen

overwrite=True

job_id=int(os.environ.get('SLURM_ARRAY_TASK_ID'))
if job_id>=90:
	style='xax'
	job_id-=90
else:
	style='had4'


print [fl.split('/')[-1] for fl in glob.glob('data_models/*')]
folder=[fl.split('/')[-1] for fl in glob.glob('data_models/*')][job_id]
print folder
model=folder.split('_')[0]
run=folder.split('_')[1]
if len(glob.glob('sftof/'+model+'.nc'))!=0:
	sftof=glob.glob('sftof/'+model+'.nc')[0]
	scenario = 'rcp85'
	if len(glob.glob('data_models/'+model+'_'+run+'/*'+scenario+'*.nc'))==3:
		tas='data_models/'+model+'_'+run+'/tas_'+scenario+'.nc'
		tos='data_models/'+model+'_'+run+'/tos_'+scenario+'.nc'
		sic='data_models/'+model+'_'+run+'/sic_'+scenario+'.nc'

		if style=='xax':
			if os.path.isfile(style+'_'+scenario+'_old_mask.txt')==False or overwrite:
				Popen('python blend-runnable/ncblendmask-nc4.py '+style+' '+tas+' '+tos+' '+sic+' '+sftof+' > data_models/'+model+'_'+run+'/'+style+'_'+scenario+'_old_mask.txt',shell=True).wait()

		if style=='had4':
			if os.path.isfile('had4_'+scenario+'_old_mask.txt')==False or overwrite:
				Popen('python blend-runnable/ncblendhadcrut-nc4.py '+tas+' '+tos+' '+sic+' '+sftof+'  data/CRU_extended_old.nc data/SST_extended_old.nc > data_models/'+model+'_'+run+'/had4_'+scenario+'_old_mask.txt',shell=True).wait()
