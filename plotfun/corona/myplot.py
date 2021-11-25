# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 21:54:02 2021

@author: Offszanka
"""
import locale
import os

import matplotlib as mpl
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from .. import plot_help
from . import get_data

SOURCE_TEXT = """Quellen: Robert-Koch-Institut und GeoBasis-DE / BKG 2021"""
POS_SOURCE_TEXT = 0.34, 0.005
POS_DATE = {'x' : 0.1, 'y' : 0.95}
POS_TITLE = 0.1, 0.96
POS_INCIDENCE_TOTAL = 0.575, 0.02

locale.setlocale(locale.LC_TIME, 'de_DE')

df_corona, df_total, dshape = get_data.get_corona_data()

colormap = sns.color_palette("rocket_r", as_cmap=True)
color_blue = sns.color_palette("colorblind")[0]

dmin = df_corona.min().min()
dmax = 300

def plot_map(ax, val, ):
    global dshape
    ax.clear()
    ax.set_title('7-Tage Inzidenz / Landkreise', loc='right',
                 fontdict = dict(fontsize = 10), y = -0.056, color='dimgray')
    ax.set_axis_off()
    data = df_corona[val]
    dshape['data'] = data
    dshape.plot(column='data', ax=ax, cmap=colormap, vmin=dmin, vmax=dmax)
    ax.margins(y=0)


def plot_incidence(ax, val):
    ax.clear()
    # ax.set_title('7-Tage Inzidenz / Deutschland', loc='right',
    #              fontdict = dict(fontsize = 10), y = -2, color='dimgray')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    data = df_total[:val]
    data.plot(ax=ax, color=color_blue)
    ax.fill_between(data.index, data, color=color_blue, alpha=0.5)
    ax.margins(y=0)


def white_space(ax, val):
    ax.clear()
    ax.set_axis_off()


table = np.asarray([[1],
                    [2],
                    [3]])

plot_functions = {'map' : plot_map,
                  'incidence' : plot_incidence,
                  'white_space' : white_space
                  }


def animation_make(from_date = None, to_date = None, save_name = None, approx=10):
    gp = plot_help.GridPlot(table, plot_functions = plot_functions,
                            name_book = {1 : 'map',
                                         2 : 'incidence',
                                         3 : 'white_space'},
                            grid_kwargs={'height_ratios':[7, 1, 0.15],
                                         'bottom':0.1,
                                         'top':0.9,
                                         'hspace': 0.0},
                            fig_kwargs = dict(constrained_layout=True,
                                              figsize=(5, 9)),
                            )
    # Add the text for the sources.
    gp['fig'].text(*POS_SOURCE_TEXT, SOURCE_TEXT, fontsize=8)
    gp['fig'].text(*POS_TITLE, "Corona-Pandemie in Deutschland", fontsize=18,
                        fontdict={'family' : 'arial'})
    gp['fig'].text(*POS_INCIDENCE_TOTAL, '7-Tage Inzidenz / Deutschland', 
                   fontdict = dict(fontsize = 10), color='dimgray')
    to_save = save_name is not None
    # if from_date is None:
    #     from_date = df_corona.columns.min()
    # if to_date is None:
    #     to_date = df_corona.columns.max()
    # date_range = pd.date_range(start=from_date, end=to_date, freq='D')
    date_range = df_total.index

    def init_func():
        axins = inset_axes(gp['map'],
                    width="80%",  # width = 5% of parent_bbox width
                    height="4%",  # height : 50%
                    loc='lower left',
                    bbox_to_anchor=(0.1, -0.1, 1, 1),
                    bbox_transform=gp['map'].transAxes,
                    borderpad=0,
                    )
        cbar = gp['fig'].colorbar(mpl.cm.ScalarMappable(cmap=colormap), cax=axins, ticks=[0, 0.2, 0.4, 0.6, 0.8, 1],
                                  orientation='horizontal')
        cbar.ax.set_xticklabels([  0,  60, 120, 180, 240, ">300"])

    def anim_update(val, obj, fargs):
        for kf in obj.plot_functions:
            obj.plot_functions[kf](obj[kf], val)

        obj['fig'].suptitle(val.strftime('%d. %B %Y'),
                            **POS_DATE, fontsize=14,
                            ha = 'left',
                            fontdict={'family' : 'arial'})

    kw = dict(fps=12, bitrate=1800)
    anim=gp.plot_animation(date_range,
                           anim_update=anim_update,
                           init_func=init_func,
                           to_save=to_save, save_path=save_name,
                           writer_args=kw,
                           end_time = 2)
    return anim


def main():
    anim = animation_make(
        # pd.Timestamp(year=2021, month=3, day=24).tz_localize('utc'),
        #                   pd.Timestamp(year=2021, month=3, day=28).tz_localize('utc'),
                          save_name=os.path.join('data', 'corona', 'corona_pandemic_ger.mp4'),
                          )
    return df_corona, dshape, anim


