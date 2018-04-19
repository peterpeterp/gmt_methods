import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import itertools
import matplotlib
import seaborn as sns; sns.set()




# FIG 1
plot_dict={
	'gmt_sat':{'l_color':'orange','color':'darkorange','longname':'$\mathregular{GMT_{SAT}}$','pos':0.65,'z':2},
	'gmt_b':{'l_color':'tomato','color':sns.color_palette()[2],'longname':'$\mathregular{GMT_{blend}}$','pos':0.75,'z':3},
}

scenario='rcp85'


for mod_style in ['model','runs']:
	for av_style in ['20year']:
		for preind_name in ['1861-1880','1850-1900']:
			gmt=da.read_nc('data/gmt_plot_ready_'+av_style+'_'+mod_style+'_'+preind_name+'.nc')['gmt']

			plt.close()
			fig,axes=plt.subplots(nrows=1,ncols=2,figsize=(10,5))
			ax=axes.flatten()
			ax[0].plot([-1,5],[1.5,1.5],linestyle='--',color='k',zorder=0)
			x__=np.arange(0,5,0.01)

			for method in ['gmt_sat','gmt_b']:
				tmp=plot_dict[method]
				x_=np.asarray(gmt[scenario,:,'gmt_ar5',:]).reshape(len(gmt.model)*len(gmt.time))
				y_=np.asarray(gmt[scenario,:,method,:]).reshape(len(gmt.model)*len(gmt.time))
				idx = np.isfinite(x_) & np.isfinite(y_)
				x,y=x_[idx],y_[idx]
				ax[0].scatter(x,y,color=tmp['l_color'],marker='v',alpha=0.3)

			for method in ['gmt_b','gmt_sat']:
				tmp=plot_dict[method]
				gmt_ar5_15=[]
				for model in gmt.model:
					t_15=np.nanargmin(abs(gmt[scenario,model,method,:].values-1.5))
					ax[0].scatter(gmt[scenario,model,'gmt_ar5',:].ix[t_15],gmt[scenario,model,method,:].ix[t_15],color=tmp['color'],marker='*',alpha=1)
					gmt_ar5_15.append(gmt[scenario,model,'gmt_ar5',:].ix[t_15])

				spread=np.percentile(gmt_ar5_15,[0,1/6.*100,50,5/6.*100,100])
				yy=np.mean(gmt_ar5_15)
				#yy=np.median(gmt_ar5_15)
				ax[0].plot([spread[0],spread[-1]],[tmp['pos'],tmp['pos']],color=tmp['color'],zorder=tmp['z'])
				ax[0].fill_between([spread[1],spread[3]],[tmp['pos']-0.02,tmp['pos']-0.02],[tmp['pos']+0.02,tmp['pos']+0.02],color=tmp['color'],zorder=tmp['z'])
				ax[0].plot([yy,yy],[tmp['pos'],1.5],color=tmp['color'],lw=2,zorder=tmp['z'])
				ax[0].plot([yy,yy],[tmp['pos']-0.02,tmp['pos']+0.02],color='white',lw=2,zorder=tmp['z'])
				#ax[0].text(yy,1,str(round(yy,2)),rotation=90,verticalalignment='center',horizontalalignment='center',backgroundcolor='white',color=tmp['color'])
				ax[0].plot([-99,-99],[-99,-99],color=tmp['color'],lw=2,label=tmp['longname']+' '+str(round(yy,2))+ \
				' ('+str(round(spread[0],2))+'-'+str(round(spread[-1],2))+')')

			ax[0].plot([-1,5],[-1,5],linestyle='--',color='k')
			ax[0].set_ylim((0.61,2.3))
			ax[0].set_xlim((0.61,2.3))
			ax[0].text(-0.1, 1.02, 'a', transform=ax[0].transAxes,fontsize=18, fontweight='bold', va='top', ha='right')
			ax[0].set_xlabel('$\mathregular{GMT_{AR5}}$ $\mathregular{[^\circ C]}$')
			ax[0].set_ylabel('$\mathregular{GMT_{alt}}$ $\mathregular{[^\circ C]}$')
			ax[0].legend(loc='upper left',fontsize=12)

			for method in ['gmt_b']:
				x_=np.asarray(gmt[scenario,:,'gmt_ar5',:]).reshape(len(gmt.model)*len(gmt.time))
				y_=np.asarray(gmt[scenario,:,method,:]).reshape(len(gmt.model)*len(gmt.time))
				idx = np.isfinite(x_) & np.isfinite(y_)
				x,y=x_[idx],y_[idx]

				ax[1].scatter(x,y-x,color=plot_dict[method]['l_color'],marker='v',alpha=0.3)

				for level in [1,1.5,2,2.5]:
					diff=[]
					for model in gmt.model:
						x=gmt[scenario,model,'gmt_ar5',:].values
						y=gmt[scenario,model,'gmt_bm',:].values-x
						t_15=np.nanargmin(abs(x-level))
						diff.append(y[t_15])

					tmp=np.nanpercentile(diff,[0,1/6.*100,50,5/6.*100,100])
					ax[1].plot([level,level],tmp[[0,4]],color=plot_dict[method]['color'],lw=2)
					ax[1].plot([level-0.02,level+0.02],[np.mean(diff),np.mean(diff)],color='white',lw=2)
					ax[1].fill_between([level-0.02,level+0.02],[tmp[1],tmp[1]],[tmp[3],tmp[3]],color=plot_dict[method]['color'])


			ax[1].plot([-1,5],[0,0],linestyle='-',color='k',lw=2)
			ax[1].set_ylim((-0.8,0.4))
			ax[1].set_xlim((0.61,2.7))
			ax[1].text(-0.1, 1.02, 'b', transform=ax[1].transAxes,fontsize=18, fontweight='bold', va='top', ha='right')

			ax[1].set_xlabel('$\mathregular{GMT_{AR5}}$ $\mathregular{[^\circ C]}$')
			ax[1].set_ylabel('$\mathregular{GMT_{blend-mask} -GMT_{AR5}}$ $\mathregular{[^\circ C]}$')

			plt.tight_layout()
			plt.savefig('plots/Figure_SI_blend_'+av_style+'_'+mod_style+'_'+preind_name+'.png',dpi=300)
			plt.savefig('plots/Figure_SI_blend_'+av_style+'_'+mod_style+'_'+preind_name+'.pdf')





			#
