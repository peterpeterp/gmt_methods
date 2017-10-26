import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import pandas as pd

models=['ACCESS1-0', 'ACCESS1-3', 'IPSL-CM5B-LR', 'MIROC5', 'FIO-ESM', 'CMCC-CMS', 'MPI-ESM-LR', 'MIROC-ESM', 'HadGEM2-AO', 'CanESM2', 'MPI-ESM-MR', 'CSIRO-Mk3-6-0', 'MRI-CGCM3', 'CESM1-BGC', 'inmcm4', 'GISS-E2-R-CC', 'BNU-ESM', 'CCSM4', 'GFDL-ESM2G', 'EC-EARTH', 'GFDL-ESM2M', 'NorESM1-M', 'IPSL-CM5A-MR', 'IPSL-CM5A-LR', 'GFDL-CM3', 'CNRM-CM5', 'GISS-E2-H', 'MIROC-ESM-CHEM', 'CSIRO-Mk3L-1-2', 'NorESM1-ME', 'CMCC-CM', 'GISS-E2-R', 'HadGEM2-CC', 'GISS-E2-H-CC', 'bcc-csm1-1-m', 'HadGEM2-ES', 'bcc-csm1-1', 'CESM1-CAM5']

runs=['r3i2p1', 'r12i1p1', 'r5i1p3', 'r6i1p1', 'r5i1p1', 'r8i1p1', 'r1i1p3', 'r1i1p2', 'r1i1p1', 'r5i1p2', 'r6i1p3', 'r7i1p1', 'r9i1p1', 'r4i1p2', 'r4i1p3', 'r4i1p1', 'r10i1p1', 'r2i2p1', 'r2i1p1', 'r2i1p2', 'r2i1p3', 'r1i2p1', 'r3i1p1', 'r3i1p3', 'r3i1p2']

models=[]
runs=[]
for folder in [fl.split('/')[-1] for fl in glob.glob('data/*')]:
	models.append(folder.split('_')[0])
	runs.append(folder.split('_')[1])

models=list(set(models))
runs=list(set(runs))

print models
print runs
styles=['xxx', 'mxx', 'xax', 'max', 'xxf', 'mxf', 'xaf', 'maf','had4']

variables=['air','gmt','time']

#gmt=da.DimArray(axes=[styles,['rcp26','rcp45','rcp85'],models,runs,variables,np.arange(0,2880)],dims=['style','model','run','scenario','variable','time'])


gmt=da.DimArray(axes=[styles,['rcp26','rcp45','rcp85'],models,variables,np.arange(0,2880)],dims=['style','scenario','model','variable','time'])


for style in ['xxx', 'mxx', 'xax', 'max', 'xxf', 'mxf', 'xaf', 'maf','had4']:
	print style
	for scenario in ['rcp26','rcp45','rcp85']:
		print scenario
		for model,mo in zip(models,range(len(models))):
			runs=[fl.split('/')[-1] for fl in glob.glob('data/'+model+'*')]

			gmt_tmp=np.zeros([len(runs),2880])*np.nan
			air_tmp=np.zeros([len(runs),2880])*np.nan
			for folder,i in zip(runs,range(len(runs))):
				run=folder.split('_')[1]
				if len(glob.glob('data/'+model+'_'+run+'/*'+scenario+'*.txt'))!=0:
					try:
						tmp=pd.read_table('data/'+model+'_'+run+'/'+style+'_'+scenario+'.txt',sep=' ',header=None)
						tmp.columns=[0,1,2,3]
						if len(tmp[0])==2880:
							gmt_tmp[i,:]=tmp[2]
							air_tmp[i,:]=tmp[1]
							gmt[style][scenario][model]['time']=tmp[0]
					except:
						pass

			gmt[style][scenario][model]['gmt']=np.nanmean(gmt_tmp,axis=0)
			gmt[style][scenario][model]['air']=np.nanmean(air_tmp,axis=0)



ds=da.Dataset({'gmt':gmt})
ds.write_nc('gmt.nc', mode='w')

# gmt=da.read_nc('gmt_raw.nc')['gmt']
#
# gmt__=da.DimArray(axes=[styles,['rcp26','rcp45','rcp85'],models,variables,np.arange(0,2880)],dims=['style','scenario','model','variable','time'])
#
# for model,mo in zip(models,range(len(models))):
# 	for style,st in zip(styles,range(len(styles))):
# 		for scenario,se in zip(['rcp26','rcp45','rcp85'],range(3)):
# 			print gmt.ix[st,se,mo,:,1,1:10]
# 			gmt__[style][scenario][model]['air']=np.nanmean(gmt.ix[st,se,mo,:,0,:],axis=0)
# 			gmt__[style][scenario][model]['gmt']=np.nanmean(gmt.ix[st,se,mo,:,1,:],axis=0)
# 			gmt__[style][scenario][model]['time']=np.nanmean(gmt.ix[st,se,mo,:,2,:],axis=0)
#
# ds=da.Dataset({'gmt':gmt__})
# ds.write_nc('gmt.nc', mode='w')
