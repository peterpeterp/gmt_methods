import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import itertools
import matplotlib
from scipy import stats
import seaborn as sns
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import summary_table
from statsmodels.sandbox.regression.predstd import wls_prediction_std

def running_mean_func(xx,N):
	if N==1:
		return xx
	if N!=1:
	    x=np.ma.masked_invalid(xx.copy())
	    ru_mean=x.copy()*np.nan
	    for t in range(int(N/2),len(x)-int(N/2)):
	        ru_mean[t]=np.nanmean(x[t-int(N/2):t+int(N/2)])
	    return ru_mean


gmt_all=da.read_nc('data/gmt.nc')['gmt']

models=list(gmt_all.model)
models.remove('CESM1-CAM5')
models.remove('MIROC5')
models.remove('BNU-ESM')
models.remove('bcc-csm1-1-m')

gmt_=gmt_all[gmt_all.style,gmt_all.scenario,models,gmt_all.variable,gmt_all.time]

ensemble=open('ensemble.txt','w')
for scenario in gmt_.scenario:
	ensemble.write(scenario+':\n')
	for model in sorted(gmt_.model):
		if np.isfinite(np.nanmean(gmt_['had4',scenario,model,'gmt',:])):
			ensemble.write(model+'\t')
	ensemble.write('\n')
ensemble.close()


dat=open('data/Had4_gmt.txt','r').read()
had4=[]
for line in dat.split('\n')[::2]:
	for anom in line.split(' ')[2:-1]:
		if anom!='':
			had4.append(float(anom))

had4_gmt=np.array(had4[11*12:-12])
had4_gmt-=np.nanmean(had4_gmt[0:240])
had4_time=gmt_['had4','rcp85','HadGEM2-ES','time',0:1871]



# anomaly to preindustrial
gmt=da.DimArray(axes=[['rcp26','rcp45','rcp85'],models,['bm_pre','bm_ar5','tas_ar5','tas_pre','b_pre','b_ar5','tas_millar','time'],np.arange(0,2880)],dims=['scenario','model','style','time'])

for style in gmt.style:
	for scenario in gmt.scenario:
		for model in gmt.model:
			# anomalies to preindustrial
			gmt[scenario,model,'tas_pre',:]=np.array(gmt_['xax',scenario,model,'air',:])-np.nanmean(gmt_['xax',scenario,model,'air',0:240])
			gmt[scenario,model,'bm_pre',:]=np.array(gmt_['had4',scenario,model,'gmt',:])-np.nanmean(gmt_['had4',scenario,model,'gmt',0:240])
			gmt[scenario,model,'b_pre',:]=np.array(gmt_['xax',scenario,model,'gmt',:])-np.nanmean(gmt_['xax',scenario,model,'gmt',0:240])

			# anomalies as in AR5
			gmt[scenario,model,'tas_ar5',:]=np.array(gmt_['xax',scenario,model,'air',:])-np.nanmean(gmt_['xax',scenario,model,'air',125*12:145*12])+np.nanmean(had4_gmt[125*12:145*12])
			gmt[scenario,model,'bm_ar5',:]=np.array(gmt_['had4',scenario,model,'gmt',:])-np.nanmean(gmt_['had4',scenario,model,'gmt',125*12:145*12])+np.nanmean(had4_gmt[125*12:145*12])
			gmt[scenario,model,'b_ar5',:]=np.array(gmt_['xax',scenario,model,'gmt',:])-np.nanmean(gmt_['xax',scenario,model,'gmt',125*12:145*12])+np.nanmean(had4_gmt[125*12:145*12])

			# Millar 1997-2017 base
			gmt[scenario,model,'tas_millar',:]=np.array(gmt_['xax',scenario,model,'air',:])-np.nanmean(gmt_['xax',scenario,model,'air',1632:1872])+np.nanmean(had4_gmt[1632:1872])

			# add time
			gmt[scenario,model,'time',:]=gmt_['had4',scenario,model,'time',:]


print 'warming in 1986-2006: ',np.nanmean(had4_gmt[125*12:145*12])
print 'tas: ',np.nanmean(gmt[scenario,:,'tas_pre',125*12:145*12])
print 'bm: ',np.nanmean(gmt[scenario,:,'bm_pre',125*12:145*12])
print 'b: ',np.nanmean(gmt[scenario,:,'b_pre',125*12:145*12])
print 'millar: ',np.nanmean(gmt[scenario,:,'tas_millar',125*12:145*12])

