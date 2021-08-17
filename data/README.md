# Explanation of the data files and source references:

1. **ger_energy_not_renewable.csv**: 
Contains gross energy production per year divided into categories. 
Contains the years 2002 - 2020. The unit is MWh. It seems that the data for renewable energy is not given. 
Thus, another reference is used for these energy sources.
This data is from 

    *© Statistisches Bundesamt (Destatis), 2021*,
    Stand: 30.07.2021,
    [**GENESIS-Tabelle:43311-0001**](https://www-genesis.destatis.de/genesis//online?operation=table&code=43311-0001&bypass=true&levelindex=0&levelid=1628192807653#abreadcrumb).
    This data is licensed under the 
    ["Datenlizenz Deutschland – Namensnennung – Version 2.0"](https://www.govdata.de/dl-de/by-2-0).
    The data itself was not changed. 
    However, in the presantation they were grouped into the categories shown and it was processed into 
    the needed data structure.

1. **ger_green_energy_.csv** :
   Contains the gross green net energy production per year divided into categories. 
   Contains the years 1990 - 2020. The unit is GWh. 
   This data is from 

    *Arbeitsgruppe Erneuerbare Energien-Statistik (AGEE-Stat)*,
    Stand: Februar 2021,
    [**Zeitreihen zur Entwicklung der erneuerbaren Energien in Deutschland**](https://www.erneuerbare-energien.de/EE/Navigation/DE/Service/Erneuerbare_Energien_in_Zahlen/Zeitreihen/zeitreihen.html)
    (last visit 29.07.2021).
    This data is licensed under
    ["CC BY-ND 3.0 DE"](https://creativecommons.org/licenses/by-nd/3.0/de/).

1. **ger_energymix.csv** : 
Is the concatenation of the files (1., 2.). 
The unit is GWh.

1. **ger_co2.csv** : 
CO2-Emissions per year divided into categories. The unit is Million tons. The source material is from

   *Umweltbundesamt*,
   [**Emissionsübersichten in den Sektoren des Bundesklimaschutzgesetzes, 
   Vorjahreschätzung der deutschen Treibhausgas-Emissionen für das Jahr 2020**](https://www.umweltbundesamt.de/dokument/emissionsuebersichten-in-den-sektoren-des)
   (last visit 9.08.2021). 
   For the license conditions see [here](https://www.umweltbundesamt.de/datenschutz-haftung#c-urheber-und-kennzeichenrecht).
   The data was summarised in the categories "Energiewirtschaft"(Energy industry) and "Sonstiges"(Other). Other contains all greenhousegases except 
   from Energy industry.

1. **power_plant_geo.geojson** : 
A (not complete) list of power plants in germany (More than 10MW). The table contains the power plant names, locations, net energy production 
in MWh, energy source, opening date and whether is eligible by EEG. 
It seems that the source material did not contain all power plant locations.
In addition, some zip codes/opening dates were also not given. As far as possible, this data was completed. 
The rest is ignored. 
The source material is from 

    *Bundesnetzagentur für Elektrizität, Gas, Telekommunikation, Post und Eisenbahnen*,
    [**Kraftwerksliste der Bundesnetzagentur - Stand: 19.01.2021,**](https://www.bundesnetzagentur.de/DE/Sachgebiete/ElektrizitaetundGas/Unternehmen_Institutionen/Versorgungssicherheit/Erzeugungskapazitaeten/Kraftwerksliste/start.html)
    (last visit 29.07.2021).
    This data is licensed under the
    ["Data licence Germany – attribution – version 2.0"](https://www.govdata.de/dl-de/by-2-0).
    The data was (heavily) changed: some zip codes/opening dates were added/reinterpreted. Some rows were discarded
    In the presentation the dates with only years where randomly shuffled into the year 
    to present a smoother experience.
    
   The geographical location for each zip code is from [zauberware, postal-codes-json-xml-csv](https://github.com/zauberware/postal-codes-json-xml-csv)

1. **EinheitenWind.shp**:
Contains the wind power plants of germany. It contains the location and the opening date for each power plant among other things. 
This list seems to be more complete than *power_plant_geo.geojson* and will be used from now on for the plotting.
The data is from

   *Bundesnetzagentur für Elektrizität, Gas, Telekommunikation, Post und Eisenbahnen*,
   [**Marktstammdatenregister**](https://www.marktstammdatenregister.de)
   (last visist 9.08.2021). 
   This data is licensed under the 
   ["Data licence Germany – attribution – version 2.0"](https://www.govdata.de/dl-de/by-2-0).
   The column titles were changed, some number codes were decrypted and color&geometry columns were added. 
   The data rows which did not contain the location or the opening date were discarded.
   Moreover, this file contains only a tiny fraction of the vast amount of data that the original file provided. 

1. **germany_poly.geojson** : 
A shape from germany. You can find the data [here](https://github.com/datasets/geo-countries).
    Credits to
    [Lexman](http://github.com/lexman), 
    [Open Knowledge Foundation](http://okfn.org/) 
    and
    [Natural earth](https://www.naturalearthdata.com/)
    for providing/processing the data!

1. **ger.geojson** :
A json file containing the geometry data about germany and its states. The germany shape is from (5.) while
the state boundary data comes from

    *Natural Earth*,
    [Admin 1 - States, Provinces,](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-1-states-provinces/)
    (last visit 8.8.2021).
    This data is 
    [public domain](https://www.naturalearthdata.com/about/terms-of-use/).

1. I do not need this anymore/yet. But here is still free data available. Might be cool.

    *© GeoBasis-DE / BKG 2021*,
    Stand: 01.01.2021, 
    [Verwaltungsgebiete 1:250 000 (kompakt),](https://gdz.bkg.bund.de/index.php/default/digitale-geodaten/verwaltungsgebiete/verwaltungsgebiete-1-250-000-kompakt-stand-01-01-vg250-kompakt-01-01.html)
    (last visit 30.07.2021).
    This data is licensed under the 
    ["Data licence Germany – attribution – version 2.0"](https://www.govdata.de/dl-de/by-2-0).




