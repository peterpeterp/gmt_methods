import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import itertools
import matplotlib
from scipy import stats
import seaborn as sns

gmt_raw=da.read_nc('data/gmt_model.nc')['gmt']

# new gmt names new dimarray
styles=['gmt_ar5','gmt_sat','gmt_millar','gmt_bm','gmt_b','gmt_1','gmt_1.1']
gmt=da.DimArray(axes=[['rcp85'],gmt_raw.model,styles,gmt_raw.time],dims=['scenario','model','style','time'])

# reference periods
for scenario in gmt.scenario:
	for model in gmt.model:
		# anomalies to preindustrial
		gmt[scenario,model,'gmt_sat',:]=np.array(gmt_raw['xax',scenario,model,'air',:])-np.nanmean(gmt_raw['xax',scenario,model,'air',1861:1880])
		gmt[scenario,model,'gmt_bm',:]=np.array(gmt_raw['had4',scenario,model,'gmt',:])-np.nanmean(gmt_raw['had4',scenario,model,'gmt',1861:1880])
		gmt[scenario,model,'gmt_b',:]=np.array(gmt_raw['xax',scenario,model,'gmt',:])-np.nanmean(gmt_raw['xax',scenario,model,'gmt',1861:1880])

		# anomalies as in AR5
		gmt[scenario,model,'gmt_ar5',:]=np.array(gmt_raw['xax',scenario,model,'air',:])-np.nanmean(gmt_raw['xax',scenario,model,'air',1986:2005])+0.61

		# Millar like
		gmt[scenario,model,'gmt_millar',:]=np.array(gmt_raw['xax',scenario,model,'air',:])-np.nanmean(gmt_raw['xax',scenario,model,'air',2010:2019])+0.93
		gmt[scenario,model,'gmt_1',:]=np.array(gmt_raw['xax',scenario,model,'air',:])-np.nanmean(gmt_raw['xax',scenario,model,'air',2010:2019])+1
		gmt[scenario,model,'gmt_1.1',:]=np.array(gmt_raw['xax',scenario,model,'air',:])-np.nanmean(gmt_raw['xax',scenario,model,'air',2010:2019])+1.1

print '2010-2019'
for style in gmt.style:
	print style,np.nanmean(gmt['rcp85',:,style,2010:2019])

print '1986-2005'
for style in gmt.style:
	print style,np.nanmean(gmt['rcp85',:,style,1986:2005])

print '2000-2009'
for style in gmt.style:
	print style,np.nanmean(gmt['rcp85',:,style,2000:2009])


print 'done'
# quatntile stuff
gmt_qu=da.DimArray(axes=[['rcp26','rcp45','rcp85'],styles,styles,[1,1.5,2,2.5],[0,5,10,1/6.*100,25,50,75,5/6.*100,90,95,100]],dims=['scenario','x','y','level','out'])

for scenario in ['rcp85']:
	for level in gmt_qu.level:
		for x_method in styles:
			plt.close('all')
			fig,axes=plt.subplots(nrows=2,ncols=4,figsize=(12,8))
			ax=axes.flatten()
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

				ax[pp].plot(x,y,marker='v',color='blue',linestyle='',alpha=0.02)
				ax[pp].plot(x_15,y_15,marker='v',color='green',linestyle='',alpha=0.4)

				ax[pp].plot([gmt_qu[scenario,x_method,y_method,level,0],gmt_qu[scenario,x_method,y_method,level,100]],[0.65,0.65],color='green')
				ax[pp].fill_between([gmt_qu[scenario,x_method,y_method,level,25],gmt_qu[scenario,x_method,y_method,level,75]],[0.63,0.63],[0.67,0.67],color='green')
				ax[pp].plot([gmt_qu[scenario,x_method,y_method,level,50],gmt_qu[scenario,x_method,y_method,level,50]],[0,1.5],color='green')
				y50=gmt_qu[scenario,x_method,y_method,level,50]
				ax[pp].text(y50,0.8,str(round(y50,3)),rotation=90,verticalalignment='center',horizontalalignment='center',backgroundcolor='white',color='green')
				low=gmt_qu[scenario,x_method,y_method,level,1/6.*100]
				ax[pp].text(low,1.1,str(round(low,3)),rotation=90,verticalalignment='center',horizontalalignment='center',backgroundcolor='white',color='green')
				up=gmt_qu[scenario,x_method,y_method,level,5/6.*100]
				ax[pp].text(up,1.1,str(round(up,3)),rotation=90,verticalalignment='center',horizontalalignment='center',backgroundcolor='white',color='green')

				ax[pp].set_xlim((0.61,2.5))
				ax[pp].set_ylim((0.61,2.5))
				ax[pp].set_xlabel(x_method.replace('_',' '))
				ax[pp].set_ylabel(y_method.replace('_',' '))
				ax[pp].plot([0,5],[0,5],'k--')
				ax[pp].legend(loc='upper left')

			plt.savefig('plots/details/quantiles_'+x_method+'_'+str(level)+'.png')

# conversion table
conversion_table=open('conversion_table.txt','w')
conversion_table.write('\t'.join([' ']+['gmt_ar5','gmt_sat','gmt_millar','gmt_bm']))
for x_method in ['gmt_ar5','gmt_sat','gmt_millar','gmt_bm']:
	conversion_table.write('\n'+x_method+'\t')
	for y_method in ['gmt_ar5','gmt_sat','gmt_millar','gmt_bm']:
		if y_method==x_method:
			conversion_table.write(str(round(gmt_qu[scenario,x_method,y_method,1.5,50],2))+'\t')
		else:
			conversion_table.write(str(round(gmt_qu[scenario,x_method,y_method,1.5,50],2))+' ('+str(round(gmt_qu[scenario,x_method,y_method,1.5,0],2))+'-'+str(round(gmt_qu[scenario,x_method,y_method,1.5,100],2))+')\t')
conversion_table.close()

# conversion table precise
conversion_table=open('conversion_table_precise.txt','w')
conversion_table.write('\t'.join([' ']+['gmt_ar5','gmt_sat','gmt_millar','gmt_bm']))
for x_method in ['gmt_ar5','gmt_sat','gmt_millar','gmt_bm']:
	conversion_table.write('\n'+x_method+'\t')
	for y_method in ['gmt_ar5','gmt_sat','gmt_millar','gmt_bm']:
		conversion_table.write(str(round(gmt_qu[scenario,x_method,y_method,1.5,50],4))+'\t')
conversion_table.close()

# conversion table full
conversion_table=open('conversion_table_SI.txt','w')
conversion_table.write('\t'.join([' ']+styles))
for x_method in styles:
	conversion_table.write('\n'+x_method+'\t')
	for y_method in styles:
		if y_method==x_method:
			conversion_table.write(str(round(gmt_qu[scenario,x_method,y_method,1.5,50],2))+'\t')
		else:
			conversion_table.write(str(round(gmt_qu[scenario,x_method,y_method,1.5,50],2))+' ('+str(round(gmt_qu[scenario,x_method,y_method,1.5,0],2))+'-'+str(round(gmt_qu[scenario,x_method,y_method,1.5,100],2))+')\t')
conversion_table.close()


ds=da.Dataset({'gmt':gmt})
ds.write_nc('data/gmt_plot_ready.nc', mode='w')

ds=da.Dataset({'gmt_qu':gmt_qu})
ds.write_nc('data/gmt_quantiles.nc', mode='w')
