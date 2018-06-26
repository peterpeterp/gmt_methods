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
	for av_style in ['year','20year']:
		for preind_name,preind_period in zip(['1861-1880','1850-1900'],[[1861,1880],[1850,1900]]):
			gmt_raw=da.read_nc('data/gmt_'+av_style+'_'+mod_style+'.nc')['gmt']

			# new gmt names new dimarray
			styles=['gmt_ar5','gmt_sat','gmt_millar','gmt_bm','gmt_b','gmt_1','gmt_1.1']
			gmt=da.DimArray(axes=[['rcp85'],gmt_raw.model,styles,gmt_raw.time],dims=['scenario','model','style','time'])

			# reference periods
			for scenario in gmt.scenario:
				for model in gmt.model:
					# anomalies to preindustrial
					gmt[scenario,model,'gmt_sat',:]=np.array(gmt_raw['xax',scenario,model,'air',:])-np.nanmean(gmt_raw['xax',scenario,model,'air',preind_period[0]:preind_period[1]])
					gmt[scenario,model,'gmt_bm',:]=np.array(gmt_raw['had4',scenario,model,'gmt',:])-np.nanmean(gmt_raw['had4',scenario,model,'gmt',preind_period[0]:preind_period[1]])
					gmt[scenario,model,'gmt_b',:]=np.array(gmt_raw['xax',scenario,model,'gmt',:])-np.nanmean(gmt_raw['xax',scenario,model,'gmt',preind_period[0]:preind_period[1]])

					# anomalies as in AR5
					gmt[scenario,model,'gmt_ar5',:]=np.array(gmt_raw['xax',scenario,model,'air',:])-np.nanmean(gmt_raw['xax',scenario,model,'air',1986:2005])+0.61

					# Millar like
					gmt[scenario,model,'gmt_millar',:]=np.array(gmt_raw['xax',scenario,model,'air',:])-np.nanmean(gmt_raw['xax',scenario,model,'air',2010:2019])+0.93
					gmt[scenario,model,'gmt_1',:]=np.array(gmt_raw['xax',scenario,model,'air',:])-np.nanmean(gmt_raw['xax',scenario,model,'air',2010:2019])+1
					gmt[scenario,model,'gmt_1.1',:]=np.array(gmt_raw['xax',scenario,model,'air',:])-np.nanmean(gmt_raw['xax',scenario,model,'air',2010:2019])+1.1


			print '********** '+preind_name+' ***** '+av_style+' ******* '+mod_style
			print '2010-2019'
			for style in gmt.style:
				print style,np.nanmean(gmt['rcp85',:,style,2010:2019])

			print '1986-2005'
			for style in gmt.style:
				print style,np.nanmean(gmt['rcp85',:,style,1986:2005])

			print '2006-2015'
			for style in gmt.style:
				print style,np.nanmean(gmt['rcp85',:,style,2006:2015])

			print '2000-2009'
			for style in gmt.style:
				print style,np.nanmean(gmt['rcp85',:,style,2000:2009])

			ds=da.Dataset({'gmt':gmt})
			ds.write_nc('data/gmt_plot_ready_'+av_style+'_'+mod_style+'_'+preind_name+'.nc', mode='w')


print '__________________'
print '1986-2005'
for style in gmt.style:
	print style,np.nanmean(gmt['rcp85',:,style,1986:2005])

print '2006-2015'
for style in gmt.style:
	print style,np.nanmean(gmt['rcp85',:,style,2006:2015])