# quatntile stuff
styles=['tas_pre','tas_ar5','bm_pre','bm_ar5','b_pre','b_ar5','tas_millar']
gmt_qu=da.DimArray(axes=[['rcp26','rcp45','rcp85'],styles,styles,[1,1.5,2,2.5],[0,5,10,16.6,25,50,75,83.3,90,95,100]],dims=['scenario','x','y','level','out'])

for scenario in ['rcp85']:
	for level in gmt_qu.level:
		for x_method in styles:
			plt.clf()

			fig,axes=plt.subplots(nrows=2,ncols=4,figsize=(12,8))
			ax=axes.flatten()
			for y_method,pp in zip(styles,range(7)):
				x_=np.asarray(gmt[scenario,:,x_method,:]).reshape(47*2880)
				y_=np.asarray(gmt[scenario,:,y_method,:]).reshape(47*2880)
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
				ax[pp].text(y50,0.9,str(round(y50,3)),rotation=90,verticalalignment='center',horizontalalignment='center',backgroundcolor='white',color='green')

				ax[pp].set_xlim((0.61,2.5))
				ax[pp].set_ylim((0.61,2.5))
				ax[pp].set_xlabel(x_method.replace('_',' '))
				ax[pp].set_ylabel(y_method.replace('_',' '))
				ax[pp].plot([0,5],[0,5],'k--')
				ax[pp].legend(loc='upper left')

			plt.savefig('plots/quantiles_'+x_method+'_'+str(level)+'.png')

# conversion table
conversion_table=open('conversion_table.txt','w')
conversion_table.write('\t'.join([' ']+['tas_ar5','tas_pre','bm_pre','bm_ar5']))
for x_method in ['tas_ar5','tas_pre','bm_pre','bm_ar5']:
	conversion_table.write('\n'+x_method+'\t')
	for y_method in ['tas_ar5','tas_pre','bm_pre','bm_ar5']:
		conversion_table.write(str(round(gmt_qu[scenario,x_method,y_method,1.5,50],2))+'\t')
conversion_table.close()

# conversion table precise
conversion_table=open('conversion_table_precise.txt','w')
conversion_table.write('\t'.join([' ']+['tas_ar5','tas_pre','bm_pre','bm_ar5']))
for x_method in ['tas_ar5','tas_pre','bm_pre','bm_ar5']:
	conversion_table.write('\n'+x_method+'\t')
	for y_method in ['tas_ar5','tas_pre','bm_pre','bm_ar5']:
		conversion_table.write(str(round(gmt_qu[scenario,x_method,y_method,1.5,50],4))+'\t')
conversion_table.close()

# conversion table full
conversion_table=open('conversion_table_SI.txt','w')
conversion_table.write('\t'.join([' ']+styles))
for x_method in ['tas_ar5','tas_pre','bm_pre','bm_ar5','b_pre','b_ar5']:
	conversion_table.write('\n'+x_method+'\t')
	for y_method in ['tas_ar5','tas_pre','bm_pre','bm_ar5','b_pre','b_ar5']:
		if y_method==x_method:
			conversion_table.write(str(round(gmt_qu[scenario,x_method,y_method,1.5,50],2))+'\t')
		else:
			conversion_table.write(str(round(gmt_qu[scenario,x_method,y_method,1.5,50],2))+' ('+str(round(gmt_qu[scenario,x_method,y_method,1.5,25],2))+'-'+str(round(gmt_qu[scenario,x_method,y_method,1.5,75],2))+')\t')
conversion_table.close()

