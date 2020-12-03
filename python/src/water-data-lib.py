#!/usr/bin/env python

from pandas import DataFrame, read_csv
import pandas as pd

import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime
import json
datasets = {
    "fullset": ["crs1994-73.zip","crs1999-95.zip","crs2000-01.zip","crs2002-03.zip","crs2005-04.zip","crs2006.zip",
                "crs2007.zip","crs2008.zip","crs2009.zip","crs2010.zip","crs2011.zip","crs2012.zip","crs2013.zip",
                "crs2014.zip","crs2015.zip","crs2016.zip","crs2017.zip","crs2018.zip","crs2019.zip"],

    "sane commitment": ["crs2005-04.zip","crs2006.zip","crs2007.zip","crs2008.zip",
                          "crs2009.zip","crs2010.zip","crs2011.zip","crs2012.zip","crs2013.zip","crs2014.zip",
                          "crs2015.zip","crs2016.zip","crs2017.zip","crs2018.zip","crs2019.zip"],

    "sane disbursement": ["crs2007.zip","crs2008.zip","crs2009.zip","crs2010.zip","crs2011.zip",
                          "crs2012.zip","crs2013.zip","crs2014.zip","crs2015.zip","crs2016.zip",
                          "crs2017.zip","crs2018.zip","crs2019.zip"],

    "sane": ["crs2010.zip","crs2011.zip","crs2012.zip","crs2013.zip","crs2014.zip","crs2015.zip",
             "crs2016.zip","crs2017.zip","crs2018.zip","crs2019.zip"],

    "playset": ["crs2017.zip",'crs2018.zip','crs2019.zip','crs2016.zip']
}

def read_water_data(setname = "playset", datadir='data/'):
    """
    Reads a specified (sub)-set or the full filelist
    @setname: one of 'fullset', 'sane commitment', 'sane disbursement','sane','playset'
    @datadir: the basedir where the files can be found

    @return: returns a pandas DataFrame with the data
    """
    df = DataFrame()
    filelist = datasets[setname]
    
    for i in filelist:
        print("reading: %s/%s" %(datadir,i))
        df = df.append(read_csv(datadir+i,sep="|",
                                header=0,quotechar='"',
                                encoding="iso8859_15",
                                compression="zip",low_memory=False,
                                dtype={
                                    'DonorCode': np.unicode_,
                                    'AgencyCode': np.unicode_,
                                    'RecipientCode': np.unicode_,
                                    'RegionCode': np.unicode_,
                                    'IncomegroupCode': np.unicode_,
                                    'FlowCode': np.unicode_,
                                    'Bi_Multi': np.unicode_,
                                    'Category': np.unicode_,
                                    'Finance_t': np.unicode_,
                                    'CrsID': np.unicode_,
                                    'Aid_t': np.unicode_,
                                    'ProjectNumber': np.unicode_,
                                    'CurrencyCode': np.unicode_,
                                    'PurposeCode': np.unicode_,
                                    'SectorCode': np.unicode_,
                                    'ChannelCode': np.unicode_,
                                    'ParentChannelCode': np.unicode_,
                                    'BudgetIdent': np.unicode_,
                                    'Gender': np.unicode_,
                                    'Environment': np.unicode_,
                                    'PDGG': np.unicode_,
                                    'Trade': np.unicode_,
                                    'RMNCH': np.unicode_
                                },
                                parse_dates=["CommitmentDate",'ExpectedStartDate','Year',
                                             'CompletionDate','Repaydate1','Repaydate2']))
    return df
        
