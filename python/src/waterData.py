#!/usr/bin/env python

from pandas import DataFrame, read_csv, Grouper
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import numpy as np
import os
from datetime import datetime
import json
import csv
import pickle
import plotly.express as px

from worldbankApi import fetch_series, default_series
from tools import extract_features, read_water_data, merge_wbseries_with_oecd_data, get_oecd_iso3_code_mapping

default_features=['DonorName','RecipientName','DonorCode','RecipientCode','IncomegroupName',
                  'USD_Commitment_Defl','USD_Received_Defl','ShortDescription','AgencyName',
                  'FlowCode','SectorCode', 'ProjectTitle','PurposeName','SectorName',
                  'ChannelName','ChannelReportedName', 'ExpectedStartDate','CompletionDate',
                  'LongDescription','CommitmentDate','USD_GrantEquiv','USD_Disbursement_Defl']


        
def generate_sunburst_for_grouping(idf,startyear = None, stopyear = datetime.now().year,
                                   targetdir = "results/dataoverview/",
                                   basefilename = "projects_grouping",
                                   incomegroups=['LDCs','LMICs','UMICs'],
                                   valuename='USD_Commitment_Defl',
                                   filterzerocommitment = True):
    """
    create graph that group data into 
    * Incomegroup + Sector
    * Incomegroup + Sector + Purpose
    * RecipientCountry + Sector 
    * RecipientCountry + Sector + Purpose

    @param idf (DataFrame): the inputDataFrame that shall be used as base for the images and json-files
    @param startyear (int): select a specific year as start. for example 2011 to get graphs beginning at 1-1-2011 upto the end of the data
    @param stopyear: select a specific year to end. for example 2018 to get graphs including data upto 31-12-2018 
    @param targetdir: where to store the results. will be created if needed
    @param filterzerocommitment: about 50% of the raw-data have not amount for the attribute 'USD_Commitment_Defl' per default those datapoints will be ignored
    @param valuename: the name of the feature/column to use. defaults to 'USD_Commitment_Defl'
    @param basefilename: the filename and format (based on extension) of the resulting image
    @incomegroups: only consider the listed incomegroups. expects an array of IncomegroupNames. There are: LDCs,LMICs,MADCTs,Other LICs,Part I unallocated by income, UMICs. project specific per default only LDCs, LMICs and UMICs are taken into account. with None or empty array every group is considered

    """

    all_incomegroups = ["LDCs","LMICs","MADCTs","Other LICs","Part I unallocated by income", "UMICs"]
    df = DataFrame()

    # filter for needed features
    for i in ['CommitmentDate','IncomegroupName',valuename,'SectorName','PurposeName','RecipientName','AgencyName']:
        df[i] = idf[i]

    if startyear:
        df = df[df['CommitmentDate'] > datetime(year=startyear-1,month=12,day=31)]
        targetdir = targetdir + "from_" + str(startyear) + "_"
    if stopyear:
        df = df[df['CommitmentDate'] < datetime(year=stopyear+1,month=1,day=1)]
        targetdir = targetdir + "upto_" + str(stopyear) 
    if startyear or stopyear:
        targetdir = targetdir + "/"

    df = df.drop(columns=['CommitmentDate'])
        
    os.makedirs(targetdir,exist_ok=True)

    if filterzerocommitment:
        df = df[df[valuename].notnull()]
        df = df[df[valuename] != 0.0]

    if type(incomegroups) == type([]) and len(incomegroups) > 0:
        df = df[df['IncomegroupName'].isin(incomegroups)]

    
    for i in [['IncomegroupName','SectorName'],
              ['IncomegroupName','PurposeName'],
              ['IncomegroupName','SectorName','PurposeName'],
              ['RecipientName','SectorName'],
              ['RecipientName','PurposeName'],
              ['RecipientName','SectorName','PurposeName'],
              ['AgencyName','RecipientName'],
              ['AgencyName','PurposeName'],
              ['AgencyName','IncomegroupName'],
              ['AgencyName','SectorName']]:

        dfg = df.groupby(i).sum().reset_index()
        with open("%s%s-%s.json" %(targetdir,basefilename,"-".join(i)),"w") as fd:
                fd.write(dfg.to_json(orient="index"))

        fig = px.sunburst(dfg, path=i, values=valuename)
        fig.write_image("%s%s-%s.png" %(targetdir,basefilename,"-".join(i)),scale=3)


    
