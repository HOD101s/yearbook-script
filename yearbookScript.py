from PIL import Image, ImageDraw, ImageFont, ImageOps
import textwrap
Image.MAX_IMAGE_PIXELS = None

import argparse
from tqdm import tqdm
import numpy as np
import pandas as pd
import requests
import shutil

import sys
import os.path
import io
import pickle
from urllib.parse import urlparse
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", help = "Data Source .csv file",required=True)
parser.add_argument("-d", "--dept", help = "Class Department",choices=['CMPN','EXTC','IT'],required=True) 
parser.add_argument("-v", "--verbose", type=str2bool, nargs='?', default=False, help = "Display Generated File StudentName")
parser.add_argument("-s", "--skip", default=0, help = "Number of Indexes to Skip")
args = parser.parse_args()

sourcefile = args.file
folder = sourcefile.split('.')[0]

if sourcefile[-4:] != ".csv":
    print("Source File must be CSV")
    sys.exit()


# Google Auth
SCOPES = ['https://www.googleapis.com/auth/drive']
creds = None
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)
drive = build('drive', 'v3', credentials=creds)

# Reading File
data = pd.read_csv(sourcefile)

# Extract image Ids
def getId(url):
    urls = url.split(',')
    res = []
    for link in urls:
        res.append(urlparse(link).query[3:])
    return res

# DATA is not consistent therefore must change Column names per csv or edit csvs
data['ImageId'] = data['Picture'].apply(lambda x : getId(x))


def generateStudent(target,name,img,quote,roll,index,verbose):
    
    # get image    
    # google api to download file into student.png
    
    request = drive.files().get_media(fileId=img)
    fh = io.FileIO("student.png", 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        if verbose:
            print(name)  
        
    # File Naming Convention : RollNumber StudentName PhotoNumber Rotation
    filename = str(roll)+' '+name+' '+str(index+1)
        
    try:
        student = Image.open('student.png')
    except:
        print(f'Failed on Entry : {index} Roll : {roll} Name : {name}')
        with open(folder+'/'+'logs.txt','w') as f:
            f.write(f'Failed on Image : {index+1} Roll : {roll} Name : {name}\n')
        return

    targetCopy = target.copy()

    if student.size[0]>student.size[1]:
        # save vertical image with 90 shifts
        getImg(target,name,student.rotate(270,expand=True),quote).save(folder+'/'+filename+' 270.png')
        getImg(target,name,student.rotate(90,expand=True),quote).save(folder+'/'+filename+' 90.png')
        
    getImg(targetCopy,name,student,quote).save(folder+'/'+filename+'.png')
        

def getImg(targetObj,name,student,quote,CORRECTION=7):

    target = targetObj.copy()
    
    d = ImageDraw.Draw(target)
    
    # Paste student image in target
    student.thumbnail( (500,500), Image.ANTIALIAS)
    student = ImageOps.expand(student, border=3)
    target.paste(student,((target.size[0]-student.size[0])//2 + CORRECTION, ((target.size[1]-student.size[1])//2-60 )))
    
    # Add Name
    namefont = ImageFont.truetype("fonts/gabr.ttf", 40)
    w,h = d.textsize(name,namefont)
    d.text(((target.size[0]-w)/2+ CORRECTION,750), name, fill=(0,0,0),font=namefont)
    
    # Add Quote
    quotefont = ImageFont.truetype("fonts/Symbola.ttf", 30)
    currentHt,pad = 810,30
    para = textwrap.wrap(quote, width=45)
    for line in para:
        w,h = d.textsize(line,quotefont)
        d.text(((target.size[0]-w)/2+ CORRECTION,currentHt), line, fill=(0,0,0),font=quotefont)
        currentHt += pad
    
    return target

template = {}
template['CMPN'] = "targets/targetPink.png"
template['EXTC'] = "targets/targetBlue.png"
template['IT'] = "targets/targetGreen.png"

skip = args.skip
for i in tqdm(range(skip,data.shape[0])):
    target = Image.open(template[args.dept])
    name = data.iloc[i]['Full Name.'].strip()
    if len(name.split(' ')) >2:
        name = ' '.join([name.split(' ')[0],name.split(' ')[-1]])
    img = data.iloc[i]['ImageId']
    quote = data.iloc[i]['Quote']
    roll = data.iloc[i]['Roll No.']
    try:
        os.mkdir(folder)
    except:
        pass
    for j in range(len(img)):
        generateStudent(target,name,img[j],quote,roll,j,args.verbose)