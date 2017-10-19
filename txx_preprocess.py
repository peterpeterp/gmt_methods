import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import itertools
import matplotlib
from scipy import stats



gmt_all=da.read_nc('data/gmt.nc')['gmt']
models=list(gmt_all.model)
models.remove('CESM1-CAM5')
models.remove('MIROC5')
models.remove('BNU-ESM')
models.remove('bcc-csm1-1-m')

gmt_=gmt_all[gmt_all.style,gmt_all.scenario,models,gmt_all.variable,gmt_all.time]

wlvls=da.DimArray(axes=[['rcp26','rcp45','rcp85'],models,[1.489,1.5,1.587,1.695]],dims=['scenario','model','level'])

missing_gmt=open('data/missing_gmt_in_wlcalc.txt','w')

os.chdir('../wlcalculator/app/')
import wacalc.CmipData as CmipData; reload(CmipData)


for model in gmt_.model:
	for scenario in gmt_.scenario:
		try:
			cmipdata = CmipData.CmipData('CMIP5',[model.lower()],[scenario])
			cmipdata.get_cmip()
			cmipdata.compute_period( [1986,2006], [1850,1900], [1.489,1.5,1.587,1.695], window=21)
			lvls=cmipdata.exceedance_tm
			wlvls[scenario,model,:]=cmipdata.exceedance_tm
		except Exception as e:
			print '--------',model,'------'
			print e
			missing_gmt.write(model+scenario+'\n')

os.chdir('../../gmt/')

missing_gmt.close()

ds=da.Dataset({'wlvls':wlvls})
ds.write_nc('data/wlvls.nc', mode='w')


# for folder in [fl.split('/')[-1] for fl in glob.glob('data/*')]:
# 	model=folder.split('_')[0]
# 	run=folder.split('_')[1]
# 	for scenario in ['rcp26','rcp45','rcp85']:
# 		if len(glob.glob('data/'+model+'_'+run+'/*'+scenario+'*.nc'))==3:
#
