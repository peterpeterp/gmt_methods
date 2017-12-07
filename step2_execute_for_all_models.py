import os,glob,sys
from subprocess import Popen

overwrite=True

for folder in [fl.split('/')[-1] for fl in glob.glob('data_models/*')]:
	print folder
	model=folder.split('_')[0]
	run=folder.split('_')[1]
	if len(glob.glob('sftof/'+model+'.nc'))!=0:
		sftof=glob.glob('sftof/'+model+'.nc')[0]
		for scenario in ['rcp85']:
			if len(glob.glob('data_models/'+model+'_'+run+'/*'+scenario+'*.nc'))==3:
				tas='data_models/'+model+'_'+run+'/tas_'+scenario+'.nc'
				tos='data_models/'+model+'_'+run+'/tos_'+scenario+'.nc'
				sic='data_models/'+model+'_'+run+'/sic_'+scenario+'.nc'
				# for style in ['mxx','max','mxf','maf']:
				# 	if os.path.isfile(style+'_'+scenario+'.txt')==False or overwrite:
				# 		Popen('python blend-runnable/ncblendmask-nc4.py '+style+' '+tas+' '+tos+' '+sic+' '+sftof+'  data/Had_extended.nc > data_models/'+model+'_'+run+'/'+style+'_'+scenario+'.txt',shell=True).wait()
				# for style in ['xxx', 'xax', 'xxf', 'xaf']:
				# 	if os.path.isfile(style+'_'+scenario+'.txt')==False or overwrite:
				# 		Popen('python blend-runnable/ncblendmask-nc4.py '+style+' '+tas+' '+tos+' '+sic+' '+sftof+' > data_models/'+model+'_'+run+'/'+style+'_'+scenario+'.txt',shell=True).wait()
				if os.path.isfile('had4_'+scenario+'.txt')==False or overwrite:
					Popen('python blend-runnable/ncblendhadcrut-nc4.py '+tas+' '+tos+' '+sic+' '+sftof+'  data/CRU_extended.nc data/SST_extended.nc > data_models/'+model+'_'+run+'/had4_'+scenario+'.txt',shell=True).wait()






# python blend-runnable/ncblendhadcrut-nc4.py data_models/ACCESS1-0_r1i1p1/tas_rcp85.nc data_models/ACCESS1-0_r1i1p1/tos_rcp85.nc data_models/ACCESS1-0_r1i1p1/sic_rcp85.nc sftof/ACCESS1-0.nc data/CRU_extended.nc data/SST_extended.nc > test.txt

# python blend-runnable/ncblendhadcrut-nc4.py data_models/EC-EARTH_r14i1p1/tas_rcp85.nc data_models/EC-EARTH_r14i1p1/tos_rcp85.nc data_models/EC-EARTH_r14i1p1/sic_rcp85.nc sftof/ACCESS1-0.nc data/CRU_extended_old.nc data/SST_extended_old.nc > test.txt
