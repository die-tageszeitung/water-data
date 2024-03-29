#!/usr/bin/env python3

import pandas as pd
import numpy as np
from worldbankApi import get_regionnames
import pickle
import os


# worldbank and creditor reporting system use different names for the countries
worldbank_to_crs_countynames = {
    "Yemen, Rep.": "Yemen",
    "Vietnam": "Viet Nam",
    "Venezuela, RB": "Venezuela",
    "St. Vincent and the Grenadines": "Saint Vincent and the Grenadines",
    "Russian Federation": "Russia",
    "West Bank and Gaza": "West Bank and Gaza Strip",
    "Korea, Dem. People’s Rep.": "Democratic People's Republic of Korea",
    "Macao SAR, China": "Macau (China)",
    "St. Lucia": "Saint Lucia",
    "Lao PDR": "Lao People's Democratic Republic",
    "Korea, Rep.": "Korea",
    "St. Kitts and Nevis": "Saint Kitts and Nevis",
    "Kyrgyz Republic": "Kyrgyzstan",
    "Iran, Islamic Rep.": "Iran",
    "Hong Kong SAR, China": "Hong Kong (China)",
    "Gambia, The": "Gambia",
    "Micronesia, Fed. Sts.": "Micronesia",
    "Egypt, Arab Rep.": "Egypt",
    "Congo, Rep.": "Congo",
    "Congo, Dem. Rep.": "Democratic Republic of the Congo",
    "Cote d'Ivoire": "Côte d'Ivoire",
    "China": "China (People's Republic of)",
    "Bahamas, The": "Bahamas"
    }

no_mapping_for_crs_countries = ['Montserrat','Cook Islands','Niue','Tokelau','Saint Lucia','Anguilla','Netherlands Antilles','Saint Helena','Mayotte','Chinese Taipei','Wallis and Futuna']
no_mapping_for_worldbank_countries = ['Virgin Islands (U.S.)','Taiwan, China','Sint Maarten (Dutch part)','San Marino','Puerto Rico','St. Martin (French part)','Monaco','Isle of Man','Guam','Greenland','Faroe Islands','Curacao','American Samoa','Andorra','Channel Islands']

crs_to_worldbank_countrynames = {v: k for k, v in worldbank_to_crs_countynames.items()}

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
    #"playset": ['crs2019.zip']
}