# FIG 1
plot_dict={
	'tas_pre':{'l_color':'orange','color':'darkorange','longname':'$\mathregular{GMT_{SAT}}$','pos':0.65},
	'bm_pre':{'l_color':'cornflowerblue','color':sns.color_palette()[0],'longname':'$\mathregular{GMT_{BM\_CMIP5}}$','pos':0.75},
	'bm_ar5':{'l_color':'tomato','color':sns.color_palette()[2],'longname':'$\mathregular{GMT_{BM\_CMIP5\_ref}}$','pos':0.85},
}
for scenario in ['rcp85']:
	plt.clf()
	fig,axes=plt.subplots(nrows=1,ncols=2,figsize=(10,5))
	ax=axes.flatten()
	ax[0].fill_between([-1,5],[1.55,1.55],[1.45,1.45],color='white')
	ax[0].plot([-1,5],[1.45,1.45],linestyle='--',color='k')
	ax[0].plot([-1,5],[1.55,1.55],linestyle='--',color='k')
	x__=np.arange(0,5,0.01)

	for method in ['tas_pre','bm_pre','bm_ar5']:
		tmp=plot_dict[method]

		x_=np.asarray(gmt[scenario,:,'tas_ar5',:]).reshape(47*2880)
		y_=np.asarray(gmt[scenario,:,method,:]).reshape(47*2880)
		idx = np.isfinite(x_) & np.isfinite(y_)
		x,y=x_[idx],y_[idx]
		ax[0].scatter(x,y,color=tmp['l_color'],marker='v',alpha=0.1)


		yy=gmt_qu[scenario,'tas_ar5',method,1.5,50]
		ax[0].plot([gmt_qu[scenario,'tas_ar5',method,1.5,0],gmt_qu[scenario,'tas_ar5',method,1.5,100]],[tmp['pos'],tmp['pos']],color=tmp['color'])
		ax[0].fill_between([gmt_qu[scenario,'tas_ar5',method,1.5,25],gmt_qu[scenario,'tas_ar5',method,1.5,75]],[tmp['pos']-0.02,tmp['pos']-0.02],[tmp['pos']+0.02,tmp['pos']+0.02],color=tmp['color'])
		ax[0].plot([yy,yy],[tmp['pos'],1.5],color=tmp['color'],lw=2)
		ax[0].plot([yy,yy],[tmp['pos']-0.02,tmp['pos']+0.02],color='white',lw=2)
		ax[0].text(yy,1,str(round(yy,2)),rotation=90,verticalalignment='center',horizontalalignment='center',backgroundcolor='white',color=tmp['color'])
		ax[0].plot([-99,-99],[-99,-99],color=tmp['color'],lw=2,label=tmp['longname']+' '+str(round(yy,2))+ \
		' ('+str(round(gmt_qu[scenario,'tas_ar5',method,1.5,25],2))+'-'+str(round(gmt_qu[scenario,'tas_ar5',method,1.5,75],2))+')')

	ax[0].plot([-1,5],[-1,5],linestyle='--',color='k')
	ax[0].set_ylim((0.61,2.3))
	ax[0].set_xlim((0.61,2.3))

	ax[0].set_xlabel('$\mathregular{GMT_{AR5}}$ $\mathregular{[^\circ C]}$')
	ax[0].set_ylabel('$\mathregular{GMT_{alt}}$ $\mathregular{[^\circ C]}$')
	ax[0].legend(loc='upper left',fontsize=12)

	for method in ['bm_pre','bm_ar5']:
		x_=np.asarray(gmt[scenario,:,'tas_ar5',:]).reshape(47*2880)
		y_=np.asarray(gmt[scenario,:,method,:]).reshape(47*2880)
		idx = np.isfinite(x_) & np.isfinite(y_)
		x,y=x_[idx],y_[idx]

		ax[1].scatter(x,y-x,color=plot_dict[method]['l_color'],marker='v',alpha=0.1)

		for level in gmt_qu.level:
			tmp=y[(x>level-0.05) & (x<level+0.05)]-x[(x>level-0.05) & (x<level+0.05)]
			tmp=np.nanpercentile(tmp,[0,25,50,75,100])
			ax[1].plot([level,level],tmp[[0,4]],color=plot_dict[method]['color'],lw=2)
			ax[1].plot([level-0.02,level+0.02],[tmp[2],tmp[2]],color='white',lw=2)
			ax[1].fill_between([level-0.02,level+0.02],[tmp[1],tmp[1]],[tmp[3],tmp[3]],color=plot_dict[method]['color'])


	ax[1].plot([-1,5],[0,0],linestyle='-',color='k',lw=2)
	ax[1].set_ylim((-0.8,0.4))
	ax[1].set_xlim((0.61,2.7))

	ax[1].set_xlabel('$\mathregular{GMT_{AR5}}$ $\mathregular{[^\circ C]}$')
	ax[1].set_ylabel('$\mathregular{GMT_{alt} -GMT_{AR5}}$ $\mathregular{[^\circ C]}$')

	plt.tight_layout()
	plt.savefig('plots/FIG1_'+scenario+'_qu.png')
	plt.savefig('plots/FIG1_'+scenario+'_qu.pdf')



