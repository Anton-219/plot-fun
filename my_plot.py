# -*- coding: utf-8 -*-
"""
Created on Sat Jul 24 15:43:16 2021

@author: Offszanka

Display energymix together with co2 - emissions and a map showing
wind power plants in germany.

TODO: More efficient. But it works and this is fine.
TODO: MAYBE export the pie chart to a function
"""

from collections import namedtuple
import datetime as dt

import matplotlib.pyplot as plt
import matplotlib.lines as mlines

import numpy as np

## Custom modules
from get_data import get_data, COLOR_ENERGYMIX, GREEN_ENERGY
import plot_help


# Use dark style and than customize it a bit.
plt.style.use('dark_background')

plt.rcParams.update({
    'figure.facecolor': '#131313',
    'figure.edgecolor': '#131313',
    'savefig.facecolor': '#131313',
    'savefig.edgecolor': '#131313',
    'text.color': '#dddddd'
    })

## Constants
# TODO (maybe) add all the constant to a dictionary.
SOURCE_TEXT = """Quellen: Bundesnetzagentur,  Umweltbundesamt, Statistisches Bundesamt (Destatis)"""
POS_SOURCE_TEXT = 0.68, 0.005
WEDGES_WIDTH = 0.45 # Defines the widths of the pie chart wedges
INNER_CIRCLE_RADIUS = 0.75*(1-WEDGES_WIDTH) # Defines the radius of the inner circle. (which breathes)
DOT_MARKERSIZE = 1

color_book = dict(
    ger_inner = '#3c3d42',#paleturquoise
    ger_border = '#131313',
    ger_alpha = 1.,
    co2_Energiewirtschaft = '#dfdfdf', #'#fff0ec', # 'peachpuff'
    co2_Sonstiges = '#3c3d42', #'#9a9a9a',# 'dimgray'
    energymix_green = '#004b00',
    energymix_alpha = 0.5,
    inner_circle = '#595959',#4f2e4f',
    inner_circle_bound = '#808080',# '#7f4a7f',
    colors_power_plants = {'Windenergie' : '#79ff62'}, # #6eb0fe
    colors_energymix = {'Kohle' : '#6f40ff',
                        'Gas und Öl' : '#84398e',
                        'Kernenergie' : '#f43ffe',
                        'Photovoltaik' : '#fff770',
                        'Wasserkraft' : '#65e3ef',
                        'Biomasse' : '#ffc77c',
                        'Windkraft' : '#79ff62', #'#6eb0fe',
                        'Geothermie' : '#ff7cb9',
                        'Sonstiges' : 'grey',
                        },
)

## Load and preprocess the data
df_energymix = get_data('energymix')
# new column order
df_energymix = df_energymix[['Gas und Öl', 'Kohle', 'Kernenergie','Sonstiges',
                             'Wasserkraft', 'Photovoltaik', 'Biomasse',
                             'Windkraft', 'Geothermie']]

df_co2 = get_data('co2')
df_co2['Sonstiges'] = df_co2[[col for col in df_co2.keys() if col != 'Energiewirtschaft']].sum(axis=1)
df_co2.drop(columns=[col for col in df_co2.keys()
                     if col not in ('Energiewirtschaft', 'Sonstiges')],
            inplace=True)

df_co2 = df_co2.loc[2002:]

# This was the old data from Kraftwerksliste
# df_pplist = get_data('power_plant_list', more_dense_openings=True)
# df_pplist = df_pplist[df_pplist['energy source'] == 'Windenergie (Onshore-Anlage)']
# df_pplist['energy source'] = df_pplist['energy source'].\
#     replace('Windenergie (Onshore-Anlage)', 'Windanlagen (Onshore)')

df_wind = get_data('wind farms', color_book=color_book['colors_power_plants'])
# This is possible because right now every power plant here is a wind power plant
# To simply change the name in the legendary.
df_wind['energy source'] = 'Windkraftanlagen'

df_pplist = df_wind
ger_poly = get_data('germany_poly')



# icon_wind_turbine = get_data('wind-turbine', alpha=0.09)

## Define all the needed functions.
def _get_interpolation(data, val):
    """Returns an interpolation of the data between current year and next year."""
    year = val['year']
    alpha = val['alpha']

    # Check for the value.
    # Need to theck for alpha = 0 and alpha = 1 if year is the last year
    # which would result in a KeyError as year+1 will not exist then.
    if alpha == 0:
        return data.loc[year]
    elif alpha == 1:
        return data.loc[year+1]
    else:
        return (1 - alpha)*data.loc[year] + alpha*data.loc[year+1]

