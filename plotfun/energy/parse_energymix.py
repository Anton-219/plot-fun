# -*- coding: utf-8 -*-
"""
Created on Tue Jul 27 16:21:56 2021

@author: Offszanka

This module parses the date into the file energymix.
"""

import os

import numpy as np
import pandas as pd

DATA_PATH = os.path.join('data', 'energy')
PATH_ENERGY = os.path.join(DATA_PATH, 'ger_energy_not_renewable.csv') # Not renewable.
# TODO! Vorischt
PATH_GREEN_ENERGY = os.path.join(DATA_PATH, 'ger_green_energy_.csv') # renewable

# These rows give no information and are empty (values are 0  or N/A)
# They are given by (table_energy from below)
# list = table_energy.index[(table_energy == 0).all(axis=1)] + ['Insgesamt']
ROWS_TO_DROP_NO_INFORMATION = ['Kohlenwertstoffe aus Steinkohle', 'Raffineriegas', 'Solarthermie',
       'Sonstige Steinkohlen', 'Steinkohlenbriketts', 'Steinkohlenkoks',
       'Strom (Elektrokessel)', 'Wasserstoff',
       'Wärmepumpen (Erd- und Umweltwärme)', 'Insgesamt']

# I think that these categories represent renewable energies. They are included
# in the ger_green_energy.csv file.
ROWS_TO_DROP_GREEN = ['Abfall (Hausmüll, Industrie)',
                      'Abfall (Hausmüll, Siedlungsabfälle)',
                      'Abfall (Industrie)',
                      'Andere Speicher',
                      'Biogas',
                      'Biomethan (Bioerdgas)',
                      'Deponiegas',
                      'Feste biogene Stoffe',
                      'Flüssige biogene Stoffe',
                      'Geothermie',
                      'Klärgas',
                      'Klärschlamm',
                      'Laufwasser',
                      'Photovoltaik',
                      'Pumpspeicher mit natürlichem Zufluss',
                      'Pumpspeicher ohne natürlichen Zufluss',
                      'Speicherwasser',
                      'Windkraft',
                      'Pumpspeicherwasser',
                      'Sonstige erneuerbare Energien']

CATEGORIES = {'Gas und Öl' : ['Kokereigas', 'Erdgas, Erdölgas', 'Flüssiggas',
                       'Grubengas', 'Hochofengas', 'Sonstige hergestellte Gase',
                       'Dieselkraftstoff', 'Heizöl, leicht', 'Heizöl, schwer',
                      'Petrolkoks', 'Sonstige Mineralölprodukte'],
              'Kohle' : ['Braunkohlenbriketts', 'Braunkohlenkoks',
                              'Hartbraunkohlen', 'Rohbraunkohlen',
                              'Sonstige Braunkohlen', 'Staub- und Trockenkohle',
                              'Steinkohlen'],
              'Kernenergie' : ['Kernenergie'],
              'Sonstiges' : ['Wärme', 'Sonstige Energieträger', 'Wirbelschichtkohle'],
              'Wasserkraft' : ['Wasserkraft'],
              'Photovoltaik' : ['Photovoltaik'],
              'Windkraft' : ['Windenergie an Land', 'Windenergie auf See'],
              'Biomasse' : ['biogene Festbrennstoffe', 'biogene flüssige Brennstoffe',
                            'Biogas', 'Biomethan', 'Klärgas', 'Deponiegas',
                            'biogener Anteil des Abfalls'],
              'Geothermie' : ['Geothermie'],
              }

ROWS_TO_DROP = ROWS_TO_DROP_NO_INFORMATION + ROWS_TO_DROP_GREEN
### First, process the data of Destatis.

# Read the file and remove all the stuff which is unnecessary for data processing
df_energy = pd.read_csv(PATH_ENERGY,
                        encoding = "ISO-8859-1", sep=';', na_values=['-', '.'],
                        skiprows=[0,1,2,3,4,6], skipfooter=5, engine='python')

# Rename some columns and remove the 'Elektrizitätserzeugung (netto)' column
# which will not be needed.
df_energy.rename(columns={'Unnamed: 0' : 'year',
                          'Unnamed: 1' : 'category',
                          'Elektrizitätserzeugung (brutto)' : 'consumption'},
                 inplace=True)
df_energy.drop(columns='Elektrizitätserzeugung (netto)', inplace=True)

# Also, drop the the rows which happens to be also in the green energy table
# or are not needed or resulted to be empty (filled with zeros, N/A etc.)


# Transform the energy into GWH to be compatible with the other (green energy) table.
df_energy['consumption'] = df_energy['consumption']/1e3

# Group the categories together
table_energy = df_energy.pivot(index='category', columns='year').fillna(0.0)
table_energy.drop(table_energy.loc[ROWS_TO_DROP].index, inplace=True)

# To remove the multiindices
table_energy.columns = table_energy.columns.droplevel(0)

def categorize(table : pd.DataFrame, cat : dict) -> pd.DataFrame:
    """Categorize the data into the categories cat"""
    df_return = pd.DataFrame()
    for key in cat:
        df = table.loc[table.index.intersection(cat[key])]
        if not df.empty:
            df_return[key] = df.sum(axis=0)
    return df_return

df_energy_reduced = categorize(table_energy, CATEGORIES)

## Now, parse the green energy data
df_energy = pd.read_csv(PATH_GREEN_ENERGY,
                        encoding = "ISO-8859-1", sep=';', engine='python')
df_energy.set_index('Kategorie (in GWh)', inplace=True)
df_energy = df_energy.applymap(lambda x : pd.to_numeric((x.replace(',',''))))
df_energy = categorize(df_energy, CATEGORIES)
df_energy.set_index(df_energy.index.astype(np.int), inplace=True)
#
df_energy_reduced[df_energy.keys()] = df_energy

# Save the resulting data
df_energy_reduced.to_csv(os.path.join(DATA_PATH, 'ger_energymix.csv'))