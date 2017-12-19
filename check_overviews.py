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

gmt_raw=da.read_nc('data/gmt_all_remapdis.nc')['gmt']
model_runs=sorted(gmt_raw.model_run)
for model_run in gmt_raw.model_run:
	if model_run.split('_')[0] in ['CESM1-CAM5','BNU-ESM','bcc-csm1-1-m','CESM1-WACCM']:
		model_runs.remove(model_run)
	elif np.isnan(np.nanmean(gmt_raw['xax','rcp85',model_run,'gmt',:].values)):
		model_runs.remove(model_run)

model_runs.remove('EC-EARTH_r7i1p1')
model_runs.remove('EC-EARTH_r11i1p1')
model_runs.remove('EC-EARTH_r12i1p1')
model_runs.remove('EC-EARTH_r13i1p1')
model_runs.remove('EC-EARTH_r14i1p1')

gmt=gmt_raw[gmt_raw.style,gmt_raw.scenario,model_runs,gmt_raw.variable,gmt_raw.time]

for style,var,title in zip(['xax','xax'],['air','gmt'],['SAT unmasked','Blended air/sea temperature, unmasked, temperature anomalies, variable ice']):
	plt.close()
	fig,axes=plt.subplots(nrows=8,ncols=9,figsize=(8,9))
	axes=axes.flatten()
	for model_run,ax,i in zip(gmt.model_run,axes[0:len(gmt.model_run)],range(len(gmt.model_run))):
		cowtan_file='blend-results.160518/rcp85-'+style+'/rcp85_'+model_run+'.temp'
		if np.isfinite(np.nanmean(gmt[style,'rcp85',model_run,'gmt',:].values)) and os.path.isfile(cowtan_file):
			tmp=pd.read_table(cowtan_file,sep=' ',header=None)
			tmp.columns=['time','air','gmt','diff']
			perc_diff=(gmt[style,'rcp85',model_run,var,1861:2100].values-np.array(tmp[var]))
			ax.plot(np.array(tmp['time']),perc_diff)
		ax.text(1853,0.04,model_run.replace('_','\n'),fontsize=8)
		ax.set_xlim((1850,2100))
		ax.set_ylim((-0.05,0.05))
		ax.get_xaxis().set_visible(False)
		ax.set_yticks([-0.05,-0.025,0,0.025,0.05])
		if i in range(0,90,9):
			ax.set_ylabel('devaiation')
		else:
			ax.set_yticklabels(['','','','',''])

	for i in range(68,72):
		axes[i].axis('off')

	plt.suptitle(title)
	plt.savefig('plots/check/check_cowtan_'+style+'_'+var+'_ensemble.png')


def yearly_anomaly(gmt_in,ref_period=[1861,1880]):
	gmt_anom=gmt_in
	# anomaly to preindustrial
	for style in gmt_anom.style:
		for scenario in gmt_anom.scenario:
			for model in gmt_anom.model_run:
				gmt_anom[style,scenario,model,'air',:]-=np.nanmean(gmt_in[style,scenario,model,'air',ref_period[0]:ref_period[1]])
				gmt_anom[style,scenario,model,'gmt',:]-=np.nanmean(gmt_in[style,scenario,model,'gmt',ref_period[0]:ref_period[1]])

	# yearly values
	gmt_year=da.DimArray(axes=[gmt_all.style,gmt_all.scenario,gmt_in.model_run,gmt_all.variable,np.arange(1850,2100,1)],dims=['style','scenario','model_run','variable','time'])
	for model in gmt_year.model_run:
		for style in gmt_year.style:
			for var in gmt_year.variable:
				for year in gmt_year.time:
					gmt_year[style,'rcp85',model,var,year]=np.nanmean(gmt_anom[style,'rcp85',model,var,year:year+1])

	return gmt_year

gmt_year=yearly_anomaly(gmt)

for style,title in zip(['xax','had4'],['Blended unmasked - SAT (1861-2016)','HadCRUT4 emulate - SAT (1861-2916)']):
	plt.close()
	fig,axes=plt.subplots(nrows=8,ncols=9,figsize=(8,9))
	axes=axes.flatten()
	for model_run,ax,i in zip(gmt.model_run,axes[0:len(gmt_year.model_run)],range(len(gmt_year.model_run))):
		if np.isfinite(np.nanmean(gmt_year[style,'rcp85',model_run,'gmt',:].values)):
			diff=(gmt_year[style,'rcp85',model_run,'gmt',:].values-gmt_year['xax','rcp85',model_run,'air',:].values)
			ax.plot(gmt_year.time,diff)
		ax.text(1864,0.03,model_run.replace('_','\n'),fontsize=8)
		ax.set_xlim((1861,2016))
		ax.set_ylim((-0.3,0.1))
		ax.get_xaxis().set_visible(False)
		ax.set_yticks([-0.3,-0.2,0.1,0.0,0.1])
		if i in range(0,90,9):
			ax.set_ylabel('K')
		else:
			ax.set_yticklabels(['','','','',''])

	for i in range(68,72):
		axes[i].axis('off')

	plt.suptitle(title)
	plt.savefig('plots/check/overview_'+style+'_ensemble.png')