# FIG SI 1
plot_dict={
	'tas_pre':{'l_color':'orange','color':'darkorange','longname':'$\mathregular{GMT_{SAT}}$','pos':0.65,'lsty':'-'},
	'tas_ar5':{'l_color':'xyan','color':'darkcyan','longname':'$\mathregular{GMT_{AR5}}$','pos':0.65,'lsty':'--'},
	'bm_pre':{'l_color':'cornflowerblue','color':sns.color_palette()[0],'longname':'$\mathregular{GMT_{BM\_CMIP5}}$','pos':0.75,'lsty':'-'},
	'bm_ar5':{'l_color':'tomato','color':sns.color_palette()[2],'longname':'$\mathregular{GMT_{BM\_CMIP5\_ref}}$','pos':0.85,'lsty':':'},
}
plt.clf()
fig,axes=plt.subplots(nrows=1,ncols=2,figsize=(10,5))
ax=axes.flatten()
year=gmt['rcp85','HadGEM2-ES','time',0:1871]

ax[0].plot(gmt['rcp85','HadGEM2-ES','time',0:1871],running_mean_func(had4_gmt,12),'gray',lw=2,alpha=0.6,label='HadCRUT4')
for method in ['tas_pre','bm_pre']:
	ax[0].plot(year,running_mean_func(np.nanmean(gmt['rcp85',:,method,0:1871],axis=0),12),label=plot_dict[method]['longname'],color=plot_dict[method]['color'])
for method in ['tas_ar5','bm_ar5']:
	ax[0].plot(year.ix[0:135*12],running_mean_func(had4_gmt,12)[0:135*12],label=plot_dict[method]['longname'],color=plot_dict[method]['color'],linestyle=plot_dict[method]['lsty'])
	ax[0].plot(year.ix[135*12:1871],running_mean_func(np.nanmean(gmt['rcp85',:,method,:],axis=0)[135*12:1871],12),color=plot_dict[method]['color'],linestyle=plot_dict[method]['lsty'])

ax[0].set_ylim((-0.4,1.3))
ax[0].set_xlim((1861,2014))
ax[0].plot([1996,1996],[-0.4,1.5],color='k')
ax[0].set_ylabel('$\mathregular{GMT}$ $\mathregular{[^\circ C]}$')
ax[0].legend(loc='upper left',fontsize=10)

for method in ['tas_pre','bm_pre']:
	ax[1].plot(year,running_mean_func(np.nanmean(gmt['rcp85',:,method,0:1871]-had4_gmt,axis=0),60),label=plot_dict[method]['longname'],color=plot_dict[method]['color'])
for method in ['tas_ar5','bm_ar5']:
	ax[1].plot(year.ix[0:125*12],running_mean_func(had4_gmt-had4_gmt,60)[0:125*12],label=plot_dict[method]['longname'],color=plot_dict[method]['color'],linestyle=plot_dict[method]['lsty'])
	ax[1].plot(year.ix[125*12:1871],running_mean_func(np.nanmean(gmt['rcp85',:,method,0:1871]-had4_gmt,axis=0),60)[125*12:1871],color=plot_dict[method]['color'],linestyle=plot_dict[method]['lsty'])

#ax[1].set_ylim((-0.2,0.2))
ax[1].plot([1860,2020],[0,0],color='k')
ax[1].plot([1996,1996],[-0.2,0.2],color='k')
ax[1].set_xlim((1861,2015))
ax[1].set_ylabel('$\mathregular{GMT-GMT_{obs}}$ $\mathregular{[^\circ C]}$')
plt.tight_layout()
plt.savefig('plots/GMT_ref.png')
plt.savefig('plots/GMT_ref.pdf')


