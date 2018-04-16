import os,glob,sys
from subprocess import Popen

overwrite=True

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--overwrite",'-o', help="overwrite output files",action="store_true")
parser.add_argument('--model','-m',help='model name',required=True)
parser.add_argument('--run','-r' ,help='run name',required=True)
args = parser.parse_args()

if args.overwrite:
    overwrite=True
else:
    overwrite=False

model=args.model
run=args.run

if model is not None and run is not None:
	model_runs=[model+'_'+run]

else:
	print [fl.split('/')[-1] for fl in glob.glob('data_models/*')],len([fl.split('/')[-1] for fl in glob.glob('data_models/*')])
	model_runs=[fl.split('/')[-1] for fl in glob.glob('data_models/*')]


scenario = 'rcp85'
style='xxx'

for model_run in model_runs:
	print model_run
	model=model_run.split('_')[0]
	run=model_run.split('_')[1]

	# As the blending scripts struggle when the time axis isn't complete, I extended some files with nans (see step1_checkand extend_data.py)

	tas='data_models/'+model+'_'+run+'/tas_'+scenario+'.nc'
	tos='data_models/'+model+'_'+run+'/tos_'+scenario+'.nc'
	sic='data_models/'+model+'_'+run+'/sic_'+scenario+'.nc'

	if model in sftof_replace_dict.keys():
		sftof='sftof/'+sftof_replace_dict[model]+'.nc'
	else:
		sftof='sftof/'+model+'.nc'

	if os.path.isfile(style+'_'+scenario+'.txt')==False or overwrite:
		Popen('python gmt_methods/ncblendmask-nc4.py '+style+' '+tas+' '+tos+' '+sic+' '+sftof+' > data_models/'+model+'_'+run+'/'+style+'_'+scenario+'.txt',shell=True).wait()
