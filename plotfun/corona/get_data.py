# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 14:03:09 2021

@author: Offszanka

Loads the needed data and defines some constants.

"""
# # Enter this, to change to plot-fun dir. TODO REmove.
# os.chdir(os.path.join('..', 'plot-fun'))

import glob
import os

import geopandas as gpd
import numpy as np
import pandas as pd
import scipy.ndimage.filters as filters
from tqdm import tqdm

# DATA_PATH = os.path.join('..', '..', 'data')
DATA_PATH = 'data'

PATH_CORONA_DATA = os.path.join(DATA_PATH, 'corona-data', '2021_11_22 Fallzahlen_Kum_Tab.xlsx')
PATH_DE_LANDKREISE = os.path.join(DATA_PATH, 'geodata', 'vg250-ew_12-31.gk3.shape.ebenen',
                             'vg250-ew_ebenen_1231', 'VG250_KRS.shp')


ars_book = {
    "Schleswig-Holstein" : "01",
    "Hamburg" : "02",
    "Niedersachsen" : "03",
    "Bremen" : "04",
    "Nordrhein-Westfalen" : "05",
    "Hessen" : "06",
    "Rheinland-Pfalz" : "07",
    "Baden-Württemberg" : "08",
    "Bayern" : "09",
    "Saarland" : "10",
    "Berlin" : "11",
    "Brandenburg" : "12",
    "Mecklenburg-Vorpommern" : "13",
    "Sachsen" : "14",
    "Sachsen-Anhalt" : "15",
    "Thüringen" : "16",
}
ars_book_ = {ars_book[key] : key for key in ars_book}

# These two population numbers and LKNR can be found in PATH_DE_LANDKREISE
w_ewz = 117967
e_ewz = 41970
w_lknr = "16063"
e_lknr = "16056"
to_date = pd.Timestamp(year=2020, month=11, day=18)
date_reform = pd.Timestamp(year=2021, month=7, day=14)


def shape():
    dgf = gpd.read_file(PATH_DE_LANDKREISE)
    # Remove the entries whose populution is 0.
    dgf.drop(dgf.loc[dgf.EWZ == 0].index, inplace=True)
    dgf['ARS'] = dgf['ARS'].astype(str).str.zfill(5)
    dgf.set_index('ARS', inplace=True, verify_integrity=True)

    # Because of a particularity in the data,
    # the counties 16056(Eisenach) and 16063(Wartburgkreis) must be combined
    # eisenach = dgf[dgf['ARS'] == '16056']
    # wartburgkreis = dgf[dgf['ARS'] == '16063']
    eisenach = dgf.loc[[e_lknr]]
    wartburgkreis = dgf.loc[[w_lknr]]
    geom = wartburgkreis.union(eisenach.geometry, align=False)
    dgf.loc[wartburgkreis.index, 'geometry'] = geom
    dgf.drop(eisenach.index, inplace=True)

    return dgf


def parse_corona_data():
    """Loads the csv-files and parses them to a simple and fast-readable format. 
    Use only for the raw data and do not to plot the graphs with this function. 
    Use get_corona_data for this."""
    corona_dict= dict()
    files = glob.glob(os.path.join(DATA_PATH, 'corona-data', 'counties', '*'))
    for fi in tqdm(files):
        # See e.g. https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/f7bdcbe7188545daabe65e6c9e2a4379_0/about
        # for a documentation of the files.
        df = pd.read_csv(fi)
        df['Meldedatum'] = pd.to_datetime(df['Meldedatum'])
        # Condition which is mentioned above in the source.
        df = df.loc[df['NeuerFall'].isin((0,1)),:].copy() # Copy to supress the SettingWithCopyWarning TODO Better pls.

        counties = df.groupby(by='IdLandkreis')
        for name, group in counties:
            name = str(name).zfill(5)
            if name in corona_dict:
                raise RuntimeError(f'This should absolutely NOT happen. {name} is in corona_dict.')
            corona_dict[name] = group.groupby(by='Meldedatum').agg(np.sum)['AnzahlFall']
    df_corona = pd.DataFrame(corona_dict).T
    df_corona.fillna(0, inplace=True)
    return df_corona


def get_corona_data():
    """Reads the files and transforms them to plotable DataFrames. Also calculates the 7-day incidences."""
    df = pd.read_csv(os.path.join(DATA_PATH, 'corona-data', '2020_11_24_CoronaFallzahlen_counties.csv'), index_col=0)
    df.columns = pd.to_datetime(df.columns)
    df.index = df.index.astype(str).str.zfill(5)
    dshape = shape()

    # On the map Berlin is only present as one. Thus we sum the cases.
    bidx = set(df.index) - set(dshape.index)
    df.loc['11000'] = df.loc[bidx].sum(axis=0)
    df.drop(bidx, inplace=True)

    # Calculate the 7-day incidences.
    df_7days = df.rolling(7, axis=1).sum()
    df_7days.fillna(0, inplace=True)

    df_total = df.sum(axis=0)
    df_total = df_total.rolling(7).sum()
    df_total.fillna(0, inplace=True)

    df_7days = (df_7days.divide(dshape['EWZ'], axis='index')*100000)
    df_total = df_total/dshape['EWZ'].sum()*100000
    
    df_7days.sort_index(inplace=True)
    df_total.sort_index(inplace=True)
    
    return df_7days, df_total, dshape


# def parse_data():
#     df_corona = pd.read_excel(PATH_CORONA_DATA, "LK_7-Tage-Inzidenz (fixiert)",
#                        skiprows = [0, 1, 2, 3, 416, 417, 418, 419, 420])
#     # LKNR (= ARS) is a unique key for each county
#     df_corona['LKNR'] = df_corona['LKNR'].astype(str).str.zfill(5)
#     df_corona.set_index('LKNR', inplace=True, verify_integrity=True)
#     df_corona.drop(columns=['NR', 'LK'], inplace=True)
#     df_corona.columns = pd.to_datetime(df_corona.columns, dayfirst=True)
#     dshape = shape()

#     # Because of a particularity in the data,
#     # the counties 16056(Eisenach) and 16063(Wartburgkreis) must be combined
#     # We resolve this by simply combining these two counties.
#     al = e_ewz/w_ewz
#     ig = (1/(al+1))*df_corona.loc[w_lknr, df_corona.columns < date_reform] + (1/(1 + 1/al)) * df_corona.loc[e_lknr, df_corona.columns < date_reform]
#     df_corona.loc[w_lknr, df_corona.columns < date_reform] = ig
#     df_corona.drop(e_lknr, inplace=True)

#     # In the Corona table Berlin is splitted to multiple district.
#     # We do not want this here. So we remove them and add them later
#     df_corona.drop(set(df_corona.index) - set(dshape.index), inplace=True)

#     # Only from 18th Nov 2020 the data is given for each county.
#     # We circumvent this by assigning each county in the state the same incidence.
#     df_states = pd.read_excel(PATH_CORONA_DATA, "BL_7-Tage-Inzidenz (fixiert)",
#                               skiprows = [0, 1])
#     # This step is needed to safely convert the columns to its respective dates.
#     df_states.set_index('Unnamed: 0', inplace=True, verify_integrity=True)
#     df_states.columns = pd.to_datetime(df_states.columns, dayfirst=True)
#     df_states.drop(columns = df_states.columns[df_states.columns >= to_date], inplace=True)
#     df_states.reset_index(drop=False, inplace=True)
#     df_states.rename(columns = {'Unnamed: 0': 'temp'}, inplace=True)

#     df_states_complete = pd.read_excel(PATH_CORONA_DATA, "BL_7-Tage-Inzidenz (fixiert)",
#                                        skiprows = [0, 1])
#     df_states_complete.set_index('Unnamed: 0', inplace=True, verify_integrity=True)
#     df_states_complete.columns = pd.to_datetime(df_states_complete.columns, dayfirst=True)

#     # Add Berlin to Corona data
#     df_corona.loc["11000"] = df_states_complete.loc['Berlin'] # This only adds the dates from up_to.
#     # Merge the dataframes.
#     df_corona['temp'] = df_corona.index.str[:2]
#     df_corona.replace({'temp':ars_book_}, inplace=True)
#     _df = df_corona.merge(df_states, how='left', on = 'temp')
#     df_corona = _df.set_index(df_corona.index)
#     df_corona.drop(columns = ['temp'], inplace=True)
#     df_corona = df_corona[df_corona.columns.sort_values()]

#     return df_corona, df_states_complete, dshape
