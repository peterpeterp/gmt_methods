import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import itertools
import matplotlib
import seaborn as sns

def running_mean_func(xx,N):
	if N==1:
		return xx
	if N!=1:
	    x=np.ma.masked_invalid(xx.copy())
	    ru_mean=x.copy()*np.nan
	    for t in range(int(N/2),len(x)-int(N/2)):
	        ru_mean[t]=np.nanmean(x[t-int(N/2):t+int(N/2)])
	    return ru_mean


gmt=da.read_nc('data/gmt_plot_ready.nc')['gmt']
gmt_qu=da.read_nc('data/gmt_quantiles.nc')['gmt_qu']

time_ax=da.DimArray(axes=[np.array(gmt.time)],dims=['time'])
time_ax[:]=gmt.time

# read HadCRUT4
dat=open('data/HadCRUT4_gmt.txt','r').read()
had4=[]
year=[]
for line in dat.split('\n')[::2]:
	year.append(line.split(' ')[0])
	for anom in line.split(' ')[1:-1]:
		if anom!='':
			had4.append(float(anom))
# get HadCRUT4 for 1850-2016
had4_gmt_=np.array(had4[:-12])
had4_gmt=da.DimArray(axes=[np.array(gmt.time)],dims=['time'])
had4_gmt[1850:2017]=had4_gmt_
ref_ar5=gmt.time[(gmt.time>1986) & (gmt.time<2006)]
had4_gmt[:]=had4_gmt[:]-np.nanmean(had4_gmt[ref_ar5])+0.61

print 'hadcrut4',np.nanmean(had4_gmt[2010:2020])
print 'blend-mask',np.nanmean(gmt['rcp85',:,'gmt_bm',2010:2020])-0.93
print 'millar',np.nanmean(gmt['rcp85',:,'gmt_millar',2010:2020])
print 'blend-mask',np.nanmean(gmt['rcp85',:,'gmt_bm',2015:2016])-0.93

# FIG SI 1
plot_dict={
	'gmt_sat':{'l_color':'orange','color':'darkorange','longname':'$\mathregular{GMT_{SAT}}$','pos':0.65,'lsty':'-'},
	'gmt_ar5':{'l_color':'lawngreen','color':sns.color_palette()[1],'longname':'$\mathregular{GMT_{AR5}}$','pos':0.65,'lsty':'-'},
	'gmt_millar':{'l_color':'cornflowerblue','color':sns.color_palette()[0],'longname':'$\mathregular{GMT_{M17}}$','pos':0.75,'lsty':'-'},
	'gmt_1':{'l_color':'cornflowerblue','color':sns.color_palette()[0],'longname':'$\mathregular{GMT_{1}}$','pos':0.75,'lsty':'--'},
	'gmt_1.1':{'l_color':'cornflowerblue','color':sns.color_palette()[0],'longname':'$\mathregular{GMT_{1.1}}$','pos':0.75,'lsty':':'},
	'gmt_bm':{'l_color':'tomato','color':sns.color_palette()[2],'longname':'$\mathregular{GMT_{blend-mask}}$','pos':0.85,'lsty':'-'},
	'gmt_b':{'l_color':'tomato','color':sns.color_palette()[2],'longname':'$\mathregular{GMT_{blend}}$','pos':0.85,'lsty':'--'},
}
plt.close()
fig,axes=plt.subplots(nrows=1,ncols=2,figsize=(10,5))
ax=axes.flatten()
ax[0].plot(time_ax,running_mean_func(had4_gmt,12),'gray',lw=2,alpha=0.6,label='HadCRUT4')
for method in gmt.style:
	tmp=plot_dict[method]
	ax[0].plot(time_ax,running_mean_func(np.nanmean(gmt['rcp85',:,method,:],axis=0),12),label=tmp['longname'],color=tmp['color'],linestyle=tmp['lsty'])

ax[0].set_ylim((-0.3,2.7))
ax[0].set_xlim((1950,2050))
ax[0].text(-0.1, 1.02, 'a', transform=ax[0].transAxes,fontsize=18, fontweight='bold', va='top', ha='right')
ax[0].set_ylabel('$\mathregular{GMT}$ $\mathregular{[^\circ C]}$')
ax[0].legend(loc='upper left',fontsize=10)

for method in gmt.style:
	tmp=plot_dict[method]
	ax[1].plot(time_ax,running_mean_func(np.nanmean(gmt['rcp85',:,method,:],axis=0),240),label=tmp['longname'],color=tmp['color'],linestyle=tmp['lsty'])

ax[1].plot([1996,1996],[0,3],color='k')
ax[1].text(1996,1.7,str(1996),rotation=90,verticalalignment='center',horizontalalignment='center',backgroundcolor='white',color=tmp['color'])
ax[1].plot([2015,2015],[0,3],color='k')
ax[1].text(2015,1.7,str(2015),rotation=90,verticalalignment='center',horizontalalignment='center',backgroundcolor='white',color=tmp['color'])
ax[1].plot([1850,2100],[1.5,1.5],color='k')
ax[1].text(1990,1.5,str(1.5),rotation=0,verticalalignment='center',horizontalalignment='center',backgroundcolor='white',color=tmp['color'])
ax[1].set_ylim((0,1.8))
ax[1].set_xlim((1986,2040))
ax[1].text(-0.1, 1.02, 'b', transform=ax[1].transAxes,fontsize=18, fontweight='bold', va='top', ha='right')
ax[1].set_ylabel('$\mathregular{GMT}$ $\mathregular{[^\circ C]}$')

plt.tight_layout()
plt.savefig('plots/GMT_method_check.png')
plt.savefig('plots/GMT_method_check.pdf')


for method in gmt.style:
	print method, np.nanmean(gmt['rcp85',:,method,1850:1900]), np.nanmean(gmt['rcp85',:,method,1986:2006]), np.nanmean(gmt['rcp85',:,method,2010:2020])
