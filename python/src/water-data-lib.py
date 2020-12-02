#!/usr/bin/env python

from pandas import DataFrame, read_csv
import matplotlib.pyplot as plt
import numpy as np

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
    """

    nrows = int(len(windowsize) / ncols) + 1
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols,figsize=( ncols * subplotwidth, nrows * subplotwidth ))

    for (i,win) in enumerate(windowsize):
        df = idf.copy()
        if filterzerocommitment:
            df = df[df['USD_Commitment_Defl'] != 0.0]
            
        df = df[df['USD_Commitment_Defl'] > np.float64(win[0])]
        df = df[df['USD_Commitment_Defl'] < np.float64(win[1])]
            
        projectcount = df['USD_Commitment_Defl'].count()
        commitsum = df['USD_Commitment_Defl'].sum()

        print("drawing at %d - %d" %(i % ncols,int(i/ncols)))
        print(df.describe())
        
        df['USD_Commitment_Defl'].plot(kind='hist',grid=True,ax=axes[int(i/ncols)][i % ncols],bins=bins,
                                      title=" %.2f < x > %.2f \n %d projects with total of %.2f mUSD" % (np.float64(win[0]),np.float64(win[1]),projectcount,commitsum))
        

    plt.savefig(targetdir+"projects_commitsizes.png")
    plt.close(plt.gcf())


if __name__ == "__main__":
    df = read_water_data()
    generate_histograms_about_projectsize(df)