def read_water_data(setname = "playset", datadir='data/', datasets=datasets,cachedir="data/cache"):
    """
    Reads a specified (sub)-set or the full filelist
    @setname: one of 'fullset', 'sane commitment', 'sane disbursement','sane','playset'
    @datadir: the basedir where the files can be found
    @datasets: a dict with datasets containing lists of zip-filenames to read from the datadir

    @return: returns a pandas DataFrame with the data
    """
    df = pd.DataFrame()

    cached_df_filename = "%s/%s.p" %(cachedir,setname)
    try:
        with open(cached_df_filename, 'rb') as fd:
            print("Reading Datafrom cached file: %s" %(cached_df_filename))
            df = pickle.load(fd)
    except:
    
        filelist = datasets[setname]
    
        for i in filelist:
            print("reading: %s/%s" %(datadir,i))
            df = df.append(pd.read_csv(datadir+i,sep="|",
                                       header=0,quotechar='"',
                                       encoding="iso8859_15",
                                       compression="zip",low_memory=False,
                                       dtype={
                                           'DonorCode': np.unicode_,
                                           'InitialReport': np.unicode_,
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
                                           'SDGfocus': np.unicode_,
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
        print("Writing cached_df_file: %s" %(cached_df_filename))
        os.makedirs(cachedir,exist_ok=True)    

        with open(cached_df_filename, 'wb') as fd:
            pickle.dump(df, fd)

    return df

def get_oecd_iso3_code_mapping(cachedir="data/cache", datadir="data/"):
    """
    returns a mapping of oecd-country-codes to iso3-Countrycodes. Since the mapping does not overlap,
    one dict with bothmappings is returned

    @param cachedir: stores the result in a cache-file 
    @param datadir: where to finde the oecd-data
    """

    cached_filename = "%s/oecdiso3.p" %(cachedir)
    crs_wb_country_idmap = {}
    try:
        with open(cached_filename, 'rb') as fd:
            print("Reading countrycode-mapping cached file: %s" %(cached_filename))
            crs_wb_country_idmap = pickle.load(fd)
    except:
        df = read_water_data(datadir=datadir,setname="fullset",cachedir=cachedir)
        wb_regions = get_regionnames(cachedir=cachedir)
        
        recipients = df[['RecipientCode','RecipientName']].groupby(["RecipientCode","RecipientName"]).count().reset_index()
        recipients.rename(columns={"RecipientCode": "Code", "RecipientName": "Name"}, inplace=True)

        donors = df[['DonorCode','DonorName']].groupby(["DonorCode","DonorName"]).count().reset_index()
        donors.rename(columns={"DonorCode": "Code", "DonorName": "Name"},inplace=True)

        codenamemap = donors.append(recipients)

        codenamemap.replace(inplace=True,to_replace=crs_to_worldbank_countrynames)
        dfmap = codenamemap.merge(wb_regions,how='outer',left_on='Name',right_on="name")


        for row in dfmap[['Code','Name','name','id','region']].iterrows():
            row = row[1]
            if row['id'] and row['id'] is not np.nan and row['Code'] and row['Code'] is not np.nan :
                crs_wb_country_idmap[row['Code']] = row['id']
                crs_wb_country_idmap[row['id']] = row['Code']
        print("Writing cached_file: %s" %(cached_filename))
        with open(cached_filename, 'wb') as fd:
            pickle.dump(crs_wb_country_idmap, fd)

    finally:
        # adding some values that are (maybe) missing in the datasets
        #AIA Anguilla 
        crs_wb_country_idmap['376'] = 'AIA' 
        crs_wb_country_idmap['AIA'] = '376'
        # COK Cook Islands 
        crs_wb_country_idmap['831'] = 'COK'
        crs_wb_country_idmap['COK'] = '831'
        # FLK Falkland Islands (Malvinas) 
        crs_wb_country_idmap['443'] = 'FLK'
        crs_wb_country_idmap['FLK'] = '443'
        # MYT Mayotte
        crs_wb_country_idmap['258'] = 'MYT'
        crs_wb_country_idmap['MYT'] = '258'
        # MSR Montserrat 
        crs_wb_country_idmap['385'] = 'MSR'
        crs_wb_country_idmap['MSR'] = '385'
        # ANT Netherlands Antilles 
        crs_wb_country_idmap['361'] = 'ANT'
        crs_wb_country_idmap['ANT'] = '361'
        # NIU Niue 
        crs_wb_country_idmap['856'] = 'NIU'
        crs_wb_country_idmap['NIU'] = '856'
        # SHN Saint Helena, Ascension and Tristan da Cunha 
        crs_wb_country_idmap['276'] = 'SHN'
        crs_wb_country_idmap['SHN'] = '276'
        # TKL Tokelau 
        crs_wb_country_idmap['868'] = 'TKL'
        crs_wb_country_idmap['TKL'] = '868'
        # WLF Wallis and Futuna 
        crs_wb_country_idmap['876'] = 'WLF'
        crs_wb_country_idmap['WLF'] = '876'
        # MKD Macedonia, the former Yugoslav Republic of 
        crs_wb_country_idmap['88'] = 'MKD'
        crs_wb_country_idmap['MKD'] = '88'
        # SVK Slovakia
        crs_wb_country_idmap['69'] = 'SVK'
        crs_wb_country_idmap['SVK'] = '69'
        # SWZ Swaziland  / Eswatini
        crs_wb_country_idmap['280'] = 'SWZ'
        crs_wb_country_idmap['SWZ'] = '280'
        # HUN Hungary 
        crs_wb_country_idmap['75'] = 'HUN'
        crs_wb_country_idmap['HUN'] = '75'
        # EST Estonia
        crs_wb_country_idmap['82'] = 'EST'
        crs_wb_country_idmap['EST'] = '82'
        # CZE Czech Republic
        crs_wb_country_idmap['68'] = 'CZE'
        crs_wb_country_idmap['CZE'] = '68'
        # BGR Bulgaria 
        crs_wb_country_idmap['72'] = 'BGR'
        crs_wb_country_idmap['BGR'] = '72'
        # LVA Latvia 
        crs_wb_country_idmap['83'] = 'LVA'
        crs_wb_country_idmap['LVA'] = '83'
        # LTU Lithuania
        crs_wb_country_idmap['84'] = 'LTU'
        crs_wb_country_idmap['LTU'] = '84'

        ####### no ISO3Codes for regions
        # Africa, America, Asia, Bilateral, Caribbean & Central America, Caribbean,
        # Central America, Central Asia, East African Community, Eastern Africa, Europe,
        # Far East Asia, Melanesia, Middle Africa, Middle East, North of Sahara, Oceania,
        # South & Central Asia, South America, South Asia, South of Sahara, Southern Africa,
        # Western Africa
        
        #for i in ['298','498','798','9998','389','1031','1032','619','237','1027','89','789',
        #          '1033','1028','589','189','889','689','489','679','289','1029','1030']:
        #    crs_wb_country_idmap[i]=""

        # Chinese Taipei - no iso3code
        #crs_wb_country_idmap['732'] = ""

        # generic catch
        #crs_wb_country_idmap[''] = ''
        #crs_wb_country_idmap[np.nan] = ''
        
        
        return crs_wb_country_idmap


def extract_features(idf,features):
    
    """
    @param idf: the dataframe to extract the features/columns from
    @param features: an array containing the featurenames to extract

    """
    df = pd.DataFrame()
    if type(features) == type([]) and len(features) > 0:
        for i in features:
            if i in idf:
                df[i] = idf[i]
    else:
        df = idf.copy()
            

    return df

def apply_historical_incomegroups_wb(ioecddf,oecd_iso3,
                                     datadir="data/",datafilename="OGHIST.csv",
                                     datefeature="CommitmentDate",
                                     oecdidfeature="RecipientCode",
                                     targetname="IncomegroupName (WB)",
                                     valuemap={'L': 'LDCs',
                                               'LM': 'LMICs',
                                               'UM':'UMICs',
                                               'H': 'HICs',
                                               'LM*':'LMICs'}
                                     ):
    """
    The Incomegroup classification of the oecd for counties is stated as "active data", meaning it's a feature
    that changes every year for some countries. further more the classification used by the oecd is based on the
    UN-list of LDCs while filling the gaps with delayed data from the worldbank. This leads to some problems 
    regarding historical data. This function merges the historical classification data provided by the worldbank 
    with the oecd-microdata. see: https://datahelpdesk.worldbank.org/knowledgebase/articles/378834-how-does-the-world-bank-classify-countries . Classificationdata is expected as a csv-file in the format 
       "id";"Country";1987;1988;1989;...
    where "id" is the iso3code of the country and "Country" is the speaking name. Missing values are backfilled.

    @param ioecddf: microdata-Dataframe of oecd
    @param oecd_iso3: the mapping from oecd-country-codes to iso3-country-codes
    @param datadir: the directory where to find the historical classification data.
    @param datafilename: the filename of the historical classification
    @param datefeature: which feature to use to merge on - must be a datetime-feature
    @param valuemap: the historical data uses different values for classification then the oecd, mapping is used to replace them.
    @param oecdidfeature: the feature to as countriecodes
    @param targetname: how to name the new feature

    
    """
    # read the historical classification in Incomegroups from the worldbank
    icgroup_df = pd.read_csv(datadir+datafilename,header=0,quotechar='"',low_memory=False,sep=";",na_values=['..'])

    # the historical data some datapoints
    # fill missing values with the value from the next valid year 
    # this is a little dirty in code
    T = icgroup_df.T
    T = T.fillna(method ='backfill') 

    icgroup_df = T.T
    icgroup_df = icgroup_df.melt(id_vars=('id','Country'),var_name="Year")

    # replace the values used for classification with the values used by oecd
    icgroup_df = icgroup_df.replace({'value': valuemap})
    icgroup_df = icgroup_df.replace({'id': oecd_iso3})

    # create a mergeable unique feature
    icgroup_df['mergefield'] = icgroup_df['Year'].apply(lambda x: str(x))
    icgroup_df['mergefield'] = icgroup_df['mergefield'] + icgroup_df['id']

    df = ioecddf.copy()
        

    # create a mergefield within the dataframe
    df['mergefield'] = df[datefeature].apply(lambda x: "%.0f" %(x.year)) # NaN cannot be converted to Int
    df['mergefield'] = df['mergefield'] + df[oecdidfeature]
    #display(df.sample())
    df = df.merge(icgroup_df.add_prefix("worldbank "),
                  right_on='worldbank mergefield',
                  how="left",left_on='mergefield',indicator=True)
    df.drop(columns=['mergefield','worldbank id','worldbank Country',
                     'worldbank Year','worldbank mergefield','_merge'],inplace=True)
    df.rename(columns={'worldbank value': targetname},inplace=True)

    return df

def apply_historical_incomegroups_oecd(ioecddf,
                                       datadir="data/",datafilename="oecd-incomegroup-history.csv",
                                       datefeature="CommitmentDate",useindex=False,
                                       oecdidfeature="RecipientCode",
                                       targetname="IncomegroupName (oecd hist)",
                                       valuemap = {
                                           "High Income Countries": "HICs",
                                           "Least Developed Countries": "LDCs",
                                           "Lower Middle Income Countries": "LMICs",
                                           "More Advanced Developing Countries and Territories": "MADCTs",
                                           "Other Low Income Countries": "Other LICs",
                                           "Upper Middle Income Countries": "UMICs"}
                                     ):
    """
    add the historical incomegroup classification data to the oecd-dataframe

    @param ioecddf: microdata-Dataframe of oecd
    @param datadir: the directory where to find the historical classification data.
    @param datafilename: the filename of the historical classification
    @param datefeature: which feature to use to merge on - must be a datetime-feature
    @param valuemap: the historical data uses different values for classification then the oecd. the mapping is used to replace them.
    @param oecdidfeature: the feature to as countriecodes
    @param targetname: how to name the new feature

    @return: a copy of the original 'ioecddf' with the new feature 'targetname'
    """

    df = ioecddf.copy()
    df['mergefield'] = df[datefeature].apply(lambda x: "%.0f" %(x.year))
    df['mergefield'] = df['mergefield'] + df[oecdidfeature]
    
    hist_oecd_ig=pd.read_csv(filepath_or_buffer=datadir + datafilename,
                             dtype={'year': np.unicode_, 'RecipientCode': np.unicode_},
                             usecols=['year','incomegroup','RecipientCode'],
                             delimiter=";")
    hist_oecd_ig.replace({'incomegroup': valuemap},inplace=True)

    hist_oecd_ig.rename(inplace=True,
                        columns={'incomegroup': targetname,'RecipientCode':'hist_oecd_ig_id'})

    hist_oecd_ig['mergefield'] = hist_oecd_ig['year'] 
    hist_oecd_ig['mergefield'] = hist_oecd_ig['mergefield'] + hist_oecd_ig['hist_oecd_ig_id']
    hist_oecd_ig.drop(columns=['hist_oecd_ig_id','year'],inplace=True)

    df = df.merge(hist_oecd_ig,on="mergefield",how="left")
    df.drop(columns=['mergefield'],inplace=True)
    return df
            

def merge_wbseries_with_oecd_data(ioecddf, iwbdf, codemapping,cachedir="data/cache",mergedonor=True, mergerecipient=True):
    """
    merges yearly stats from the worldbank with the microdata provided by the oecd based on a
    a country-code mapping. The dataenrichment is done for DonorCode and RecipientCode. The
    series from worldbank is prefixed with "Donorstat " and "Recipientstat ". The 
    commitmentdate (year) is used as the second attribute

    @param ioecddf: a DataFrame with the microdata from oecd containing 
    @param iwbdf: a DataFrame containing stat-series from the worldbank
    @param codemapping: a mapping from oecd-country-codes to iso3 country codes used by worldbank
    @param cachedir: where to store/find cached data
    @param mergedonor: per default the worldbank data is merged on donorcountry
    @param mergerecipient: per default the worldbank data is merged on recipientcountry

    @return: a DataFrame with enrichments for the Donor and Recipient
    """
    
    odf = pd.DataFrame()
    
    # first we kick out everything that cannot be merged, b/c it's not in the mapping
    oecddf = ioecddf.copy()
    if mergedonor:
        oecddf = ioecddf[ioecddf['DonorCode'].isin(list(codemapping))]
    #print(oecddf.describe())
    if mergerecipient:
        oecddf = oecddf[oecddf['RecipientCode'].isin(list(codemapping))]
    #print(oecddf.describe())
    wbdf = iwbdf[iwbdf['Country'].isin(list(codemapping))].reset_index()
    #print(wbdf.describe())

    # merge some additional infos about the countries from country-data
    cdf = get_regionnames(cachedir=cachedir)
    wbdf = wbdf.merge(cdf, right_on="id", how="left", left_on="Country")
    #print(wbdf.describe())
    
    # create a mergefield on worldbank data
    wbdf['mergefield'] = wbdf['Year'].apply(lambda x: str(x))
    wbdf['mergefield'] = wbdf['mergefield'] + wbdf['id']
    
    odf = oecddf.copy()
    
    # create two mergefields for Donor and Recipients
    if mergedonor:
        odf['donormerge'] = odf['CommitmentDate'].apply(lambda x: str(x.year))
        odf['donormerge'] = odf['donormerge'] + odf['DonorCode'].apply(lambda x: str(codemapping[x]))
        odf = odf.merge(wbdf.add_prefix("Donorstat "),
                        right_on='Donorstat mergefield',
                        how="left",left_on='donormerge')
        odf.drop(columns=['Donorstat mergefield','donormerge','Donorstat index','Donorstat Year','Donorstat name','Donorstat Country'],inplace=True)
        odf.rename(columns={'Donorstat id': 'Donorstat iso3Code'},inplace=True)

    if mergerecipient:
        odf['recipientmerge'] = odf['CommitmentDate'].apply(lambda x: str(x.year))
        odf['recipientmerge'] = odf['recipientmerge'] + odf['RecipientCode'].apply(lambda x: str(codemapping[x]))
        odf = odf.merge(wbdf.add_prefix("Recipientstat "),
                        right_on='Recipientstat mergefield',
                        how="left",left_on="recipientmerge")
        odf.drop(columns=['Recipientstat mergefield','recipientmerge','Recipientstat index','Recipientstat Year','Recipientstat Country'],inplace=True)
        odf.rename(columns={'Recipientstat id': 'Recipientstat iso3Code'},inplace=True)

    
    
    return odf

if __name__ == "__main__":
    from worldbankApi import fetch_series
    wbdf = fetch_series()
    oecddf = read_water_data()
    idf = extract_features(oecddf).reset_index()
    df = merge_wbseries_with_oecd_data(idf,wbdf)
    print(df.describe())
    #print(get_oecd_iso3_code_mapping())






    