def _calc_circle_size(x, min_x, max_x, r_min, r_max):
    """
    Calculates the circle size depending on the given values.

    If x == min_data -> size = r_min
    If x == max_data -> size = r_max
    In between: linear interpolation.

    Parameters
    ----------
    x : float
        Value between min_x and max_x.
    min_x : float
        The minimal reachable number.
    max_x : float
        The maximal reachable number.
    r_min : float
        The minimal radius.
    r_max : float
        The maximal radius.

    Returns
    -------
    float
        circle size.
    """
    return (x - min_x)/(max_x - min_x) * (r_max - r_min) + r_min

def plot_energymix(ax, val, max_data = df_energymix.sum(axis=1).max(),
                   max_size = 1-WEDGES_WIDTH):
    """Plots the energymix part"""
    global df_energymix

    ax.clear()
    ax.set_title('Strommix', y=0.91)
    ax.axis('equal')

    # Calculate the data values between the years to let plot appear smooth.
    data = _get_interpolation(df_energymix, val)

    ## Plot the outer part which will indicate the green energy
    per_g = data[GREEN_ENERGY].sum()/data.sum()

    # This is if I want to sort the columns maybe later
    kwargs = {'colors' : [color_book['colors_energymix'][k] for k in df_energymix.keys()],
              'wedgeprops' : {'width' : WEDGES_WIDTH,
                              'linewidth' : 0.6,
                              'edgecolor' : color_book['ger_border']},
              }

    # The first color will be omitted later (alpha=0)
    pp,_ = ax.pie([1-per_g, per_g], colors=['black', color_book['energymix_green']],
                  radius=1.05, wedgeprops=kwargs['wedgeprops'])

    # Disable the other part of the pie chart i.e. do not explicitly
    # show the not green energy part.
    pp[0].set_alpha(0)

    def calc_xy(x,y):
        return 0.95*np.sign(x), -1

    def c_style(wedge):
        ang = (wedge.theta2 - wedge.theta1)/2 + wedge.theta1
        return  f"arc,angleA={90*np.sign(ang-300)},angleB=45,armA=30"

    plot_help.make_annotations([pp[1]], ax, ['Erneuerbare Energien'],
                               calc_xy=calc_xy,
                               c_style=c_style)

    # plot the data part
    pie_chart = ax.pie(data.values, **kwargs)

    # Add transparency to the not green energy parts.
    wedges = np.asarray(pie_chart[0])
    [w.set_alpha(color_book['energymix_alpha']) for w in wedges[~data.index.isin(GREEN_ENERGY)]]


    total_production = np.round(data.sum()/1e3, 1)
    ax.text(0.0, 0, f"{total_production} TWh",
            ha='center', va='center', fontsize=16,
            )

    ax.legend(pie_chart[0], data.index, loc='center right', frameon=False)

    # Plot the inner circle.
    circle_size = _calc_circle_size(data.sum(), 0, max_data, 0, max_size)

    circle_bound = plt.Circle((0.,0.), max_size, edgecolor=color_book['inner_circle_bound'],
                              lw=0.7, fill=False)

    circle_inner = plt.Circle((0.,0.), circle_size, color=color_book['inner_circle'])
    ax.add_patch(circle_inner)
    ax.add_patch(circle_bound)
    return pie_chart

