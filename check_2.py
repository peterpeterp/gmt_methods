import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import pandas as pd
import seaborn as sns
import itertools
import matplotlib

try:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/gmt/')
except:
	os.chdir('/p/projects/tumble/carls/shared_folder/gmt/')

gmt=da.read_nc('data/gmt_all_remapdis_50.nc')['gmt']
grid_sizes=[]
for model_run in gmt.model_run:
	try:
		tmp=da.read_nc('sftof/sftof_fx_'+model_run.split('_')[0]+'_historical_r0i0p0.nc')
		try:
			grid_sizes.append(tmp['i'].shape[0]*tmp['j'].shape[0])
		except:
			grid_sizes.append(tmp['lat'].shape[0]*tmp['lon'].shape[0])
	except:
		grid_sizes.append(0)

model_runs_df=pd.DataFrame(np.array([gmt.model_run,grid_sizes]).T,columns=['name','size'])

for sftof_style in ['_remapdis']:
	gmt=da.read_nc('data/gmt_all'+sftof_style+'.nc')['gmt']
	for style,var,title in zip(['xax','xax'],['air','gmt'],['SAT unmasked','Blended air/sea temperature, unmasked, temperature anomalies, variable ice']):
		plt.close()
		fig,axes=plt.subplots(nrows=9,ncols=10,figsize=(12,15))
		axes=axes.flatten()
		for model_run,ax,i in zip(model_runs_df.sort_values(by=['name'],ascending=False)['name'],axes[0:len(gmt.model_run)],range(len(gmt.model_run))):
			cowtan_file='blend-results.160518/rcp85-'+style+'/rcp85_'+model_run+'.temp'
			if np.isfinite(np.nanmean(gmt[style,'rcp85',model_run,'gmt',:].values)) and os.path.isfile(cowtan_file):
				tmp=pd.read_table(cowtan_file,sep=' ',header=None)
				tmp.columns=['time','air','gmt','diff']
				perc_diff=(gmt[style,'rcp85',model_run,var,1861:2100].values-np.array(tmp[var]))
				ax.plot(np.array(tmp['time']),perc_diff)
				if model_run=='ACCESS1-0_r1i1p1':
					print perc_diff
				ax.text(1853,0.04,model_run.replace('_','\n'),fontsize=8)
			ax.set_xlim((1850,2100))
			ax.set_ylim((-0.05,0.05))
			ax.get_xaxis().set_visible(False)
			ax.set_yticks([-0.05,-0.025,0,0.025,0.05])
			if i in range(0,90,10):
				ax.set_ylabel('devaiation')
			else:
				ax.set_yticklabels(['','','','',''])

		for ax in axes[85:90]:
			ax.axis('off')

		plt.suptitle(title)
		plt.savefig('plots/check/check_'+style+'_'+var+'_detail'+sftof_style+'.png')
