import os,glob,sys
from subprocess import Popen


combi=open('model-run-combinations.txt','r').read()

for folder in [fl.split('/')[-1] for fl in glob.glob('data/*')]:
	model=folder.split('_')[0]
	run=folder.split('_')[1]
	if len(glob.glob('sftof/'+model+'.nc'))!=0:
		sftof=glob.glob('sftof/'+model+'.nc')[0]
		for scenario in ['rcp26','rcp45','rcp85']:
			if len(glob.glob('data/'+model+'_'+run+'/*'+scenario+'*.nc'))==3:
				tas=glob.glob('data/'+model+'_'+run+'/tas_'+scenario+'.nc')[0]
				tos=glob.glob('data/'+model+'_'+run+'/tos_'+scenario+'.nc')[0]
				sic=glob.glob('data/'+model+'_'+run+'/sic_'+scenario+'.nc')[0]
				for style in ['mxx','max','mxf','maf']:
					if os.path.isfile(style+'_'+scenario+'.txt')==False:
						Popen('python blend-runnable/ncblendmask-nc4.py '+style+' '+tas+' '+tos+' '+sic+' '+sftof+'  Had_extended.nc > data/'+model+'_'+run+'/'+style+'_'+scenario+'.txt',shell=True).wait()
				for style in ['xxx', 'xax', 'xxf', 'xaf']:
					if os.path.isfile(style+'_'+scenario+'.txt')==False:
						Popen('python blend-runnable/ncblendmask-nc4.py '+style+' '+tas+' '+tos+' '+sic+' '+sftof+' > data/'+model+'_'+run+'/'+style+'_'+scenario+'.txt',shell=True).wait()
				if os.path.isfile('had4_'+scenario+'.txt')==False:
					Popen('python blend-runnable/ncblendhadcrut-nc4.py '+tas+' '+tos+' '+sic+' '+sftof+'  CRU_extended.nc SST_extended.nc > data/'+model+'_'+run+'/had4_'+scenario+'.txt',shell=True).wait()

combi.close()
