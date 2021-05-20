# Yearbook Image Generation Script

## yearbookScript.py usage
`python yearbookScript.py [-h] -f FILE -d {CMPN,EXTC,IT} [-v [VERBOSE]]`

#### Arguments
-h, --help            show this help message and exit <br>
-f FILE, --file FILE  Data Source .csv file <br>
-d {CMPN,EXTC,IT}, --dept {CMPN,EXTC,IT} Class Department  <br>
-v [VERBOSE], --verbose [VERBOSE] Display Generated File StudentName <br>
-s [SKIP], --skip [SKIP] Number of Indexes to Skip

##### Expected Column Names in csv file : Timestamp,Full Name.,Roll No.,Picture,Quote,Groupfie
Yes I'm aware of the typo. However we do not handle Groupfile images in this script so even if absent no isses.

## Error Logging
#### logs.txt
Error Logs file generated to track failed data points and store error log.

## Prerequisites
Generate Google Drive API Credentials : https://developers.google.com/drive/api/v3/quickstart/python
<br>
Store credentials.json with Script file 