# FIG SI 2 as FIG 1 but blended instead of blended_masked
plot_dict={
	'tas_pre':{'l_color':'orange','color':'darkorange','longname':'$\mathregular{GMT_{SAT}}$','pos':0.65},
	'b_pre':{'l_color':'cornflowerblue','color':sns.color_palette()[0],'longname':'$\mathregular{GMT_{B\_CMIP5}}$','pos':0.75},
	'b_ar5':{'l_color':'tomato','color':sns.color_palette()[2],'longname':'$\mathregular{GMT_{B\_CMIP5\_ref}}$','pos':0.85},
}
for scenario in ['rcp85']:
	plt.clf()
	fig,axes=plt.subplots(nrows=1,ncols=2,figsize=(10,5))
	ax=axes.flatten()
	ax[0].fill_between([-1,5],[1.55,1.55],[1.45,1.45],color='white')
	ax[0].plot([-1,5],[1.45,1.45],linestyle='--',color='k')
	ax[0].plot([-1,5],[1.55,1.55],linestyle='--',color='k')
	x__=np.arange(0,5,0.01)

	for method in ['tas_pre','b_pre','b_ar5']:
		tmp=plot_dict[method]

		x_=np.asarray(gmt[scenario,:,'tas_ar5',:]).reshape(47*2880)
		y_=np.asarray(gmt[scenario,:,method,:]).reshape(47*2880)
		idx = np.isfinite(x_) & np.isfinite(y_)
		x,y=x_[idx],y_[idx]
		ax[0].scatter(x,y,color=tmp['l_color'],marker='v',alpha=0.1)


		yy=gmt_qu[scenario,'tas_ar5',method,1.5,50]
		ax[0].plot([gmt_qu[scenario,'tas_ar5',method,1.5,0],gmt_qu[scenario,'tas_ar5',method,1.5,100]],[tmp['pos'],tmp['pos']],color=tmp['color'])
		ax[0].fill_between([gmt_qu[scenario,'tas_ar5',method,1.5,25],gmt_qu[scenario,'tas_ar5',method,1.5,75]],[tmp['pos']-0.02,tmp['pos']-0.02],[tmp['pos']+0.02,tmp['pos']+0.02],color=tmp['color'])
		ax[0].plot([yy,yy],[tmp['pos'],1.5],color=tmp['color'],lw=2)
		ax[0].plot([yy,yy],[tmp['pos']-0.02,tmp['pos']+0.02],color='white',lw=2)
		ax[0].text(yy,1,str(round(yy,2)),rotation=90,verticalalignment='center',horizontalalignment='center',backgroundcolor='white',color=tmp['color'])
		ax[0].plot([-99,-99],[-99,-99],color=tmp['color'],lw=2,label=tmp['longname']+' '+str(round(yy,2))+ \
		' ('+str(round(gmt_qu[scenario,'tas_ar5',method,1.5,25],2))+'-'+str(round(gmt_qu[scenario,'tas_ar5',method,1.5,75],2))+')')

	ax[0].plot([-1,5],[-1,5],linestyle='--',color='k')
	ax[0].set_ylim((0.61,2.3))
	ax[0].set_xlim((0.61,2.3))

	ax[0].set_xlabel('$\mathregular{GMT_{AR5}}$ $\mathregular{[^\circ C]}$')
	ax[0].set_ylabel('$\mathregular{GMT_{alt}}$ $\mathregular{[^\circ C]}$')
	ax[0].legend(loc='upper left',fontsize=12)

	for method in ['b_pre','b_ar5']:
		x_=np.asarray(gmt[scenario,:,'tas_ar5',:]).reshape(47*2880)
		y_=np.asarray(gmt[scenario,:,method,:]).reshape(47*2880)
		idx = np.isfinite(x_) & np.isfinite(y_)
		x,y=x_[idx],y_[idx]

		ax[1].scatter(x,y-x,color=plot_dict[method]['l_color'],marker='v',alpha=0.1)

		for level in gmt_qu.level:
			tmp=y[(x>level-0.05) & (x<level+0.05)]-x[(x>level-0.05) & (x<level+0.05)]
			tmp=np.nanpercentile(tmp,[0,25,50,75,100])
			ax[1].plot([level,level],tmp[[0,4]],color=plot_dict[method]['color'],lw=2)
			ax[1].plot([level-0.02,level+0.02],[tmp[2],tmp[2]],color='white',lw=2)
			ax[1].fill_between([level-0.02,level+0.02],[tmp[1],tmp[1]],[tmp[3],tmp[3]],color=plot_dict[method]['color'])


	ax[1].plot([-1,5],[0,0],linestyle='-',color='k',lw=2)
	ax[1].set_ylim((-0.8,0.4))
	ax[1].set_xlim((0.61,2.7))

	ax[1].set_xlabel('$\mathregular{GMT_{AR5}}$ $\mathregular{[^\circ C]}$')
	ax[1].set_ylabel('$\mathregular{GMT_{alt} -GMT_{AR5}}$ $\mathregular{[^\circ C]}$')

	plt.tight_layout()
	plt.savefig('plots/FIG1_'+scenario+'_qu_SI.png')
	plt.savefig('plots/FIG1_'+scenario+'_qu_SI.pdf')




