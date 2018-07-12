import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import itertools
import matplotlib
from scipy import stats
import seaborn as sns

os.chdir('/Users/peterpfleiderer/Documents/Projects/gmt')


# these models start in 1861 GFDL-CM3 GFDL-ESM2G GFDL-ESM2M HadGEM2-AO HadGEM2-CC HadGEM2-ES


for mod_style in ['model','runs']:
	for av_style in ['year']:
		for preind_name,preind_period in zip(['1861-1880','1850-1900'],[[1861,1880],[1850,1900]]):
			gmt=da.read_nc('data/gmt_plot_ready_'+av_style+'_'+mod_style+'_'+preind_name+'.nc')['gmt']

			print '********** '+preind_name+' ***** '+av_style+' ******* '+mod_style
			print '1986-2005'
			for style in ['gmt_sat','gmt_bm']:
				print style,np.nanmean(gmt['rcp85',:,style,1986:2005])

			print '2006-2015'
			for style in ['gmt_sat','gmt_bm']:
				print style,np.nanmean(gmt['rcp85',:,style,2006:2015])

			print 'diff 2006-2015',np.nanmean(gmt['rcp85',:,'gmt_sat',2006:2015])-np.nanmean(gmt['rcp85',:,'gmt_bm',2006:2015])


def yearly_anomaly(gmt_in,ref_period=[1861,1880]):
	gmt_anom=gmt_in
	# anomaly to preindustrial
	gmt_anom.values-=np.expand_dims(np.nanmean(gmt_anom[:,:,:,:,ref_period[0]:ref_period[1]].values,axis=4),axis=4)

	# yearly values
	gmt_year=da.DimArray(axes=[gmt_in.style,gmt_in.scenario,gmt_in.model_run,gmt_in.variable,np.arange(1850,2100,1)],dims=['style','scenario','model_run','variable','time'])
	for model in gmt_year.model_run:
		for style in gmt_year.style:
			for var in gmt_year.variable:
				for year in gmt_year.time:
					gmt_year[style,'rcp85',model,var,year]=np.nanmean(gmt_anom[style,'rcp85',model,var,year:year+1])

	return gmt_year

gmt_cowtan=da.read_nc('data/gmt_all_cowtan.nc')['gmt']
gmt_cowtan-=np.expand_dims(np.nanmean(gmt_cowtan[:,:,:,:,1861:1880].values,axis=4),axis=4)

model_runs=[mr for mr in gmt_cowtan_year.model_run  if mr.split('_')[-1]=='r1i1p1']
model_runs.remove('FIO-ESM_r1i1p1')
model_runs.remove('bcc-csm1-1-m_r1i1p1')
model_runs.remove('bcc-csm1-1_r1i1p1')
model_runs.remove('inmcm4_r1i1p1')

print "********** cowtan's data *****"
print '1986-2005'
for style,var,name in zip(['xax','had4'],['air','gmt'],['SAT','blended-masked']):
	print name,':\t',round(np.nanmean(gmt_cowtan[style,'rcp85',model_runs,var,1986:2005])+0.02,03)

print '2006-2015'
for style,var,name in zip(['xax','had4'],['air','gmt'],['SAT','blended-masked']):
	print name,':\t',round(np.nanmean(gmt_cowtan[style,'rcp85',model_runs,var,2006:2015])+0.02,03)

print '2006-2015 - 1986-2005'
for style,var,name in zip(['xax','had4'],['air','gmt'],['SAT','blended-masked']):
	print name,':\t',round(np.nanmean(gmt_cowtan[style,'rcp85',model_runs,var,2006:2015])-np.nanmean(gmt_cowtan[style,'rcp85',model_runs,var,1986:2005]),03)


print 'diff SAT-blendedmasked in 2006-2015:\t',round(np.nanmean(gmt_cowtan['xax','rcp85',model_runs,'air',2006:2015])-np.nanmean(gmt_cowtan['had4','rcp85',model_runs,'gmt',2006:2015]),03)
