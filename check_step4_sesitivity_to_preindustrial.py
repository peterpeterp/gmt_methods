import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import itertools
import matplotlib
from scipy import stats
import seaborn as sns

gmt_full=da.read_nc('data/gmt_model.nc')['gmt']

print 'models starting in 1850',gmt_full.model[np.isfinite(gmt_full['xax','rcp85',:,'air'].ix[:,1])]
print 'models starting in 1861',gmt_full.model[np.isfinite(gmt_full['xax','rcp85',:,'air'].ix[:,1])==False]

# select models starting in 1850
gmt_=gmt_full[:,:,np.isfinite(gmt_['xax','rcp85',:,'air'].ix[:,1]),:,:]

# new gmt names new dimarray
styles=['gmt_ar5','gmt_sat','gmt_millar','gmt_bm','gmt_b','gmt_1','gmt_1.1']
gmt__=da.DimArray(axes=[['rcp85'],gmt_.model,styles,gmt_.time],dims=['scenario','model','style','time'])


# reference periods
ref_preindust_dict={'1850-1900':gmt__.time[(gmt__.time>=1850) & (gmt__.time<1901)],
					'1861-1880':gmt__.time[(gmt__.time>=1861) & (gmt__.time<1881)],
					'1861-1900':gmt__.time[(gmt__.time>=1861) & (gmt__.time<1901)]}

for name,ref_preindustrial in ref_preindust_dict.items():

	ref_ar5=gmt__.time[(gmt__.time>=1986) & (gmt__.time<2006)]
	ref_millar=gmt__.time[(gmt__.time>=2010) & (gmt__.time<2020)]

	for style in gmt__.style:
		for scenario in gmt__.scenario:
			for model in gmt__.model:
				# anomalies to preindustrial
				gmt__[scenario,model,'gmt_sat',:]=np.array(gmt_['xax',scenario,model,'air',:])-np.nanmean(gmt_['xax',scenario,model,'air',ref_preindustrial])
				gmt__[scenario,model,'gmt_bm',:]=np.array(gmt_['had4',scenario,model,'gmt',:])-np.nanmean(gmt_['had4',scenario,model,'gmt',ref_preindustrial])
				gmt__[scenario,model,'gmt_b',:]=np.array(gmt_['xax',scenario,model,'gmt',:])-np.nanmean(gmt_['xax',scenario,model,'gmt',ref_preindustrial])

				# anomalies as in AR5
				gmt__[scenario,model,'gmt_ar5',:]=np.array(gmt_['xax',scenario,model,'air',:])-np.nanmean(gmt_['xax',scenario,model,'air',ref_ar5])+0.61

				# Millar like
				gmt__[scenario,model,'gmt_millar',:]=np.array(gmt_['xax',scenario,model,'air',:])-np.nanmean(gmt_['xax',scenario,model,'air',ref_millar])+0.93
				gmt__[scenario,model,'gmt_1',:]=np.array(gmt_['xax',scenario,model,'air',:])-np.nanmean(gmt_['xax',scenario,model,'air',ref_millar])+1
				gmt__[scenario,model,'gmt_1.1',:]=np.array(gmt_['xax',scenario,model,'air',:])-np.nanmean(gmt_['xax',scenario,model,'air',ref_millar])+1.1

	print '2010-2019'
	for style in gmt__.style:
		print style,np.nanmean(gmt__['rcp85',:,style,2010:2020])

	print '1986-2005'
	for style in gmt__.style:
		print style,np.nanmean(gmt__['rcp85',:,style,1986:2006])

	print 'done'
	# quatntile stuff
	gmt_qu=da.DimArray(axes=[['rcp26','rcp45','rcp85'],styles,styles,[1,1.5,2,2.5],[0,5,10,1/6.*100,25,50,75,5/6.*100,90,95,100]],dims=['scenario','x','y','level','out'])

	for scenario in ['rcp85']:
		for level in gmt_qu.level:
			for x_method in styles:
				plt.close('all')
				for y_method,pp in zip(styles,range(7)):
					x_=np.asarray(gmt[scenario,:,x_method,:]).reshape(len(gmt.model)*len(gmt.time))
					y_=np.asarray(gmt[scenario,:,y_method,:]).reshape(len(gmt.model)*len(gmt.time))
					idx = np.isfinite(x_) & np.isfinite(y_)
					x,y=x_[idx],y_[idx]

					tmp=np.where((y>level-0.05) & (y<level+0.05))
					y_15=y[tmp]
					x_15=x[tmp]

					for qu in gmt_qu.out:
						gmt_qu[scenario,x_method,y_method,level,qu]=np.nanpercentile(x_15,qu)

					y50=gmt_qu[scenario,x_method,y_method,level,50]
					low=gmt_qu[scenario,x_method,y_method,level,1/6.*100]
					up=gmt_qu[scenario,x_method,y_method,level,5/6.*100]

	# conversion table
	conversion_table=open('check4_conversion_table_'+name+'.txt','w')
	conversion_table.write('\t'.join([' ']+['gmt_ar5','gmt_sat','gmt_millar','gmt_bm']))
	for x_method in ['gmt_ar5','gmt_sat','gmt_millar','gmt_bm']:
		conversion_table.write('\n'+x_method+'\t')
		for y_method in ['gmt_ar5','gmt_sat','gmt_millar','gmt_bm']:
			if y_method==x_method:
				conversion_table.write(str(round(gmt_qu[scenario,x_method,y_method,1.5,50],2))+'\t')
			else:
				conversion_table.write(str(round(gmt_qu[scenario,x_method,y_method,1.5,50],5))+' ('+str(round(gmt_qu[scenario,x_method,y_method,1.5,1/6.*100],2))+'-'+str(round(gmt_qu[scenario,x_method,y_method,1.5,5/6.*100],2))+')\t')
	conversion_table.close()