# FIG 1 MILLAR
plot_dict={
	'tas_millar':{'l_color':'cyan','color':'darkcyan','longname':'$\mathregular{GMT_{Millar}}$','pos':0.65},
	'tas_pre':{'l_color':'orange','color':'darkorange','longname':'$\mathregular{GMT_{SAT}}$','pos':0.65},
	'bm_pre':{'l_color':'cornflowerblue','color':sns.color_palette()[0],'longname':'$\mathregular{GMT_{BM\_CMIP5}}$','pos':0.75},
	'bm_ar5':{'l_color':'tomato','color':sns.color_palette()[2],'longname':'$\mathregular{GMT_{BM\_CMIP5\_ref}}$','pos':0.85},
}
for scenario in ['rcp85']:
	plt.clf()
	fig,axes=plt.subplots(nrows=1,ncols=2,figsize=(10,5))
	ax=axes.flatten()
	ax[0].fill_between([-1,5],[1.55,1.55],[1.45,1.45],color='white')
	ax[0].plot([-1,5],[1.45,1.45],linestyle='--',color='k')
	ax[0].plot([-1,5],[1.55,1.55],linestyle='--',color='k')
	x__=np.arange(0,5,0.01)

	for method in ['tas_pre','bm_pre','bm_ar5','tas_millar']:
		tmp=plot_dict[method]

		x_=np.asarray(gmt[scenario,:,'tas_ar5',:]).reshape(47*2880)
		y_=np.asarray(gmt[scenario,:,method,:]).reshape(47*2880)
		idx = np.isfinite(x_) & np.isfinite(y_)
		x,y=x_[idx],y_[idx]
		ax[0].scatter(x,y,color=tmp['l_color'],marker='v',alpha=0.1)


		yy=gmt_qu[scenario,'tas_ar5',method,1.5,50]
		ax[0].plot([gmt_qu[scenario,'tas_ar5',method,1.5,0],gmt_qu[scenario,'tas_ar5',method,1.5,100]],[tmp['pos'],tmp['pos']],color=tmp['color'])
		ax[0].fill_between([gmt_qu[scenario,'tas_ar5',method,1.5,25],gmt_qu[scenario,'tas_ar5',method,1.5,75]],[tmp['pos']-0.02,tmp['pos']-0.02],[tmp['pos']+0.02,tmp['pos']+0.02],color=tmp['color'])
		ax[0].plot([yy,yy],[tmp['pos'],1.5],color=tmp['color'],lw=2)
		ax[0].plot([yy,yy],[tmp['pos']-0.02,tmp['pos']+0.02],color='white',lw=2)
		ax[0].text(yy,1,str(round(yy,2)),rotation=90,verticalalignment='center',horizontalalignment='center',backgroundcolor='white',color=tmp['color'])
		ax[0].plot([-99,-99],[-99,-99],color=tmp['color'],lw=2,label=tmp['longname']+' '+str(round(yy,2))+ \
		' ('+str(round(gmt_qu[scenario,'tas_ar5',method,1.5,25],2))+'-'+str(round(gmt_qu[scenario,'tas_ar5',method,1.5,75],2))+')')

	ax[0].plot([-1,5],[-1,5],linestyle='--',color='k')
	ax[0].set_ylim((0.61,2.3))
	ax[0].set_xlim((0.61,2.3))

	ax[0].set_xlabel('$\mathregular{GMT_{AR5}}$ $\mathregular{[^\circ C]}$')
	ax[0].set_ylabel('$\mathregular{GMT_{alt}}$ $\mathregular{[^\circ C]}$')
	ax[0].legend(loc='upper left',fontsize=12)

	for method in ['bm_pre','bm_ar5','tas_millar']:
		x_=np.asarray(gmt[scenario,:,'tas_ar5',:]).reshape(47*2880)
		y_=np.asarray(gmt[scenario,:,method,:]).reshape(47*2880)
		idx = np.isfinite(x_) & np.isfinite(y_)
		x,y=x_[idx],y_[idx]

		ax[1].scatter(x,y-x,color=plot_dict[method]['l_color'],marker='v',alpha=0.1)

		for level in gmt_qu.level:
			tmp=y[(x>level-0.05) & (x<level+0.05)]-x[(x>level-0.05) & (x<level+0.05)]
			tmp=np.nanpercentile(tmp,[0,25,50,75,100])
			ax[1].plot([level,level],tmp[[0,4]],color=plot_dict[method]['color'],lw=2)
			ax[1].plot([level-0.02,level+0.02],[tmp[2],tmp[2]],color='white',lw=2)
			ax[1].fill_between([level-0.02,level+0.02],[tmp[1],tmp[1]],[tmp[3],tmp[3]],color=plot_dict[method]['color'])


	ax[1].plot([-1,5],[0,0],linestyle='-',color='k',lw=2)
	ax[1].set_ylim((-0.8,0.4))
	ax[1].set_xlim((0.61,2.7))

	ax[1].set_xlabel('$\mathregular{GMT_{AR5}}$ $\mathregular{[^\circ C]}$')
	ax[1].set_ylabel('$\mathregular{GMT_{alt} -GMT_{AR5}}$ $\mathregular{[^\circ C]}$')

	plt.tight_layout()
	plt.savefig('plots/FIG1_'+scenario+'_qu_millar.png')




