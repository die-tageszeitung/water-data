#!/usr/bin/env python3

import world_bank_data as wb
from pandas import DataFrame
from datetime import datetime
import os
import pickle
import plotly.express as px

default_series=['SI.SPR.PCAP','SI.POV.XPND.MD','SP.POP.TOTL','AG.SRF.TOTL.K2']

def get_all_countries(reverse=False,cachedir="data/cache",includeaggs=False):
    """
    returns a mapping dict from country-codes used by the worldbank to the realnames.
    
    @param reverse: if true a mapping from country-names to the country-code is returned
    @param cachedir: since the data is on a remote server and cannot be downloaded as persistent file, 
                     the result of the api-call is stored in this cachedir
    
    @return dict: with index country-code and value of the country-name
    """
    
    result = {}
    df = get_regionnames(cachedir=cachedir)
    if includeaggs==False:
        df = df[df['region'] != "Aggregates"]
    
    if reverse:
        for i, row in df.iterrows():
            result[row['name']] = row['id']
    else:
        for i, row in df.iterrows():
            result[row['id']] = row['name']


    return result

def get_regionnames(cachedir="data/cache"):
    """
    returns a df of iso3 country-codes used by the worldbank to the realnames.
    
    @param cachedir: since the data is on a remote server and cannot be downloaded as persistent file, 
                     the result of the api-call is stored in this cachedir
    
    @return dict: with index country-code and value of the country-name
    """
    
    result = {}
    df = None
    os.makedirs(cachedir,exist_ok=True)

    cached_df_filename = cachedir+"/countrycodes.p"
    try:
        with open(cached_df_filename, 'rb') as fd:
            print("Reading Data from cached file: %s" %(cached_df_filename))
            df = pickle.load(fd)
    except:
        df = DataFrame(wb.get_countries()).reset_index()
        print("Writing cached_df_file: %s" %(cached_df_filename))
        with open(cached_df_filename, 'wb') as fd:
            pickle.dump(df, fd)
    
    return df

def fetch_series(series=default_series,
                 scale=['SI.SPR.PCAP','SI.POV.XPND.MD'], scaleby=360,
                 date="1980:%s" %(datetime.now().year), cachedir="data/cache"):
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
    @param cachedir: since the data is on a remote server and cannot be downloaded as persistent file, 
                     the result of the api-call is stored in this cachedir

    @return: a dataframe with selected series as columns and country, countrycode, year
    """
    odf = DataFrame()
    os.makedirs(cachedir,exist_ok=True)

    for i in series:
        cached_df_filename = cachedir+"/"+i+".p"
        df = None
        try:
            with open(cached_df_filename, 'rb') as fd:
                print("Reading Data from cached file: %s" %(cached_df_filename))
                df = pickle.load(fd)
        except:
            df = DataFrame(wb.get_series(i, date=date,id_or_value='id', simplify_index=True))
            print("Writing cached_df_file: %s" %(cached_df_filename))
            with open(cached_df_filename, 'wb') as fd:
                pickle.dump(df, fd)

        df = df[df[i].notnull()]
        if i in scale:
            df[i] = df[i] * scaleby
        odf = odf.append(df)
    odf = DataFrame(odf.groupby(['Country','Year']).sum())
    odf = odf.reset_index()
    return odf


if __name__ == "__main__":
    print(get_all_countries())
    print(fetch_series().sample(10))
    print(fetch_series().describe())
