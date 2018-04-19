import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import itertools
import matplotlib
import seaborn as sns; sns.set()



styles=['gmt_ar5','gmt_sat','gmt_millar','gmt_bm','gmt_b','gmt_1','gmt_1.1']


for mod_style in ['model','runs']:
	for av_style in ['20year']:
		for preind_name in ['1861-1880','1850-1900']:
			gmt=da.read_nc('data/gmt_plot_ready_'+av_style+'_'+mod_style+'_'+preind_name+'.nc')['gmt']
			gmt_qu=da.DimArray(axes=[['rcp26','rcp45','rcp85'],styles,styles,[1,1.5,2,2.5],['0','1/6.*100','50','5/6.*100','100','mean']],dims=['scenario','x','y','level','out'])
			for level in gmt_qu.level:
				for x_method in styles:
					for y_method,pp in zip(styles,range(7)):
						gmt_base=[]
						for model in gmt.model:
							tt=np.nanargmin(abs(gmt[scenario,model,x_method,:].values-level))
							gmt_base.append(gmt[scenario,model,y_method,:].ix[tt])

						gmt_qu['rcp85',x_method,y_method,level,:].ix[0:5]=np.percentile(gmt_base,[0,1/6.*100,50,5/6.*100,100])
						gmt_qu['rcp85',x_method,y_method,level,'mean']=np.mean(gmt_base)


			ds=da.Dataset({'gmt_qu':gmt_qu})
			ds.write_nc('data/gmt_quantiles_'+av_style+'_'+mod_style+'_'+preind_name+'.nc', mode='w')

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

			#