# #linear regression and estimates
#
# gmt_lr=da.DimArray(axes=[['rcp26','rcp45','rcp85'],styles,styles,['slope','slope_err','intercept','intercept_err','1.5_low','1.5_up','1.5','1.5_err']],dims=['scenario','x','y','out'])
#
# for scenario in ['rcp85']:
# 	for x_method in ['bm_ar5','bm_pre','tas_pre','tas_ar5','b_pre','b_ar5']:
# 		plt.clf()
#
# 		fig,axes=plt.subplots(nrows=2,ncols=3,figsize=(12,8))
# 		ax=axes.flatten()
# 		for y_method,pp in zip(['bm_pre','bm_ar5','tas_pre','tas_ar5','b_pre','b_ar5'],range(6)):
# 			x_=np.asarray(gmt[scenario,:,x_method,:]).reshape(47*2880)
# 			y_=np.asarray(gmt[scenario,:,y_method,:]).reshape(47*2880)
# 			idx = np.isfinite(x_) & np.isfinite(y_)
# 			x,y=x_[idx],y_[idx]
#
# 			X = sm.add_constant(x)
# 			model = sm.OLS(y, X)
# 			fitted = model.fit()
# 			x_pred = np.arange(0,5,0.01)
# 			x_pred2 = sm.add_constant(x_pred)
# 			y_pred = fitted.predict(x_pred2)
# 			sdev, lower, upper = wls_prediction_std(fitted, exog=x_pred2, alpha=1/3.)
#
# 			tmp=gmt_lr[scenario,x_method,y_method,:]
# 			tmp['slope']=fitted.params[1]
# 			tmp['intercept']=fitted.params[0]
# 			tmp['slope_err']=V[0,0]
# 			tmp['intercept_err']=V[1,1]
# 			tmp['1.5_low']=x_pred[np.argmin(abs(1.5-upper))]
# 			tmp['1.5_up']=x_pred[np.argmin(abs(1.5-lower))]
# 			tmp['1.5']=x_pred[np.argmin(abs(1.5-y_pred))]
#
# 			ax[pp].plot(x,y,marker='v',color='blue',linestyle='',alpha=0.02)
#
# 			ax[pp].plot(x_pred,y_pred,color='red')
# 			ax[pp].fill_between(x_pred,lower,upper,color='red',alpha=0.7)
# 			ax[pp].plot([tmp['1.5'],tmp['1.5']],[0,1.5],color='red',label=str(round(gmt_lr[scenario,x_method,y_method,'1.5'],4))+' ('+str(round(tmp['1.5_low'],3))+'-'+str(round(tmp['1.5_up'],3))+')')
# 			ax[pp].plot([tmp['1.5_low'],tmp['1.5_low']],[0,1.5],color='red')
# 			ax[pp].plot([tmp['1.5_up'],tmp['1.5_up']],[0,1.5],color='red')
# 			ax[pp].text(tmp['1.5'],1.1,str(round(tmp['1.5'],3)),rotation=90,verticalalignment='center',horizontalalignment='center',backgroundcolor='white',color='red')
#
# 			ax[pp].set_xlim((0.61,2.5))
# 			ax[pp].set_ylim((0.61,2.5))
# 			ax[pp].set_xlabel(x_method.replace('_',' '))
# 			ax[pp].set_ylabel(y_method.replace('_',' '))
# 			ax[pp].plot([0,5],[0,5],'k--')
# 			ax[pp].legend(loc='upper left')
#
# 		plt.savefig('plots/linear_regression_to_'+x_method+'.png')

