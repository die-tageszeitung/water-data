#!/usr/bin/env python3

import world_bank_data as wb
from pandas import DataFrame
from datetime import datetime

def get_all_countries(reverse=False):
    """
    returns a mapping dict from country-codes used by the worldbank to the realnames.
    
    @param reverse: if true a mapping from country-names to the country-code is returned
    
    @return dict: with index country-code and value of the country-name
    """
    
    result = {}
    df = DataFrame(wb.get_countries()).reset_index()
    df = df[df['region'] != "Aggregates"]
    
    if reverse:
        for i, row in df.iterrows():
            result[row['name']] = row['id']
    else:
        for i, row in df.iterrows():
            result[row['id']] = row['name']


    return result

def fetch_series(series=['SI.SPR.PCAP','SI.POV.XPND.MD','SP.POP.TOTL','AG.SRF.TOTL.K2'],
                 scale=['SI.SPR.PCAP','SI.POV.XPND.MD'], scaleby=360,
                 date="1980:%s" %(datetime.now().year)):
    """
    fetches a definded indicators and formates them in a wide-dataframe

    @param series: an array of names/string series as defined by the worldbank - defaults to:
      SI.POV.XPND.MD: Median daily per capita income or consumption expenditure (2011 PPP)
      SI.SPR.PCAP: Survey mean consumption or income per capita, total population (2011 PPP $ per day)
      SP.POP.TOTL: Population, total
      AG.SRF.TOTL.K2: Surface area (sq. km)
    @param scale: array of series-names that are scaled 
    @param scaleby: the scalefactor to apply to the series that should be scaled - used to scale daily to year by 360
    @param date: the including timerange - defaults to 1980 upto the current year in the format 'from:to' ex. '1980:2020'

    @return: a dataframe with selected series as columns and country, countrycode, year
    """
    odf = DataFrame()
    for i in series:
        df = DataFrame(wb.get_series(i, date=date,id_or_value='id', simplify_index=True))
        df = df[df[i].notnull()]
        if i in scale:
            df[i] = df[i] * scaleby
        odf = odf.append(df)
    return odf.reset_index()


if __name__ == "__main__":
    print(get_all_countries())
    print(fetch_series().describe())
