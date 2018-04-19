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

plot=False
styles=['gmt_ar5','gmt_sat','gmt_millar','gmt_bm','gmt_b','gmt_1','gmt_1.1']

for mod_style in ['model','runs']:
	for av_style in ['year']:
		for preind_name,preind_period in zip(['1861-1880','1850-1900'],[[1861,1880],[1850,1900]]):
			gmt=da.read_nc('data/gmt_plot_ready_'+av_style+'_'+mod_style+'_'+preind_name+'.nc')['gmt']

			# quatntile stuff
			gmt_qu=da.DimArray(axes=[['rcp26','rcp45','rcp85'],styles,styles,[1,1.5,2,2.5],[0,1/6.*100,50,5/6.*100,100,'mean']],dims=['scenario','x','y','level','out'])

			for scenario in ['rcp85']:
				for level in gmt_qu.level:
					for x_method in styles:
						if plot:
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

							gmt_qu[scenario,x_method,y_method,level,:].ix[:-1]=np.nanpercentile(x_15,[0,1/6.*100,50,5/6.*100,100])
							gmt_qu[scenario,x_method,y_method,level,'mean']=np.nanmean(x_15)

							if plot:
								y50=gmt_qu[scenario,x_method,y_method,level,50]
								low=gmt_qu[scenario,x_method,y_method,level,1/6.*100]
								up=gmt_qu[scenario,x_method,y_method,level,5/6.*100]

								ax[pp].set_title('points in bin: '+str(len(x_15)))
								ax[pp].plot(x,y,marker='v',color='blue',linestyle='',alpha=0.02)
								ax[pp].plot(x_15,y_15,marker='v',color='green',linestyle='',alpha=0.4)
								ax[pp].plot([gmt_qu[scenario,x_method,y_method,level,0],gmt_qu[scenario,x_method,y_method,level,100]],[0.65,0.65],color='green')
								ax[pp].fill_between([gmt_qu[scenario,x_method,y_method,level,25],gmt_qu[scenario,x_method,y_method,level,75]],[0.63,0.63],[0.67,0.67],color='green')
								ax[pp].plot([gmt_qu[scenario,x_method,y_method,level,50],gmt_qu[scenario,x_method,y_method,level,50]],[0,1.5],color='green')
								ax[pp].text(y50,0.8,str(round(y50,3)),rotation=90,verticalalignment='center',horizontalalignment='center',backgroundcolor='white',color='green')
								ax[pp].text(low,1.1,str(round(low,3)),rotation=90,verticalalignment='center',horizontalalignment='center',backgroundcolor='white',color='green')
								ax[pp].text(up,1.1,str(round(up,3)),rotation=90,verticalalignment='center',horizontalalignment='center',backgroundcolor='white',color='green')
								ax[pp].set_xlim((0.61,2.5))
								ax[pp].set_ylim((0.61,2.5))
								ax[pp].set_xlabel(x_method.replace('_',' '))
								ax[pp].set_ylabel(y_method.replace('_',' '))
								ax[pp].plot([0,5],[0,5],'k--')
								ax[pp].legend(loc='upper left')

						if plot:
							plt.savefig('plots/details/quantiles_'+x_method+'_'+str(level)+'_'+av_style+'_'+mod_style+'_'+preind_name+'.png')

			# conversion table
			conversion_table=open('tables/conversion_table_'+av_style+'_'+mod_style+'_'+preind_name+'.txt','w')
			conversion_table.write('\t'.join([' ']+['gmt_ar5','gmt_sat','gmt_millar','gmt_bm']))
			for x_method in ['gmt_ar5','gmt_sat','gmt_millar','gmt_bm']:
				conversion_table.write('\n'+x_method+'\t')
				for y_method in ['gmt_ar5','gmt_sat','gmt_millar','gmt_bm']:
					if y_method==x_method:
						conversion_table.write(str(round(gmt_qu[scenario,x_method,y_method,1.5,'mean'],2))+'\t')
					else:
						conversion_table.write(str(round(gmt_qu[scenario,x_method,y_method,1.5,'mean'],2))+' ('+str(round(gmt_qu[scenario,x_method,y_method,1.5,str(0)],2))+'-'+str(round(gmt_qu[scenario,x_method,y_method,1.5,str(100)],2))+')\t')
			conversion_table.close()

			# conversion table precise
			conversion_table=open('tables/conversion_table_precise_'+av_style+'_'+mod_style+'_'+preind_name+'.txt','w')
			conversion_table.write('\t'.join([' ']+['gmt_ar5','gmt_sat','gmt_millar','gmt_bm']))
			for x_method in ['gmt_ar5','gmt_sat','gmt_millar','gmt_bm']:
				conversion_table.write('\n'+x_method+'\t')
				for y_method in ['gmt_ar5','gmt_sat','gmt_millar','gmt_bm']:
					conversion_table.write(str(round(gmt_qu[scenario,x_method,y_method,1.5,'mean'],4))+'\t')
			conversion_table.close()

			# conversion table full
			conversion_table=open('tables/conversion_table_SI_'+av_style+'_'+mod_style+'_'+preind_name+'.txt','w')
			conversion_table.write('\t'.join([' ']+styles))
			for x_method in styles:
				conversion_table.write('\n'+x_method+'\t')
				for y_method in styles:
					if y_method==x_method:
						conversion_table.write(str(round(gmt_qu[scenario,x_method,y_method,1.5,'mean'],2))+'\t')
					else:
						conversion_table.write(str(round(gmt_qu[scenario,x_method,y_method,1.5,'mean'],2))+' ('+str(round(gmt_qu[scenario,x_method,y_method,1.5,str(0)],2))+'-'+str(round(gmt_qu[scenario,x_method,y_method,1.5,str(100)],2))+')\t')
			conversion_table.close()

			ds=da.Dataset({'gmt_qu':gmt_qu})
			ds.write_nc('data/gmt_quantiles_'+av_style+'_'+mod_style+'_'+preind_name+'.nc', mode='w')