def generate_histograms_about_projectsize(idf,startyear = None, stopyear = None,
                                          targetdir = "results/dataoverview/",
                                          basefilename = "projects_commitsizes.png",
                                          filterzerocommitment = True,
                                          bins = 50, subplotwidth = 7, ncols = 3,
                                          windowsize = [("-inf",0.0),(0.0,"inf"),(0.0,8.0),(0.0,3.0),
                                                        (0.0,1.0),(0.0,0.2),("-inf",-0.2),(1.0,60.0),
                                                        (60.0,"inf"),(200.0,"inf"),(500.0,"inf")]
                                          ):
    """
    generates some histograms and jsondata about the general data. The results are stored in the targetdir. the start and stop year is 
    appended to the dirpath, if provided. 
    Data without or with 0.0 as value for USD_Commitment_Defl are filtered out per default

    @param idf (DataFrame): the inputDataFrame that shall be used as base for the images and json-files
    @param startyear (int): select a specific year as start. for example 2011 to get graphs beginning at 1-1-2011 upto the end of the data
    @param stopyear: select a specific year to end. for example 2018 to get graphs including data upto 31-12-2018 
    @param targetdir: where to store the results. will be created if needed
    @param filterzerocommitment: about 50% of the raw-data have not amount for the attribute 'USD_Commitment_Defl' per default those datapoints will be ignored
    @param windowsize: different projectsizes the graphs should show - an array of tupels. first value of the tupel defines the lower bound (value must be greater to be shown)
                       second value defines the upper bound (value must be smaller then this to be shown)
    @param bins: how many buckets shall be created
    @param subplitwidth: width and height of a singe subplot
    @param ncols: number of subplots per row in the graph
    @param basefilename: the filename and format (based on extension) of the resulting image
    """

    nrows = int(len(windowsize) / ncols) + 1
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols,figsize=( ncols * subplotwidth, nrows * subplotwidth ))

    rdf = idf.copy()

    # filter on Commitmentdate
    
    if startyear:
        rdf = rdf[rdf['CommitmentDate'] > datetime(year=startyear-1,month=12,day=31)]
        targetdir = targetdir + "from_" + str(startyear) + "_"
    if stopyear:
        rdf = rdf[rdf['CommitmentDate'] < datetime(year=stopyear+1,month=1,day=1)]
        targetdir = targetdir + "upto_" + str(stopyear) 
    if startyear or stopyear:
        targetdir = targetdir + "/"

    if filterzerocommitment:
        rdf = rdf[rdf['USD_Commitment_Defl'] != 0.0]
        
    os.makedirs(targetdir,exist_ok=True)
    
    # generate subplots for each defined window
    for (i,win) in enumerate(windowsize):
        print("filtering for and creating: %s for subplot: %.2f < x < %.2f" %(targetdir + basefilename,np.float64(win[0]),np.float64(win[1])))
        df = rdf.copy()
            
        df = df[df['USD_Commitment_Defl'] > np.float64(win[0])]
        df = df[df['USD_Commitment_Defl'] < np.float64(win[1])]
            
        projectcount = df['USD_Commitment_Defl'].count()
        commitsum = df['USD_Commitment_Defl'].sum()

        df['USD_Commitment_Defl'].plot(kind='hist',grid=True,ax=axes[int(i/ncols)][i % ncols],bins=bins,
                                      title=" %.2f < x < %.2f \n %d projects with total of %.2f mUSD" % (np.float64(win[0]),np.float64(win[1]),projectcount,commitsum))
        # create a json_file with the plotdata - XXX don't calculate the bins twice

        if df['USD_Commitment_Defl'].count() > 0:
            dfh=pd.cut(df['USD_Commitment_Defl'],bins=bins).value_counts()
            with open("%s%s-%.2f-%.2f.json" %(targetdir,basefilename,np.float64(win[0]),np.float64(win[1])),"w") as fd:
                fd.write(dfh.to_json())

        else:
            print("Warning no Data for: %s%s-%.2f-%.2f.json" %(targetdir,basefilename,np.float64(win[0]),np.float64(win[1])))

    plt.savefig(targetdir+basefilename)
    plt.close(plt.gcf())

def filter_donor_sector_flow_recipient(idf,donorcodes=['5'],sectorcodes=['140'],flowcodes=['11','13'],
                                       recipientcodes=["285","248","282","238","278","266",
                                                       "228","645","666","555","142","437","428"]):
    """
    Filters a given DataFrame for donors, sectors, flows and/or recipients. Only the provided will be taken into account.
    Since this dataanlyse is for specific project the defaults are choosen for germany, water, ODA Grands and ODA Loans. the default recipients are:
    '285': "Uganda",
    '248': "Kenia",
    '282': "Tansania",
    '238': "Äthiopien",
    '278': "Sudan",
    '279': "Südsudan",
    '266': "Ruanda",
    '228': "Burundi",
    '645': "Indien",
    '666': "Bangladesch",
    '555': "Libanon",
    '142': "Ägypten",
    '437': "Kolumbien",
    '428': "Bolivien"

    @param donorcodes: an array of donor country codes (labels/text) used by the oecd to identify a country. Use None or array of size 0 to skip this filter
    @param sectorcodes: an array of sector codes (label/text) used by the oecd to identify a secort. Use None or array of size 0 to skip this filter
    @param flowcodes: an array of flow codes (label/text) used by the oecd to mark specific types of helps. Use None or array of size 0 to skip this filter
    @param recipientcodes: an array of recipient codes (label/text) used by the oecd to identify a recipient country

    @return: returns a new DataFrame with applied filters
    """

    df = idf.copy()
    if type(donorcodes) == type([]) and len(donorcodes) > 0:
        df = df[df['DonorCode'].isin(donorcodes)]
        
    if type(sectorcodes) == type([]) and len(sectorcodes) > 0:
        df = df[df['SectorCode'].isin(sectorcodes)]
        
    if type(flowcodes) == type([]) and len(sectorcodes) > 0:
        df = df[df['FlowCode'].isin(flowcodes)]

    if type(recipientcodes) == type([]) and len(recipientcodes)> 0:
        df = df[df['RecipientCode'].isin(recipientcodes)]
        
    return df
    

if __name__ == "__main__":
    # read the data respecting what is defined as "sane" set from the oecd
    df = read_water_data(setname="sane commitment")
    # generate histogram over the full dataset
    generate_histograms_about_projectsize(df)
    # histogram for the years 2010-
    generate_histograms_about_projectsize(df,startyear=2010)
    # histogram for the years 2015-2017
    generate_histograms_about_projectsize(df,startyear=2015,stopyear=2017)
    # and a histogram for every year
    for i in range(2010,2020):
        generate_histograms_about_projectsize(df,startyear=i,stopyear=i)

    df = filter_donor_sector_flow_recipient(df)
    # generate histogram over the full dataset
    generate_histograms_about_projectsize(df,basefilename="projectsizes_germany_water_selected_countries.png")
    generate_histograms_about_projectsize(df,basefilename="projectsizes_germany_water_selected_countries.png",startyear=2015)
    