def plot_co2(ax, val, max_data=df_co2.sum(axis=1).max(),
             max_size=1-WEDGES_WIDTH):
    """Plots the co2 part"""
    global df_co2

    ax.clear()
    ax.axis('equal')
    ax.set_title('Treibhausgasemissionen (in CO2-Äquivalente)', y = 0.94) # 0.94 empirically found

    Prop = namedtuple('Prop', 'color explode')
    d = {'Energiewirtschaft' : Prop(color_book['co2_Energiewirtschaft'], 0.0),
         'Sonstiges' : Prop(color_book['co2_Sonstiges'], 0.0)}
    kwargs = {'colors' : [d[k].color for k in df_co2.keys()],
              'explode' : [d[k].explode for k in df_co2.keys()],
              'wedgeprops' : {'width' : WEDGES_WIDTH,
                              'linewidth' : 0.6,
                              'edgecolor' : color_book['ger_border']},
              }

    data = _get_interpolation(df_co2, val)

    pie_chart = ax.pie(data.values, autopct='%1.1f%%', pctdistance=0.75,
                       **kwargs)

    # Change the percent text sizes and colors
    for autotext in pie_chart[2]:
        autotext.set_color('black')
        autotext.set_fontsize(12)

    pie_chart[0][1].set_alpha(0.5)

    def calc_xy(x,y):
        return 0.95*np.sign(x), np.clip(1.4*y, -1.02, 1.02)

    plot_help.make_annotations(pie_chart[0][0], ax, data.index,
                               calc_xy=calc_xy)

    total = np.round(data.sum(), 1)
    ax.text(0.0, 0, f"{total} MT",
            ha='center', va='center', fontsize=16,
            )

    # plot the inner circle.
    circle_size = _calc_circle_size(data.sum(), 0, max_data, 0, max_size)
    circle_bound = plt.Circle((0.,0.), max_size, edgecolor=color_book['inner_circle_bound'],
                              lw=0.7, fill=False)
    circle_inner = plt.Circle((0.,0.), circle_size, color=color_book['inner_circle'])
    ax.add_patch(circle_bound)
    ax.add_patch(circle_inner)

    return pie_chart

def _get_interpolation_map(df_map, val, before_val = None,*,
                           time_col = 'opening date'):
    """Gets an interpolation of the map between the years.
    Note that -depending on the options - here the inbetween opening dates are
    random."""

    # + 1 is needed because this is how the date is interpreted here.
    # If the year is shown then the pie charts already show the data for
    # this year. The map data however would lag behind.
    year = val['year'] + 1
    alpha = val['alpha']

    # Get the current moment (indicated by alpha)
    # by adding the percentage of the passed year
    # (alpha) to the current year. (Ignore leap years.)
    current_year = dt.datetime(year, 1,1)
    current_moment = current_year + dt.timedelta(days = alpha*365)

    if before_val is None:
        ddf = df_map[df_map[time_col] <= current_moment]
        return ddf, ddf
    else:
        byear = before_val['year']
        balpha = before_val['alpha']
        before_year = dt.datetime(byear, 1,1)
        before_moment = before_year + dt.timedelta(days = balpha*365)

        m1 = (df_map[time_col] <= current_moment)
        m2 = (df_map[time_col] > before_moment)

        return df_map[m1 & m2], df_map[m1]

before_val = None

def plot_map(ax, val,
         plot_args_intermap={},
         plot_args_backmap={},
         # extent=[6.2, 12.9, 48, 54.5],
         enable_before_val = False,
         ):
    global df_pplist, ger_poly

    if not enable_before_val:
        ax.clear()
        ax.set_axis_off()
        ax.axis('equal')
        ger_poly.plot(ax=ax, edgecolor=None, color=color_book['ger_inner'],
                      alpha=color_book['ger_alpha'])
        ger_poly.boundary.plot(ax=ax, edgecolor=color_book['ger_border'], # color_book['ger_border']
                               color=None, lw=0.8)
        # _ger_country.plot(ax=ax, edgecolor='black')

    # I removed  the plotting of the wind turbine icon because as one might say
    # in good german: "Das ist hässlich!"
    # However, I let it here. Maybe someday I will need this.
    # if extent is not None:
    #     # Plot the wind turbine icon
    #     minx, miny, maxx, maxy = ger_poly.bounds.iloc[0]
    #     ax.imshow(icon_wind_turbine, zorder=1, extent=extent)

    if enable_before_val:
        global before_val
        bval = before_val
        before_val = val
    else:
        bval = None
    inter_map, until_now_map = _get_interpolation_map(df_pplist, val, bval)

    if inter_map.empty:
        return
    else:
        group = until_now_map.groupby(['energy source'])
        color_list = group['color'].unique()

        # How can I manage the legend markers better?
        handlers = [mlines.Line2D([], [], color=col[0], marker='o', linestyle='None')
                    for col in color_list]

        name_labels = [f"{name}: {num:05d}"  for name, num in zip(color_list.index, group.size())]

        points = inter_map.geometry
        ax.plot(points.x, points.y, 'o', color=inter_map['color'].iloc[0],
                zorder=2, **plot_args_intermap)

        # inter_map.plot(ax=ax, color=inter_map['color'],
        #                   zorder=2,
        #                   **plot_args_intermap
        #                   )

        ax.legend(handlers, name_labels,
                  loc='lower center', frameon=False,
                  bbox_to_anchor=(0., 0.0))

