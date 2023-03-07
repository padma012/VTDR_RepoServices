# -*- coding: utf-8 -*-

"""
Created on Tue Sep 28 09:41:18 2021

@author: padma carstens
"""

"""
Purpose: 
1. Downloads published article from figshare using article ID and token. This was built off of UAL-RE ldcoolp code to download article information which was built off of figshare Python code to retrieve article information 
2. Reads the published row for the corresponding article in the "Published" sheet from the google spreadsheet 20211214_VTDR_PublishedDatasets_Log_V7.xls. Creates publication folder following VTDR ingest folder naming and APTrust bag naming convention for preservation.
3. Get article details to create a json file for figshare metadata, creates ArchivalPackageREADME rtf file using create_archivalreadme.

"""

import os
from os.path import exists
import sys
sys.path.append('figshare')
sys.path.append('LD-Cool-P')
#sys.path.insert(0,'C:/Users/padma/anaconda3/envs/curation/figshare/figshare')
#sys.path.insert(0,'C:/Users/padma/anaconda3/envs/curation/figshare')
#sys.path.insert(0,'C:/Users/padma/anaconda3/envs/curation')
#sys.path.insert(0,'C:/Users/padma/anaconda3/envs/curation/LD-Cool-P')
#sys.path.insert(0,'C:/Users/padma/anaconda3/envs/curation/LD-Cool-P/ldcoolp')
import json
from ldcoolp.curation import retrieve
from AutomatedArchivalPackageREADME import create_archivalreadme
from Read_VTDR_Spreadsheet import vtpubsheet
from Read_VTDR_Spreadsheet import vtingsheet
import shutil
import os
#import figshare
from figshare.figshare import Figshare

#Get the parameters from configurations.ini to retrieve information from an article on Figshare

import configparser
config=configparser.ConfigParser()
config.read('configurations.ini')

#Get the ArticleID
ArticleID=config['FigshareSettings']['FigshareArticleID']
#Get the Published Version number 
PublishedVersionNumber=config['FigshareSettings']['PublishedVersionNumber']
#Get the Ingest Version number 
IngestVersionNumber=config['FigshareSettings']['IngestVersionNumber']
#Get your figshare token 
token=config['FigshareSettings']['token']
#Get curator name 
CuratorName=config['FigshareSettings']['CuratorName']

#Get the row information of the published article from the Published sheet using the corresponding ArticleID and Version Number:
vtsheet=vtpubsheet(ArticleID,PublishedVersionNumber)
#Get article id 
article_id=vtsheet['gsarticleid']
#get requestor name
Requestor=vtsheet['gsrequestr']
#get corresponding author name
CorrespondingAuthor=vtsheet['gscorsauth']
#get version
Version=vtsheet['gsversnum']
#get published date in YYYYMMDD format 
DatePublished= vtsheet['gsdatepub'] 
#get DOI suffix
DOIsuffix=vtsheet['DOIsuffix']



#get the row number of published article
PublishedAccessionNumber= vtsheet['gspubnum']
#get the ingest number corresponding to the published accession number
IngestAccessionNumber=vtsheet['gsingestno']
#Get LastnameFirstnameinitial of requestor and corresponding author:
RequestorLFI=vtsheet['gsreqlastfi']
CorrespondingAuthorLFI=vtsheet['gscorrlastfi']

#-----------------------------------------------------
#Create Publication folder and download the figshare published article

#Get current directory:
#directory_path=os.getcwd() 
PubFolderPath=config['PubFolder_PathSettings']['PubFolderPath'] 

aptrustBagName=f"VTDR_{PublishedAccessionNumber}_{IngestAccessionNumber}_DOI_{DOIsuffix}_{CorrespondingAuthorLFI}_v{Version}_{DatePublished}"
payload_directory1=f"DisseminatedContent"
PubFolderPayloadPath=os.path.join(PubFolderPath,aptrustBagName, payload_directory1)
metadata_directory_path=f"{PublishedAccessionNumber}_DownloadedFileMetadata_v{Version}"
fversion=int(PublishedVersionNumber[1])

fs=Figshare(token=token,private=False,version=fversion)
FileDownload=retrieve.download_files(article_id, fversion, fs, data_directory=PubFolderPayloadPath, metadata_directory=metadata_directory_path)

#----------------Download figshare metadata for the published article and write it into a json file

json_out_file1=f"{PubFolderPayloadPath}/{PublishedAccessionNumber}_DisseminatedMetadata.json"

json_response1=fs.get_article_details(article_id,version=fversion)


if not os.path.exists(json_out_file1):
    with open(json_out_file1, 'w') as f:
        json.dump(json_response1,f,indent=4)
else:
    print(f"File exists: {json_out_file1}")

#-----------------------------------------------------------------------------

#Create ArchivalPackageREADME rtf file
archival_directory=os.path.join(PubFolderPath,aptrustBagName)
#create archival readme file using auto_fill_archive.py

reme=create_archivalreadme(ArticleID,PublishedVersionNumber,IngestVersionNumber,CuratorName,archival_directory) 

#-----------------------------------------------------------------------------
#Create VTCurationServicesActions folder in order to save provenance log and email correspondence. Provenance log and Email correspondence are created manually and stroed in this folder
                
VTCurServicesPath=f"VTCurationServicesActions"     
#data_directory_path2=os.path.join(data_directory1,data_directory2,data_directory4)
payload_path=os.path.join(PubFolderPath,aptrustBagName,VTCurServicesPath)
os.mkdir(payload_path)
print("Directory '% s' created" % payload_path) 