def generate_histograms_about_projectsize(idf,startyear = None, stopyear = datetime.now().year,
                                          targetdir = "results/dataoverview/",
                                          basefilename = "projects_commitsizes.png",
                                          filterzerocommitment = True,
                                          valuename="USD_Commitment_Defl",
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
    @param valuename: Defaults to USD_Commitment_Defl
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
        rdf = rdf[rdf[valuename].notnull()]
        rdf = rdf[rdf[valuename] != 0.0]
        
    os.makedirs(targetdir,exist_ok=True)
    
    # generate subplots for each defined window
    for (i,win) in enumerate(windowsize):
        print("filtering for and creating: %s for subplot: %.2f < x < %.2f" %(targetdir + basefilename,np.float64(win[0]),np.float64(win[1])))
        df = rdf.copy()
            
        df = df[df[valuename] > np.float64(win[0])]
        df = df[df[valuename] < np.float64(win[1])]
            
        projectcount = df[valuename].count()
        commitsum = df[valuename].sum()

        df[valuename].plot(kind='hist',grid=True,ax=axes[int(i/ncols)][i % ncols],bins=bins,
                                      title=" %.2f < x < %.2f \n %d projects with total of %.2f mUSD" % (np.float64(win[0]),np.float64(win[1]),projectcount,commitsum))
        # create a json_file with the plotdata - XXX don't calculate the bins twice

        if df[valuename].count() > 0:
            dfh=pd.cut(df[valuename],bins=bins).value_counts()
            with open("%s%s-%.2f-%.2f.json" %(targetdir,basefilename,np.float64(win[0]),np.float64(win[1])),"w") as fd:
                fd.write(dfh.to_json(orient="index"))

        else:
            print("Warning no Data for: %s%s-%.2f-%.2f.json" %(targetdir,basefilename,np.float64(win[0]),np.float64(win[1])))

    plt.savefig(targetdir+basefilename,bbox_inches='tight')
    plt.close(plt.gcf())

def generate_barchart_for_incomegroup_distribution(idf,startyear = None, stopyear = datetime.now().year,
                                                   targetdir = "results/dataoverview/",
                                                   basefilename = "incomegroups.png",
                                                   filterzerocommitment = True,
                                                   valuename="USD_Commitment_Defl",
                                                   incomegroups=['LDCs','LMICs','UMICs'],
                                                   figsize=(30,56)):
    """
    generates six barchart-graphics showing the distribution of commitments and projectnumer among the different incomegroups (LDCs,LICs...) over time. also creates the json-files of the aggregated data.

    @param idf (DataFrame): the inputDataFrame that shall be used as base for the images and json-files
    @param startyear (int): select a specific year as start. for example 2011 to get graphs beginning at 1-1-2011 upto the end of the data
    @param stopyear: select a specific year to end. for example 2018 to get graphs including data upto 31-12-2018 
    @param targetdir: where to store the results. will be created if needed
    @param filterzerocommitment: about 50% of the raw-data have not amount for the attribute 'USD_Commitment_Defl' per default those datapoints will be ignored
    @param valuename: defaults to USD_Commitment_Defl
    @param basefilename: the filename and format (based on extension) of the resulting image
    @incomegroups: only consider the listed incomegroups. expects an array of IncomegroupNames. There are: LDCs,LMICs,MADCTs,Other LICs,Part I unallocated by income, UMICs. project specific per default only LDCs, LMICs and UMICs are taken into account. with None or empty array every group is considered

    """

    all_incomegroups = ["LDCs","LMICs","MADCTs","Other LICs","Part I unallocated by income", "UMICs"]

      
    nrows = 8
    
    fig, axes = plt.subplots(nrows=nrows, ncols=1,figsize=figsize)

    df = DataFrame()
    for i in ['CommitmentDate','IncomegroupName',valuename]:
        df[i] = idf[i]

    if startyear:
        df = df[df['CommitmentDate'] > datetime(year=startyear-1,month=12,day=31)]
        targetdir = targetdir + "from_" + str(startyear) + "_"
    if stopyear:
        df = df[df['CommitmentDate'] < datetime(year=stopyear+1,month=1,day=1)]
        targetdir = targetdir + "upto_" + str(stopyear) 
    if startyear or stopyear:
        targetdir = targetdir + "/"
    
    os.makedirs(targetdir,exist_ok=True)

    if filterzerocommitment:
        df = df[df[valuename].notnull()]
        df = df[df[valuename] != 0.0]

    if type(incomegroups) == type([]) and len(incomegroups) > 0:
        df = df[df['IncomegroupName'].isin(incomegroups)]

    # group by year and IncomegroupName
    df = df.set_index("CommitmentDate")

    groupeddf = df.groupby([Grouper(freq="A"), 'IncomegroupName'])[valuename]

    # resolve grouping, unstack, fill missing and reset_index()
    ddf = groupeddf.sum().unstack().fillna(0.0).reset_index()
    # get a percent view in a new DataFrame
    df2 = DataFrame()
    for i in all_incomegroups:
        try:
            df2[i]=ddf[i]
        except Exception as e:
            pass
    df2['CommitmentYear'] = ddf.reset_index()['CommitmentDate'].apply(lambda x: str(x.year))
    
    df2=df2.set_index('CommitmentYear')
    
    countrytypesum = DataFrame(df2.T.sum())
    for i in all_incomegroups:
        try:
            df2[i] = (df2[i] / countrytypesum[0]) * 100
        except Exception as e:
            pass
    df2.replace([np.inf, -np.inf], np.nan, inplace=True) 

    df2.plot(width=0.9,grid=True,kind='bar', ax=axes[1],title="mUSD per IncomeGroup (Prozent)")
    df2.plot(width=0.9,grid=True,kind='bar', stacked=True, ax=axes[2],title="mUSD per IncomeGroup (Prozent)")

    with open("%s%s-sum-percent.json" %(targetdir,basefilename),"w") as fd:
        fd.write(df2.to_json(orient="index"))

    # an absolut view
    # create index on year as string and drop old index
    ddf["CommitmentYear"]=ddf["CommitmentDate"].apply(lambda x: str(x.year))
    ddf = ddf.drop(columns=["CommitmentDate"]).set_index("CommitmentYear")

    # plot absolut sum
    ddf.plot(width=0.9,grid=True,kind='bar',ax=axes[0], title="mUSD per IncomeGroup (sum)")

    with open("%s%s-sum-absolut.json" %(targetdir,basefilename),"w") as fd:
        fd.write(ddf.to_json(orient="index"))

    # create bar-char with mean
    ddf = groupeddf.mean().unstack().fillna(0.0).reset_index()
    
    # create index on year as string and drop old index
    ddf["CommitmentYear"]=ddf["CommitmentDate"].apply(lambda x: str(x.year))
    ddf = ddf.drop(columns=["CommitmentDate"]).set_index("CommitmentYear")

    ddf.plot(width=0.9,grid=True,kind='bar',ax=axes[3], title="mUSD per IncomeGroup (mean)")
    with open("%s%s-mean.json" %(targetdir,basefilename),"w") as fd:
        fd.write(ddf.to_json(orient="index"))


    # create bar-char with median
    ddf = groupeddf.median().unstack().fillna(0.0).reset_index()
    
    # create index on year as string and drop old index
    ddf["CommitmentYear"]=ddf["CommitmentDate"].apply(lambda x: str(x.year))
    ddf = ddf.drop(columns=["CommitmentDate"]).set_index("CommitmentYear")

    ddf.plot(width=0.9,grid=True,kind='bar',ax=axes[4], title="mUSD per IncomeGroup (median)")
    with open("%s%s-median.json" %(targetdir,basefilename),"w") as fd:
        fd.write(ddf.to_json(orient="index"))
    
    ddf = groupeddf.count().unstack().fillna(0.0).reset_index()

    # get a percent view in a new DataFrame
    df2 = DataFrame()
    for i in all_incomegroups:
        try:
            df2[i]=ddf[i]
        except Exception as e:
            pass
    df2['CommitmentYear'] = ddf.reset_index()['CommitmentDate'].apply(lambda x: str(x.year))
    
    df2=df2.set_index('CommitmentYear')
    
    countrytypesum = DataFrame(df2.T.sum())
    for i in all_incomegroups:
        try:
            df2[i] = (df2[i] / countrytypesum[0]) * 100
        except Exception as e:
            pass
    df2.replace([np.inf, -np.inf], np.nan, inplace=True) 

    df2.plot(width=0.9,grid=True,kind='bar', ax=axes[6],title="projects per IncomeGroup (Prozent)")
    df2.plot(width=0.9,grid=True,kind='bar', stacked=True,ax=axes[7],title="projects per IncomeGroup (Prozent)")
    with open("%s%s-count-percent.json" %(targetdir,basefilename),"w") as fd:
        fd.write(df2.to_json(orient="index"))

    
    # create index on year as string and drop old index
    ddf["CommitmentYear"]=ddf["CommitmentDate"].apply(lambda x: str(x.year))
    ddf = ddf.drop(columns=["CommitmentDate"]).set_index("CommitmentYear")
    
    ddf.plot(width=0.9,grid=True,kind='bar',ax=axes[5], title="projects per IncomeGroup (count)")
    with open("%s%s-count-absolut.json" %(targetdir,basefilename),"w") as fd:
        fd.write(ddf.to_json(orient="index"))



        
    
    plt.savefig(targetdir+basefilename,bbox_inches='tight')
    plt.close(plt.gcf())

    
    
def filter_donor_sector_flow_recipient(idf,donorcodes=['5'],sectorcodes=['140'],flowcodes=['11','13'],
                                       recipientcodes=["285","248","282","238","278","266",
                                                       "228","645","666","555","142","437","428"],
                                       valuename="USD_Commitment_Defl",
                                       filterzerocommitment=True):
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
    @param valuename: defaults to USD_Commitment_Defl
    @param filterzerocommitment: filter out commitments with a value of zero
    @return: returns a new DataFrame with applied filters
    """

    df = idf.copy()
    if filterzerocommitment:
        df = df[df[valuename].notnull()]
        df = df[df[valuename] != 0.0]

    if type(donorcodes) == type([]) and len(donorcodes) > 0:
        df = df[df['DonorCode'].isin(donorcodes)]
        
    if type(sectorcodes) == type([]) and len(sectorcodes) > 0:
        df = df[df['SectorCode'].isin(sectorcodes)]
        
    if type(flowcodes) == type([]) and len(flowcodes) > 0:
        df = df[df['FlowCode'].isin(flowcodes)]

    if type(recipientcodes) == type([]) and len(recipientcodes)> 0:
        df = df[df['RecipientCode'].isin(recipientcodes)]
        
    return df

def save_micro_data(idf, targetdir = "results/microdata/",basefilename = 'microdata',features=None):
    """
    stores a csv and a jsonfile with the selected features of a dataframe

    @param idf: the dataframe to extract the features/columns from
    @param targetdir: the directory to store data in. it is created if it is missing
    @param basefilename: the first part of the filename to use for the csv/json-files
    @param features: which features to store (array of strings). If None, all features are stored
    """

    os.makedirs(targetdir,exist_ok=True)
    if type(features) == type([]) and len(features)>0:
        df = extract_features(idf,features=features)

        df.to_csv(path_or_buf="%s/%s.csv" %(targetdir,basefilename),
                   sep = ";", columns=features, quoting=csv.QUOTE_NONNUMERIC)
        df.reset_index().to_json(path_or_buf="%s/%s.json" %(targetdir,basefilename),
                                 orient="index")
    else:
        idf.to_csv(path_or_buf="%s/%s.csv" %(targetdir,basefilename),
                   sep = ";", quoting=csv.QUOTE_NONNUMERIC)
        idf.reset_index().to_json(path_or_buf="%s/%s.json" %(targetdir,basefilename),
                                  orient="index")
        
            

if __name__ == "__main__":
    devel = False

    # generate histogram over the full dataset
    for valuename in ['USD_Commitment_Defl','USD_Disbursement_Defl']:

        if not devel:
            df = None
            # read the data respecting what is defined as "sane" set from the oecd
            # if a pickle file is present, load that instead

            # fetch data from worldbank
            wbdf = fetch_series()

            # read the full set of oecd-data
            oecddf = read_water_data(setname="fullset")

            codemapping = get_oecd_iso3_code_mapping()
            
            # reduce to wanted features
            idf = extract_features(oecddf,features = default_features).reset_index()

            # merge worldbankdata on year and country - commitments for regions and by 'foundations' or
            # other international constructs are filtered 
            df = merge_wbseries_with_oecd_data(idf,wbdf,codemapping=codemapping)

            # generate histogram over the full dataset
            generate_histograms_about_projectsize(df,valuename=valuename,targetdir="results/" + valuename + "/dataoverview/")
            # histogram for the years 2010-
        
            #generate_histograms_about_projectsize(df,startyear=2010,valuename=valuename)
            # histogram for the years 2015-2017
            #generate_histograms_about_projectsize(df,startyear=2015,stopyear=2017,valuename=valuename)
            # and a histogram for every year
            #for i in range(2010,2020):
            #    generate_histograms_about_projectsize(df,startyear=i,stopyear=i,valuename=valuename)

            generate_barchart_for_incomegroup_distribution(df,startyear=1980,valuename=valuename,targetdir="results/" + valuename + "/dataoverview/")
            generate_sunburst_for_grouping(df,startyear=1980,valuename=valuename,targetdir="results/" + valuename + "/dataoverview/")

            # focus on all german projects
            df_focus = filter_donor_sector_flow_recipient(df,sectorcodes=None,recipientcodes=None,valuename=valuename)
            generate_barchart_for_incomegroup_distribution(df_focus,startyear=1980,targetdir="results/" + valuename + "/germany/",valuename=valuename)
            generate_sunburst_for_grouping(df_focus,basefilename="germany_projects_grouping",startyear=1980,targetdir="results/" + valuename + "/germany/",valuename=valuename)
            
            
            # save microdata for all recipients, but filtered otherwise
            df = filter_donor_sector_flow_recipient(df,recipientcodes=None,valuename=valuename)
            features = default_features
            for i in default_series:
                features.append("Recipientstat "+i)
            save_micro_data(df,features=features,targetdir="results/" + valuename + "/microdata/")
            generate_barchart_for_incomegroup_distribution(df,basefilename="water_incomegroups.png",startyear=1980,targetdir="results/" + valuename + "/germany-water/",valuename=valuename)
            generate_sunburst_for_grouping(df,basefilename="water_projects_grouping",startyear=1980,targetdir="results/" + valuename + "/germany-water/",valuename=valuename)
            
            df = filter_donor_sector_flow_recipient(df,valuename=valuename)
            generate_histograms_about_projectsize(df,basefilename="projectsizes_germany_water_selected_countries.png",targetdir="results/" + valuename + "/germany-water/",valuename=valuename)
            generate_histograms_about_projectsize(df,basefilename="projectsizes_germany_water_selected_countries.png",startyear=2015,targetdir="results/" + valuename + "/germany-water/",valuename=valuename)
            save_micro_data(df,basefilename="microdata_selectedrecipients",features=features,targetdir="results/" + valuename + "/microdata/")

        else:
            df = read_water_data(setname="playset")
            
            generate_sunburst_for_grouping(df,startyear=1980,valuename=valuename,targetdir="results/" + valuename + "/dataoverview/")

            df_focus = filter_donor_sector_flow_recipient(df,valuename=valuename)
            generate_sunburst_for_grouping(df_focus,basefilename="water_projects_grouping",startyear=1980,valuename=valuename,targetdir="results/" + valuename + "/dataoverview/")

            # germany in general
            df_focus = filter_donor_sector_flow_recipient(df,sectorcodes=None,recipientcodes=None,valuename=valuename)
            generate_sunburst_for_grouping(df_focus,basefilename="germany_projects_grouping",startyear=1980,valuename=valuename,targetdir="results/" + valuename + "/dataoverview/")

