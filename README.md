# water-data
UCLab and tageszeitung joint project.
# get the raw-data

The rawdata was extracted from two sources. First the 'Microdata' of the OECD Creditor Reporting System (CRS1) which can be downloaded/exported from their webpage ( https://stats.oecd.org/viewhtml.aspx?datasetcode=CRS1 )

    https://stats.oecd.org/FileView2.aspx?IDFile=82c8801d-641f-49ec-8ace-9e003224c3d1 crs1994-73.zip
    https://stats.oecd.org/FileView2.aspx?IDFile=c0c345b3-74e8-499d-a280-e8af7e3f47e2 crs1999-95.zip
    https://stats.oecd.org/FileView2.aspx?IDFile=02d8f462-08eb-4b99-b12d-bd6a0edf9625 crs2000-01.zip
    https://stats.oecd.org/FileView2.aspx?IDFile=28e76303-4d91-4a36-aabb-6cce13c084b2 crs2002-03.zip
    https://stats.oecd.org/FileView2.aspx?IDFile=26a883a7-afb4-4d98-95e8-29cc63638c28 crs2005-04.zip
    https://stats.oecd.org/FileView2.aspx?IDFile=8d7734f9-4fc6-4c3a-994f-8bfd2713173d crs2006.zip
    https://stats.oecd.org/FileView2.aspx?IDFile=f49c3166-e1fd-48f1-831a-c1fe38b96c1f crs2007.zip
    https://stats.oecd.org/FileView2.aspx?IDFile=251471b4-5117-49cf-8d73-7e9b4eb1860a crs2008.zip
    https://stats.oecd.org/FileView2.aspx?IDFile=a530b713-0f45-48d7-b921-e3a70871ba58 crs2009.zip
    https://stats.oecd.org/FileView2.aspx?IDFile=cb44825a-d8e8-41b0-80f8-f42e67f96136 crs2010.zip
    https://stats.oecd.org/FileView2.aspx?IDFile=05dd3f52-a5fd-4d20-8ded-2b4159a5677b crs2011.zip
    https://stats.oecd.org/FileView2.aspx?IDFile=ed338f01-47b7-421c-92be-dee8141202e8 crs2012.zip
    https://stats.oecd.org/FileView2.aspx?IDFile=fa4ae8e5-a954-4cd5-ae72-9053094bf98d crs2013.zip
    https://stats.oecd.org/FileView2.aspx?IDFile=a990e786-6647-4e5a-8795-bbec445294ba crs2014.zip
    https://stats.oecd.org/FileView2.aspx?IDFile=4440e8de-f471-479a-9692-ddd7bf06d7d2 crs2015.zip
    https://stats.oecd.org/FileView2.aspx?IDFile=b64f050c-4e2f-44ed-a8e6-db32ce00fd4f crs2016.zip
    https://stats.oecd.org/FileView2.aspx?IDFile=bf6e1a95-a4ac-4545-9e91-1a38c9b738de crs2017.zip
    https://stats.oecd.org/FileView2.aspx?IDFile=ed94e89a-e81e-4718-ac69-2a51f5429657 crs2018.zip
    https://stats.oecd.org/FileView2.aspx?IDFile=2ae42512-f006-4fd0-92ed-b636f6c2583d crs2019.zip

The 19 zip-files are about 513MB in total - at the time of download the last update was from 05.Nov 2020. They are about 3GB raw-csv-data resp. about 4.1 million entries. The data is encoded in iso8859_15, the columns are seperated by "|" and quoted by '"'.

In this analyse only a part of the provided attributes are used:

* "Year": The year the information about a project was submited to the OECD
* "DonorCode": Country code of the donating country as a OECD-specific number (label)
* "DonorName": Country name of the donating country as a text-label (ex: 'Germany' )
* "AgencyCode": The Agency code of the donating agency as a OECD-specific number (label)
* "AgencyName": The Agency name of the donating agency as a text-label (ex: 'Agency for International Development')
* "RecipientCode": The recipient of the donation as a OECD-specific number (label)
* "RecipientName": The recipient of the donation as a text-label (ex: 'Indonesia')
* "USD_Disbursement_Defl": the 'constant' amount of million USD donated with reference to the year 2010 (float number). see https://www.oecd.org/dac/stats/informationnoteonthedacdeflators.htm for details about deflators
* "ShortDescription": a short description of the project as free form text
* "LongDescription": a long description of the project as free form text
* "ProjectTitle": the project title as free form text ( ex.: 'Election observation mission second round of the presidential elections, Ukraine')
* "PurposeName": the purpose of the project as a text-label (ex.: 'Basic sanitation')
* "SectorCode": Sector code as a OECD-specific number (label) ( ex.: '410' for water related projects )
* "SectorName": the sector name as a text-label (ex.: 'I.1.c. Secondary Education' )
* "ChannelReportedName": the project executor as free form text (ex.: 'PUBLIC SECTOR INSTITUTIONS' , 'Donor Government', 'United Nations Environment Programme')
* "CommitmentDate": the date of the grant/loan/credit/donation
* "ExpectedStartDate": the date the project is expected to start
* "CompletionDate": the date the project is expected to end/ has ended
* "IncomegroupName": development categroy of the recipient (ex.: 'LDCs','LMICs' ... see  https://www.oecd.org/dac/financing-sustainable-development/development-finance-standards/DAC-List-of-ODA-Recipients-for-reporting-2020-flows.pdf for details

The data can be downloaded by executing fetchdata.sh. The script will create the directory 'data' and store the zipfiles under the name referrenced in the scripts.

# quicksetup for up python env

<pre>
git clone https://github.com/die-tageszeitung/water-data

cd water-data

virtualenv -p python3 .

source bin/activate

pip install pandas
pip install matplotlib
pip install numpy
pip install kaleido
pip install plotly
pip install psutil
pip install world_bank_data
</pre>

then run

<pre>
./python/src/water-data-lib.py
</pre>