# # FIG 1 linear regression
# for scenario in ['rcp85']:
# 	plt.clf()
# 	fig,axes=plt.subplots(nrows=1,ncols=2,figsize=(12,6))
# 	ax=axes.flatten()
#
# 	x__=np.arange(0,5,0.01)
#
# 	for method in ['tas_pre','bm_ar5','bm_pre']:
# 		x_=np.asarray(gmt[scenario,:,'tas_ar5',:]).reshape(47*2880)
# 		y_=np.asarray(gmt[scenario,:,method,:]).reshape(47*2880)
# 		idx = np.isfinite(x_) & np.isfinite(y_)
# 		x,y=x_[idx],y_[idx]
# 		ax[0].scatter(x,y,color=plot_dict[method]['l_color'],marker='1',alpha=0.2)
#
# 		lr=stats.linregress(x,y)
# 		ax[0].plot(x__,lr[1]+x__*lr[0],color=plot_dict[method]['color'],lw=2)
#
#
# 		ax[0].plot([-99,-99],[-99,-99],color=plot_dict[method]['color'],lw=2,label=plot_dict[method]['longname']+'\n$\Delta T_{alt}='+str(round(lr[0],3))+'*\Delta T_{tas}'+['-','+'][int((np.sign(lr[1])+1)/2)]+str(round(abs(lr[1]),3))+'$')
#
# 		y=(1.5-lr[1])/lr[0]
# 		ax[0].plot([y,y],[0,1.5],color=plot_dict[method]['color'],lw=2)
# 		ax[0].text(y,0.8,str(round(y,3)),rotation=90,verticalalignment='center',horizontalalignment='center',backgroundcolor='white',color=plot_dict[method]['color'])
#
# 	ax[0].plot([-1,5],[-1,5],linestyle='--',color='k')
# 	ax[0].plot([-1,5],[1.5,1.5],linestyle='--',color='k')
# 	ax[0].set_ylim((0.61,2.5))
# 	ax[0].set_xlim((0.61,2.5))
#
# 	ax[0].set_xlabel('$\Delta T_{tas}~[^\circ C]$')
# 	ax[0].set_ylabel('$\Delta T_{alt}~[^\circ C]$')
# 	ax[0].legend(loc='upper left',fontsize=12)
#
# 	for method in ['bm_ar5','bm_pre']:
# 		x_=np.asarray(gmt[scenario,:,'tas_ar5',:]).reshape(47*2880)
# 		y_=np.asarray(gmt[scenario,:,method,:]).reshape(47*2880)
# 		idx = np.isfinite(x_) & np.isfinite(y_)
# 		x,y=x_[idx],y_[idx]
#
# 		ax[1].scatter(x,y-x,color=plot_dict[method]['l_color'],marker='1',alpha=0.2)
#
# 		lr=stats.linregress(x,y)
# 		ax[1].plot(x__,lr[1]+x__*lr[0]-x__,color=plot_dict[method]['color'],lw=2)
#
# 	ax[1].plot([-1,5],[0,0],linestyle='-',color='k',lw=2)
# 	ax[1].set_ylim((-0.5,0.5))
# 	ax[1].set_xlim((0.61,2.5))
#
# 	ax[1].set_xlabel('$\Delta T_{tas}~[^\circ C]$')
# 	ax[1].set_ylabel('$\Delta T_{alt} -\Delta T_{tas}~[^\circ C]$')
#
# 	plt.tight_layout()
# 	plt.savefig('plots/FIG1_'+scenario+'.png')
# 	plt.savefig('plots/FIG1_'+scenario+'.pdf')
