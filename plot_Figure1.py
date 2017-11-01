import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import itertools
import matplotlib
import seaborn as sns

gmt=da.read_nc('data/gmt_plot_ready.nc')['gmt']
gmt_qu=da.read_nc('data/gmt_quantiles.nc')['gmt_qu']

# FIG 1
plot_dict={
	'gmt_sat':{'l_color':'orange','color':'darkorange','longname':'$\mathregular{GMT_{SAT}}$','pos':0.65},
	'gmt_millar':{'l_color':'cornflowerblue','color':sns.color_palette()[0],'longname':'$\mathregular{GMT_{M17}}$','pos':0.85},
	'gmt_bm':{'l_color':'tomato','color':sns.color_palette()[2],'longname':'$\mathregular{GMT_{blend-mask}}$','pos':0.75},
}
for scenario in ['rcp85']:
	plt.close()
	fig,axes=plt.subplots(nrows=1,ncols=2,figsize=(10,5))
	ax=axes.flatten()
	ax[0].fill_between([-1,5],[1.55,1.55],[1.45,1.45],color='white')
	ax[0].plot([-1,5],[1.45,1.45],linestyle='--',color='k')
	ax[0].plot([-1,5],[1.55,1.55],linestyle='--',color='k')
	x__=np.arange(0,5,0.01)

	for method in ['gmt_sat','gmt_millar','gmt_bm']:
		tmp=plot_dict[method]
		x_=np.asarray(gmt[scenario,:,'gmt_ar5',:]).reshape(len(gmt.model)*len(gmt.time))
		y_=np.asarray(gmt[scenario,:,method,:]).reshape(len(gmt.model)*len(gmt.time))
		idx = np.isfinite(x_) & np.isfinite(y_)
		x,y=x_[idx],y_[idx]
		ax[0].scatter(x,y,color=tmp['l_color'],marker='v',alpha=0.3)


	for method in ['gmt_millar','gmt_bm','gmt_sat']:
		tmp=plot_dict[method]
		yy=gmt_qu[scenario,'gmt_ar5',method,1.5,50]
		ax[0].plot([gmt_qu[scenario,'gmt_ar5',method,1.5,0],gmt_qu[scenario,'gmt_ar5',method,1.5,100]],[tmp['pos'],tmp['pos']],color=tmp['color'])
		ax[0].fill_between([gmt_qu[scenario,'gmt_ar5',method,1.5,1/6.*100],gmt_qu[scenario,'gmt_ar5',method,1.5,5/6.*100]],[tmp['pos']-0.02,tmp['pos']-0.02],[tmp['pos']+0.02,tmp['pos']+0.02],color=tmp['color'])
		ax[0].plot([yy,yy],[tmp['pos'],1.5],color=tmp['color'],lw=2)
		ax[0].plot([yy,yy],[tmp['pos']-0.02,tmp['pos']+0.02],color='white',lw=2)
		#ax[0].text(yy,1,str(round(yy,2)),rotation=90,verticalalignment='center',horizontalalignment='center',backgroundcolor='white',color=tmp['color'])
		ax[0].plot([-99,-99],[-99,-99],color=tmp['color'],lw=2,label=tmp['longname']+' '+str(round(yy,2))+ \
		' ('+str(round(gmt_qu[scenario,'gmt_ar5',method,1.5,1/6.*100],2))+'-'+str(round(gmt_qu[scenario,'gmt_ar5',method,1.5,5/6.*100],2))+')')

	ax[0].plot([-1,5],[-1,5],linestyle='--',color='k')
	ax[0].set_ylim((0.61,2.3))
	ax[0].set_xlim((0.61,2.3))
	ax[0].text(-0.1, 1.02, 'a', transform=ax[0].transAxes,fontsize=18, fontweight='bold', va='top', ha='right')
	ax[0].set_xlabel('$\mathregular{GMT_{AR5}}$ $\mathregular{[^\circ C]}$')
	ax[0].set_ylabel('$\mathregular{GMT_{alt}}$ $\mathregular{[^\circ C]}$')
	ax[0].legend(loc='upper left',fontsize=12)

	for method in ['gmt_bm']:
		x_=np.asarray(gmt[scenario,:,'gmt_ar5',:]).reshape(len(gmt.model)*len(gmt.time))
		y_=np.asarray(gmt[scenario,:,method,:]).reshape(len(gmt.model)*len(gmt.time))
		idx = np.isfinite(x_) & np.isfinite(y_)
		x,y=x_[idx],y_[idx]

		ax[1].scatter(x,y-x,color=plot_dict[method]['l_color'],marker='v',alpha=0.3)

		for level in gmt_qu.level:
			tmp=y[(x>level-0.05) & (x<level+0.05)]-x[(x>level-0.05) & (x<level+0.05)]
			tmp=np.nanpercentile(tmp,[0,1/6.*100,50,5/6.*100,100])
			ax[1].plot([level,level],tmp[[0,4]],color=plot_dict[method]['color'],lw=2)
			ax[1].plot([level-0.02,level+0.02],[tmp[2],tmp[2]],color='white',lw=2)
			ax[1].fill_between([level-0.02,level+0.02],[tmp[1],tmp[1]],[tmp[3],tmp[3]],color=plot_dict[method]['color'])


	ax[1].plot([-1,5],[0,0],linestyle='-',color='k',lw=2)
	ax[1].set_ylim((-0.8,0.4))
	ax[1].set_xlim((0.61,2.7))
	ax[1].text(-0.1, 1.02, 'b', transform=ax[1].transAxes,fontsize=18, fontweight='bold', va='top', ha='right')

	ax[1].set_xlabel('$\mathregular{GMT_{AR5}}$ $\mathregular{[^\circ C]}$')
	ax[1].set_ylabel('$\mathregular{GMT_{blend-mask} -GMT_{AR5}}$ $\mathregular{[^\circ C]}$')

	plt.tight_layout()
	plt.savefig('plots/FIG1_'+scenario+'_qu.png')
	plt.savefig('plots/FIG1_'+scenario+'_qu.pdf')
