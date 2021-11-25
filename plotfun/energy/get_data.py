# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 23:23:13 2021

@author: Offszanka

Loads the needed data and defines some constants.

TODO: Use other formats as geojson
TODO: Add Closing date to data

"""
import os
import datetime as dt
import warnings

import numpy as np
import pandas as pd

# TODO Do something about this someday
# To catch the following warning.
# To disable this warning, you apparently have to downgrade geopandas.
# I don't want to do this. It seems that the only thing that suffers from this
# is the performance. And right now, I do not care about performance.
# UserWarning: The Shapely GEOS version (3.9.1dev-CAPI-1.14.1) is incompatible with the GEOS version PyGEOS was compiled with (3.9.1-CAPI-1.14.2). Conversions between both will be slow.
#   shapely_geos_version, geos_capi_version_string
with warnings.catch_warnings(record=True) as w:
    import geopandas as gpd

import cv2

DATA_PATH = os.path.join('..', '..', 'data')
# PATH_INCOME = os.path.join(DATA_PATH, 'detail_tax_income.csv')
PATH_INCOME = os.path.join(DATA_PATH, 'ger_income_1999_2020.csv')
PATH_CO2 = os.path.join(DATA_PATH, "ger_co2_category.csv")

# TODO Change this!
_data = 'data'
_icons = 'icons'
_energy = 'energy'
_geodata = 'geodata'

PATH_DICT = {'energymix' : os.path.join(_data, _energy, 'ger_energymix.csv'),
             'co2' : os.path.join(_data, 'ger_co2_category.csv'),
             'power_plant_list' : os.path.join(_data, _geodata, 'power_plant_list.geojson'),
             'germany_poly' : os.path.join(_data, _geodata, 'germany_shape', 'ger_poly.shp'),
             'wind-turbine' : os.path.join(_icons, 'wind-turbine.png'),
                'wind farms' : os.path.join(_data, _geodata, 'EinheitenWind.geojson'),
               # 'wind farms' : os.path.join(_data, _geodata, 'EinheitenWind', 'EinheitenWind.shp'),
             }

STATE_ABB = {
              'BE' : 'Berlin',
              'BB' : 'Brandenburg',
              'BW' : 'Baden-Württemberg',
              'BY' : 'Bayern',
              'HB' : 'Bremen',
              'HH' : 'Hamburg',
              'HE' : 'Hessen',
              'MV' : 'Mecklenburg-Vorpommern',
              'NI' : 'Niedersachsen',
              'NW' : 'Nordrhein-Westfalen',
              'RP' : 'Rheinland-Pfalz',
              'SL' : 'Saarland',
              'SN' : 'Sachsen-Anhalt',
              'ST' : 'Sachsen',
              'SH' : 'Schleswig-Holstein',
              'TH' : 'Thüringen'
              }

# Defines the colors how the power plants appear on the map
COLOR_POWERPLANTS = {'Windenergie (Onshore-Anlage)' : 'cornflowerblue',
                     'Windenergie (Offshore-Anlage)' : 'cornflowerblue',
                     'Windenergie' : '#066395',
                     'Gas und Öl' : 'orangered',
                     'Photovoltaik' : 'gold',
                     'Wasserkraft' : 'navy',
                     'Biomasse' : 'darkgreen',
                     'Kohle' : 'saddlebrown',
                     'Sonstiges' : 'grey',
                     'Speicher' : 'hotpink',
                     'Kernenergie' : 'yellow',
                     }

# Defines the colors how the power sources appear in the pie chart.
# COLOR_ENERGYMIX = {'Windkraft' : 'cornflowerblue',
#                    'Photovoltaik' : '#ffe34d',
#                    'Geothermie' : 'darkorange',
#                    'Gas und Öl' : '#ff944d',
#                    'Kohle' : '#b85b19',
#                    'Kernernergie' : '#86ff86',
#                    'Sonstiges' : 'gray',
#                    'Biomasse' : '#91CB3E',
#                    'Wasserkraft' : '#0067cd'
#                    }
COLOR_ENERGYMIX = {'Windkraft' : '#066395',
                   'Photovoltaik' : '#ffe34d',
                   'Geothermie' : 'darkorange',
                   'Gas und Öl' : '#e17169',
                   'Kohle' : '#661615',
                   'Kernenergie' : '#ffff00',
                   'Sonstiges' : 'gray',
                   'Biomasse' : '#91CB3E',
                   'Wasserkraft' : '#1b8dff'
                   }


GREEN_ENERGY = {'Windkraft', 'Photovoltaik', 'Geothermie', 'Biomasse', 'Wasserkraft'}

def _parse_power_plant_list(needed_cols = None, color_book = None,*,
                            more_dense_openings = False,
                            default_color = 'white'):
    """
    Reads the power plant list file and returns it. In addition, the color
    column is added which will be needed for the plotting.

    Parameters
    ----------
    needed_cols : list, optional
        The columns which will be in the returned dataframe.
        By default, all columns are returned.
        The colors table will always be included if 'power source' is included.
    color_book : dictionary, optional
        Each power source should be identified with a color.
        The default is COLOR_POWERPLANTS.
    more_dense_openings : boolean, optional
        Determines if the opening dates will be shuffled (inside the year).
        The default is False. TODO: REMOVE
    default_color : string, optional
        Default color if power source is not included in color_book.
        The default is 'white'.

    Returns
    -------
    geopandas.GeoDataFrame
        The power plant list. Extended!.

    """
    df = gpd.read_file(PATH_DICT['power_plant_list'])
    if needed_cols is None:
        needed_cols = df.keys()

    df.drop(columns=[col for col in df.keys() if col not in needed_cols],
            inplace=True)

    if color_book is None:
        color_book = COLOR_POWERPLANTS

    if 'opening date' in needed_cols:
        def date_parse(s):
            return dt.datetime.strptime(s, '%d.%m.%Y')
        df['opening date'] = df['opening date'].apply(date_parse)

        if more_dense_openings:
            def get_random_date(date):
                if date.day == 1 and date.month == 1:
                    start = date.toordinal()
                    end = dt.date(date.year, 12, 31).toordinal()
                    random_date = dt.date.fromordinal(np.random.randint(start, end+1))

                    return random_date
                else:
                    return date

            df['opening date'] = df['opening date'].apply(get_random_date)

    if 'isEEG' in needed_cols:
        df['isEEG'] = df['isEEG'] == 'Ja'

    if 'energy source' in needed_cols:
        df['color'] = df['energy source'].apply(lambda x : color_book.get(x, default_color))

    return df

def _parse_wind_turbines(needed_cols=None, color_book=None,
                         default_color=None):
    """Loads the wind turbines. See_parse_power_plant_list.
    color_book: dict of colors. If an entry is not given COLOR_POWERPLANTS
    is used instead.
    TODO integrate into _parse_power_plant_list.
    """
    df = gpd.read_file(PATH_DICT['wind farms'])

    t, ext = os.path.splitext(PATH_DICT['wind farms'])
    if ext == '.shp':
        # This is needed because .shp shortened the lengthy column titles
        df.rename(columns={'energy sou' : 'energy source',
                           'opening da' : 'opening date'}, inplace=True)
    elif ext == '.geojson':
        df.rename(columns={'Energietraeger' : 'energy source'}, inplace=True)

    if needed_cols is None:
        needed_cols = df.keys() # ['geometry', 'opening date', 'energy source']

    df.drop(columns=[col for col in df.keys() if col not in needed_cols],
            inplace=True)

    # def date_parse(s):
    #         return dt.datetime.strptime(s, '%d.%m.%Y')

    if 'opening date' in needed_cols:
        # df['opening date'] = df['opening date'].apply(date_parse)
        df['opening date'] = pd.to_datetime(df['opening date'])

    if 'energy source' in needed_cols:
        # df.rename(columns={'Energietraeger':'energy source'}, inplace=True)
        if color_book is None:
            color_book = {}

        def choose_color(key):
            return color_book.get(key, COLOR_POWERPLANTS.get(key, default_color))

        df['color'] = df['energy source'].apply(choose_color)

    return df

def _parse_energymix():
    df = pd.read_csv(PATH_DICT['energymix'], index_col=0)
    return df

def _parse_co2(**kwargs):
    return pd.read_csv(PATH_DICT['co2'], index_col=0)

def _parse_poly(path=None, needed_columns=None):
    """Loads the shape file. (or geojson.)
    needed_columns is a list describing the columns which stays in the dataframe.
    Default behaviour is only geometry.
    """
    if path == None:
        path = PATH_DICT['germany_poly']

    poly = gpd.read_file(path)
    if needed_columns is None:
        needed_columns = ['geometry']
    poly.drop(columns=[col for col in poly.keys() if col not in needed_columns],
              inplace=True)
    return poly

def _parse_wind_turbine_icon(shape = None, alpha = 1):
    """Returns the wind turbine icon with transparent background.
    Use shape (eg. (256, 256)) to resize the image.
    alpha determines the transparency of the image"""
    assert 0 <= alpha <= 1

    icon = cv2.imread(PATH_DICT['wind-turbine'], cv2.IMREAD_UNCHANGED)
    icon = cv2.cvtColor(icon, cv2.COLOR_BGRA2RGBA)
    if shape is not None:
        icon = cv2.resize(icon, shape)
    icon[:,:,3] = alpha*icon[:,:,3]
    return icon

_FUNC_DICT = {'power_plant_list' : _parse_power_plant_list,
              'energymix' : _parse_energymix,
              'co2' : _parse_co2,
              'germany_poly' : _parse_poly,
              'wind-turbine': _parse_wind_turbine_icon,
              'wind farms' : _parse_wind_turbines,
              }

def get_data(name, **kwargs):

    # Get advanced results if key is in _FUNC_DICT
    if name in _FUNC_DICT:
        return _FUNC_DICT[name](**kwargs)

    if name in PATH_DICT:
        file = PATH_DICT[name]
        t, ext = os.path.splitext(file)
        if ext in ('.geojson', '.shp'):
            return gpd.read_file(file)
        else:
            return pd.read_csv(file)
    else:
        # If it is not in PATH_DICT (hence not known) show the list of
        # available keys.
        alt = list(set(PATH_DICT.keys()).union(_FUNC_DICT))
        # every key should look like '...' and the last key should be introduced with or.
        alt_s = r"'"
        alt_s += r"', '".join(alt[:-1])
        alt_s += rf"' or '{alt[-1]}'"
        raise ValueError(rf"I do not know '{name}'. Try it again with {alt_s}")

# Ordnet den Zahlen der Dateien des Markstammdatenregisters den Energieträger zu.
# Scheint so, dass dies manuell erfolgen muss :(
energy_cbook = {
    2497 : 'Windenergie'}

def parse_data_marktstammdatenregister(path, needed_columns=None, to_save=False,
                                       to_filter = False,
                                       s_path = None, driver='GeoJSON'):
    """
    Parse the data from https://www.marktstammdatenregister.de.
    Returns only the needed information.
    The save location is derived from the path if not explicitly given.

    Parameters
    ----------
    path : TYPE
        DESCRIPTION.
    needed_columns : TYPE, optional
        DESCRIPTION. The default is None.
    to_save : TYPE, optional
        DESCRIPTION. The default is False.
    s_path : str, optional
        save path. By default the name stays the same with another extension.
        By default geojson is used. (Because it simple, easy to understand and somewhat stable)
    driver : str, optional
        Will only be needed if s_path is given and another file
        extension then geojson is used.
        The default is 'GeoJSON'.

    Returns
    -------
    the parsed GeoDataFrame.

    """
    # TODO Make needed_columns relevant.
    import lxml.etree as etree
    pf = etree.parse(path)
    df = pd.read_xml(etree.tostring(pf))

    if needed_columns is None:
        needed_columns = set(['EinheitMastrNummer', 'Landkreis', 'Gemeinde', 'Postleitzahl', 'Ort', 'Laengengrad',
                          'Breitengrad', 'Inbetriebnahmedatum', 'Energietraeger',
                          'Bruttoleistung', 'Nettonennleistung'])
    elif needed_columns == 'all':
        needed_columns = df.keys()

    # This is needed instead of df[needed_columns] because this method does not
    # return a view of the dataframe enabling inplace=True later.
    df.drop(columns=[col for col in df.keys() if col not in needed_columns],
            inplace=True)

    df.rename(columns={'Laengengrad' : 'lon' , 'Breitengrad' : 'lat'}, inplace=True)

    # drop all rows where the location (lon, lat) is not given
    df = df[df[['lon', 'lat', 'Inbetriebnahmedatum']].notna().all(axis=1)]

    if 'Inbetriebnahmedatum' in df.keys():
        # def date_parse(s):
        #     dt2 = dt.datetime.strptime(s, '%Y-%m-%d')
        #     return dt2.strftime('%d.%m.%Y')

        df.rename(columns={'Inbetriebnahmedatum' : 'opening date',
                           }, inplace=True)
        # df['opening date'] = df['opening date'].apply(date_parse)
        # Much faster than the above method
        df['opening date'] = pd.to_datetime(df['opening date'])

    if 'Energietraeger' in df.keys():
        df['Energietraeger'] = df['Energietraeger'].apply(lambda x : energy_cbook.get(x, None))

    # Convert to GeoDataFrame. According to https://www.marktstammdatenregister.de
    # the crs is WGS84 which in geopandas is EPSG:4326
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat),
                           crs='EPSG:4326')

    gdf.drop(columns = ['lon', 'lat'], inplace=True)

    if to_filter:
        # Some wind turbines are located out of germany somehow. (Out of maritime territory as well)
        # They are discarded.
        ger_poly = get_data('germany_poly', needed_columns=['geometry'])
        gdf = gpd.overlay(ger_poly, gdf, how='intersection', keep_geom_type=False)

    if to_save:
        if s_path is None:
            t, ext = os.path.splitext(path)
            s_path = t + '.geojson'
        gdf.to_file(s_path, driver=driver)
    return gdf

# if __name__ == '__main__':
#     wpath = os.path.join('data', 'osm_data', 'EinheitenWind.xml')
#     dff = parse_data_marktstammdatenregister(wpath, 'all')
