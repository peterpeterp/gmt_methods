import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import itertools
import matplotlib
from scipy import stats


gmt_all=da.read_nc('data/gmt_model.nc')['gmt']
models=list(gmt_all.model)
#models.remove('CESM1-CAM5')
#models.remove('MIROC5')
#models.remove('BNU-ESM')
#models.remove('bcc-csm1-1-m')

gmt_=gmt_all[gmt_all.style,gmt_all.scenario,models,gmt_all.variable,gmt_all.time]

levels=[1.5,1.65]

wlvls=da.DimArray(axes=[['rcp26','rcp45','rcp85'],models,levels],dims=['scenario','model','level'])

missing_gmt=open('data/missing_gmt_in_wlcalc.txt','w')

try:
	os.chdir('/p/projects/tumble/carls/shared_folder/wlcalculator/app/')
	sys.path.append('/p/projects/tumble/carls/shared_folder/wlcalculator/app/')
	os.chdir('../../gmt/')
except:
	sys.path.append('/Users/peterpfleiderer/Documents/Projects/wlcalculator/app/')

os.system('ls')
import wacalc.CmipData as CmipData; reload(CmipData)


for model in gmt_.model:
	for scenario in gmt_.scenario:
		try:
			cmipdata = CmipData.CmipData('CMIP5',[model.lower()],[scenario],cmip5_path='../../data/cmip5_ver003')
			cmipdata.get_cmip()
			cmipdata.compute_period( [1986,2006], [1850,1900], levels, window=21)
			lvls=cmipdata.exceedance_tm
			wlvls[scenario,model,:]=cmipdata.exceedance_tm
		except Exception as e:
			print '--------',model,'------'
			print e
			missing_gmt.write(model+scenario+'\n')


missing_gmt.close()

ds=da.Dataset({'wlvls':wlvls})
ds.write_nc('data/wlvls.nc', mode='w')

# write period table
period_table=open('model_period_table.txt','w')
for model in gmt_.model:
	period_table.write('\t'.join([model,str(wlvls['rcp85',model,1.5]),str(wlvls['rcp85',model,1.65])])+'\n')
period_table.close()


# for folder in [fl.split('/')[-1] for fl in glob.glob('data/*')]:
# 	model=folder.split('_')[0]
# 	run=folder.split('_')[1]
# 	for scenario in ['rcp26','rcp45','rcp85']:
# 		if len(glob.glob('data/'+model+'_'+run+'/*'+scenario+'*.nc'))==3:
#
