import os,glob,sys
from subprocess import Popen

overwrite=True

try:
	job_id=int(os.environ.get('SLURM_ARRAY_TASK_ID'))
	if job_id>=90:
		style='had4'
		job_id-=90
	else:
		style='xax'

	print [fl.split('/')[-1] for fl in glob.glob('data_models/*')],len([fl.split('/')[-1] for fl in glob.glob('data_models/*')])
	folder=[fl.split('/')[-1] for fl in glob.glob('data_models/*')][job_id]
	print folder
	model=folder.split('_')[0]
	run=folder.split('_')[1]

except:
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("--overwrite",'-o', help="overwrite output files",action="store_true")
	parser.add_argument('--model','-m',help='model name',required=True)
	parser.add_argument('--run','-r' ,help='run name',required=True)
	parser.add_argument('--style','-s' ,help='blending-masking style',required=True)
	args = parser.parse_args()

	if args.overwrite:
	    overwrite=True
	else:
	    overwrite=False

	model=args.model
	run=args.run
	style=args.style



scenario = 'rcp85'

# some replacements because sftof missing
# some replacements because of bad sftof file
sftof_replace_dict={'HadGEM2-AO':'HadGEM2-ES',
					'GISS-E2-R-CC':'GISS-E2-R',
					'GISS-E2-H-CC':'GISS-E2-H',
					'CanESM2':'ACCESS1-0',
					'IPSL-CM5A-LR':'ACCESS1-0',
					'IPSL-CM5A-MR':'ACCESS1-0',
					'IPSL-CM5B-LR':'ACCESS1-0',
					'CNRM-CM5':'CNRM-CM5-2',
					'BNU-ESM':'ACCESS1-0',
					'CESM1-CAM5':'ACCESS1-0'
					} #'CESM1-CAM5':'CESM1-BGC'



# As the blending scripts struggle when the time axis isn't complete, I extended some files with nans (see step1_checkand extend_data.py)
if os.path.isfile('data_models/'+model+'_'+run+'/tas_'+scenario+'_extended.nc') and style=='had4':
	tas='data_models/'+model+'_'+run+'/tas_'+scenario+'_extended.nc'
else:
	tas='data_models/'+model+'_'+run+'/tas_'+scenario+'.nc'

if os.path.isfile('data_models/'+model+'_'+run+'/tos_'+scenario+'_extended.nc') and style=='had4':
	tos='data_models/'+model+'_'+run+'/tos_'+scenario+'_extended.nc'
else:
	tos='data_models/'+model+'_'+run+'/tos_'+scenario+'.nc'

if os.path.isfile('data_models/'+model+'_'+run+'/sic_'+scenario+'_extended.nc') and style=='had4':
	sic='data_models/'+model+'_'+run+'/sic_'+scenario+'_extended.nc'
else:
	sic='data_models/'+model+'_'+run+'/sic_'+scenario+'.nc'


# this for loop was introduced to test the influence of different sftof remap styles - obsolete now
for sftof_style in ['']:
	if model in sftof_replace_dict.keys():
		sftof='sftof/'+sftof_replace_dict[model]+sftof_style+'.nc'
	else:
		sftof='sftof/'+model+sftof_style+'.nc'

	if style=='xax':
		if os.path.isfile(style+'_'+scenario+'.txt')==False or overwrite:
			Popen('python gmt_methods/ncblendmask-nc4.py '+style+' '+tas+' '+tos+' '+sic+' '+sftof+' > data_models/'+model+'_'+run+'/'+style+'_'+scenario+sftof_style+'.txt',shell=True).wait()

	if style=='xxx':
		if os.path.isfile(style+'_'+scenario+'.txt')==False or overwrite:
			Popen('python gmt_methods/ncblendmask-nc4.py '+style+' '+tas+' '+tos+' '+sic+' '+sftof+' > data_models/'+model+'_'+run+'/'+style+'_'+scenario+sftof_style+'.txt',shell=True).wait()


	if style=='had4':
		if os.path.isfile('had4_'+scenario+'.txt')==False or overwrite:
			Popen('python gmt_methods/ncblendhadcrut-nc4.py '+tas+' '+tos+' '+sic+' '+sftof+'  data/CRU_extended.nc data/SST_extended.nc > data_models/'+model+'_'+run+'/had4_'+scenario+sftof_style+'.txt',shell=True).wait()


# python blend-runnable/ncblendmask-nc4.py xax data_models/CanESM2_r1i1p1/tas_rcp85.nc data_models/CanESM2_r1i1p1/tos_rcp85.nc data_models/CanESM2_r1i1p1/sic_rcp85.nc sftof/GFDL-CM3.nc > test.txt

# python blend-runnable/ncblendmask-nc4.py xax data_models/CanESM2_r2i1p1/tas_rcp85.nc data_models/CanESM2_r2i1p1/tos_.nc data_models/CanESM2_r2i1p1/sic_.nc data_models/CanESM2_r2i1p1/sftof_NaN1_1x1.nc > test.txt

# python blend-runnable/ncblendhadcrut-nc4.py data_models/ACCESS1-0_r1i1p1/tas_rcp85_merged.nc data_models/ACCESS1-0_r1i1p1/tos_rcp85_merged.nc data_models/ACCESS1-0_r1i1p1/sic_rcp85_merged.nc sftof/ACCESS1-0.nc data/CRU_extended_old.nc data/SST_extended_old.nc > test.txt