## For the plotting.
plot_functions = {'map' : plot_map,
                  'energymix' : plot_energymix,
                  'co2' : plot_co2}

table = np.asarray([[1,2],
                    [1,3]])

def image_make(year, save_name = None):
    gp = plot_help.GridPlot(table, plot_functions = plot_functions,
                            name_book = {1 : 'map',
                                         2 : 'energymix',
                                         3 : 'co2'},
                            fig_kwargs = dict(constrained_layout=True,
                                              figsize=(15, 9),
                                              ))

    # Add the text for the sources.
    gp['fig'].text(*POS_SOURCE_TEXT, SOURCE_TEXT, fontsize=8)

    to_save = save_name is not None
    gp['fig'].suptitle(f'Jahr {year}', y = 0.98, fontsize=24,
                       fontdict={'family' : 'arial'})
    gp.plot_frame(dict(year=year, alpha=0.),
                  {'energymix' : dict(max_size=INNER_CIRCLE_RADIUS,
                                        max_data=df_energymix.sum(axis=1).max()),
                    'co2': dict(max_size=INNER_CIRCLE_RADIUS,
                                        max_data=df_co2.sum(axis=1).max()),
                    'map' : dict(plot_args_intermap=dict(markersize=DOT_MARKERSIZE),
                                 enable_before_val=False),
                    },
                  to_save=to_save, save_path=save_name
                  )


def animation_make(year_range, save_name = None, approx=10):
    """
    Makes an animation for the given diagram. Optionally, it saves

    Parameters
    ----------
    year_range : TYPE
        DESCRIPTION.
    save_name : TYPE, optional
        DESCRIPTION. The default is None.
    approx : TYPE, optional
        Smoothness parameter. approx-1 much images we have between year.
        The default is 10.

    Returns
    -------
    The animation.
    """
    gp = plot_help.GridPlot(table, plot_functions = plot_functions,
                            name_book = {1 : 'map',
                                         2 : 'energymix',
                                         3 : 'co2'},
                            fig_kwargs = dict(constrained_layout=True,
                                              figsize=(15, 9)),
                            )

    # Add the text for the sources.
    gp['fig'].text(*POS_SOURCE_TEXT, SOURCE_TEXT, fontsize=8)

    to_save = save_name is not None

    def helper(yz, approx_):
        alphas, rs = np.linspace(0,1, num=approx_, endpoint=False, retstep=True)
        for year in yz:
            for alpha in alphas:
                yield {'year' : year,
                        'alpha': alpha+rs,}

    def anim_update(val, obj, fargs):
        year = val['year']
        for kf in obj.plot_functions:
            obj.plot_functions[kf](obj[kf], val, **fargs.get(kf, {}))

        current_year = int(np.floor(year + val['alpha']))
        obj['fig'].suptitle(f'Jahr {current_year}', y=0.98, fontsize=24,
                            fontdict={'family' : 'arial'})

    def init_func():
        global before_val
        before_val = None

        gp['map'].set_axis_off()
        gp['map'].axis('equal')
        ger_poly.plot(ax=gp['map'],
                      color=color_book['ger_inner'],
                      alpha=color_book['ger_alpha'])
        ger_poly.boundary.plot(ax=gp['map'], edgecolor=color_book['ger_border'], # color_book['ger_border']
                               color=None, lw=0.8)

    # This is needed because otherwise animation.save does not properly work
    frames=[v for v in helper(np.arange(min(year_range), max(year_range)),
                              approx_=approx)]

    kw = dict(fps=12, bitrate=1800)

    anim=gp.plot_animation(frames,
                           fargs=({'energymix':dict(max_size=INNER_CIRCLE_RADIUS,
                                                      max_data=df_energymix.sum(axis=1).max()),
                                   'co2':dict(max_size=INNER_CIRCLE_RADIUS,
                                               max_data=df_co2.sum(axis=1).max()),
                                   'map':dict(plot_args_intermap=dict(markersize=DOT_MARKERSIZE),
                                              enable_before_val=True)},),
                           anim_update=anim_update, init_func=init_func,
                           to_save=to_save, save_path=save_name,
                           writer_args=kw)
    return anim

if __name__ == '__main__':

    # # image_make(2002)
    image_make(2020)
    # anim = animation_make((2002, 2020))
    # anim = animation_make((2002, 2020), 'germany_energymix.mp4',  approx=10)