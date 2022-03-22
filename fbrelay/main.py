from asyncore import write
from cgitb import text
from genericpath import exists
from hashlib import new
from http import cookies
import http
from operator import truediv
import pathlib
from pprint import pprint
from shlex import shlex
import time
from typing import Mapping
from urllib.response import addbase
from utils import WaitForId

import logging
from xmlrpc.client import ResponseError;

class MyLogger(logging.getLoggerClass()):
    def __init__(self, name):
        logging.Logger.__init__(self,name)
    def isEnabledFor(self, level: int) -> bool:
        return True
    def debug(self, msg: object, *args: object) -> None:
        pprint(msg)
    def info(self, msg: object, *args: object ) -> None:
        pprint(msg)
    def warn(self, msg: object, *args: object) -> None:
        pprint(msg)
    def error(self, msg: object, *args: object) -> None:
        pprint(msg)
    def critical(self, msg: object, *args: object) -> None:
        pprint(msg)
    def log(self, level: int, msg: object, *args: object) -> None:
        pprint(msg)

#logging.setLoggerClass(MyLogger)

from facebook_scraper import get_posts;
from facebook_scraper import get_photos;
from facebook_scraper import get_profile;
from facebook_scraper import set_user_agent;
from facebook_scraper import FacebookScraper;
from requests_html import HTMLSession;
import facebook_scraper;
from importlib.metadata import version;
import subprocess;
import json;
import os;
import requests;
import shutil;
import shlex;
import sys;

ssbPath="/root/.ssb/"
ssbShared="/root/.ssbshared"
def EnsureSSBDir():
    if not os.path.exists("/root/.ssb)") and not os.path.islink("/root/.ssb") and not os.path.ismount("/root/.ssb"):
        os.makedirs("/root/.ssb/")
    if not os.path.exists(ssbShared) and not os.path.islink(ssbShared) and not os.path.ismount(ssbShared):
        os.makedirs(ssbShared)


EnsureSSBDir()

fileDir = pathlib.Path(__file__).parent.resolve()
ssbConfigPath=os.path.join(fileDir,"config")
cookiesPath=os.path.join(ssbShared,"cookies.txt")

def StartServer(port:int):
    global ssbConfigPath
    shutil.copy(ssbConfigPath, ssbPath)
    ssbserver = subprocess.Popen(["ssb-server","start","--host","0.0.0.0","--port",str(port)], shell=False)
    WaitForId()

def UpdateProfile(fbprofilename):    
    lg = logging.getLogger()
    lg.warning("POS_2")
    global ssbPath
    path = os.path.join(ssbPath,fbprofilename)
    if not os.path.exists(path):
        os.makedirs(path)

    posted=os.path.join(path,"posted")
    
    #cookiesPath=os.path.join(path,"cookies.txt")
    global cookiesPath
    if not os.path.exists(cookiesPath) and not os.path.islink(cookiesPath) and not os.path.ismount(cookiesPath):
        cookiesPath=None


    tmpPath=os.path.join(path,"tmp")

    if not os.path.exists(tmpPath):
        os.makedirs(tmpPath)

    ssbserverpath = shutil.which('ssb-server')
    def AddImageToBlobStore(url:str):
        lg.warning("POS_3")
        if not url:
            return ""
        img_data = requests.get(url).content
        downloadPath = os.path.join(tmpPath,'image_name.jpg')
        with open(downloadPath, 'wb+') as handler:
            handler.write(img_data)

        if not os.path.exists(downloadPath):
            logging.getLogger().error("Failed to write image to file "+downloadPath)
        addBlob = subprocess.run(["ssb-server","blobs.add",downloadPath],shell=False, capture_output=True)
        blobid = addBlob.stdout.decode("utf-8")
        lg.warning("POS_4")
        return blobid.strip()

    def PostOnSSB(post, image):
        link=post['link']
        time=post['time']
        timestr=""
        if time:
            timestr=time.strftime("%d-%b-%Y (%H:%M)")
        msg="###### " + timestr + "\n" + post["post_text"] + "\n"
        if(image):
            if(link):
                msg=msg+"["
            msg = msg + "\n ![missing image](" + image + ")"
            if link:
                msg = msg + "](" + link + ")"
        else:
            if(link):
                msg = msg + "[LINK](" + link + ")"
            
        # msg="![](" + shlex.quote(image) + ") \n" + "###### " + shlex.quote(timestr) + "\n" + shlex.quote(post["text"]) + "\n ![](" + shlex.quote(image) + ")"
        sharedtext = post['shared_text']
        if ( sharedtext):
            sharedtext = sharedtext.replace("\n", "\n>")
            msg = msg + "\n " + "> " + sharedtext
            
        finalmsg = shlex.quote(msg)
        result=subprocess.run(
            [
                ssbserverpath,
                "publish",
                "--type",
                "post",
                "--text",
                msg
            ]
            ,shell=False, capture_output=True,text=True)
        print("Result:" +result.stdout)

    id=WaitForId()

    oldobj = dict()
    if exists(posted):
        with open(posted) as json_file:
            oldobj = json.load(json_file)

    logger=logging.getLogger()
    #set_user_agent("Mozilla/5.0 (Linux; Android 8.0.0; SM-G960F Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36")
    #browser
    #set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36")
    
    profile=None
    while True:
        try:
            #cookies = http.cookiejar.FileCookieJar(cookiesPath)
            #session = HTMLSession()
            #session.cookies=cookies
            #r = session.get('https://m.facebook.com/settings?locale=en_US')
            import socket
            
            profile = get_profile(fbprofilename, allow_extra_requests=True, likes=False,cookies=cookiesPath)
            break
        except requests.exceptions.ConnectTimeout as ex:
            logger.error("Failed to retrieve profile, retrying in 5 minutes")
            time.sleep(60*5)
        except BaseException as ex:
            logger.exception(ex)
            time.sleep(60*5)
        except:
            logger.error("Unhandled exception")
            time.sleep(60*5)
            pass
        
    logger.warning("Successfuly retrieved profile for " + fbprofilename)
    #print("version: " + version('facebook_scraper'))

    oldcoverphoto=""
    if "cover_photo" in oldobj:
        oldcoverphoto = oldobj["cover_photo"]
    photourl = profile["cover_photo"]
    if(photourl != oldcoverphoto):        
        lg.warning("Updating profile cover photo")
        oldobj["cover_photo"]=photourl
        lg.warning("Adding image to blob store " + photourl)
        photoblob = AddImageToBlobStore(photourl)
        lg.warning("Added image to blob store: " + photoblob)
        #picture
        result=subprocess.run(
                [
                    ssbserverpath,
                    "publish",
                    "--type",
                    "about",
                    "--about",
                    id,
                    "--image",
                    photoblob
                ]
                ,shell=False, capture_output=True,text=True)
        #name
        lg.warning("Updated profile cover photo")
    oldname=""
    if "name" in oldobj:
        oldname = oldobj["name"]

    newname = profile["Name"]
    newname = newname.replace(" - About","")

    if(newname != oldname):        
        lg.warning("Updating profile name")
        oldobj["name"]=newname
        result=subprocess.run(
                [
                    ssbserverpath,
                    "publish",
                    "--type",
                    "about",
                    "--about",
                    id,
                    "--name",
                    newname
                ]
                ,shell=False, capture_output=True,text=True)
        
        lg.warning("Updated profile name")

    logger.warning("Retrieving posts from facebook")
    posts = get_posts(fbprofilename, pages=5, cookies=cookiesPath)
    orderedposts = list()
    for post in posts:
        id = post['post_id']
        if(id not in oldobj):
            oldobj[id] = {}
            orderedposts.append(post)

    def sortfunc(post):
        if not "timestmap" in post:
            return 0
        return int(post['timestamp'])
    orderedposts.sort(key=sortfunc)

    logger.warning("Posting retrieved posts")
    for post in orderedposts:
        lg.warning("Adding post")
        try:        
            PostOnSSB(post, AddImageToBlobStore(post['image']))        
        except:
            pass
        lg.warning("Post added")

    with open(posted,'w') as outfile:
        json.dump(oldobj,outfile)

    # See PyCharm help at https://www.jetbrains.com/help/pycharm/



def main():
    fbprofilename=sys.argv[1]
    sleepTime = int(sys.argv[2])
    port = int(sys.argv[3])
    lg = logging.getLogger()
    StartServer(port)
    id = WaitForId()
    lg.warning("Starting for profile:" + id)

    while True:
        lg.warning("Updating profile: " + fbprofilename + " " + "(" + sys.argv[2] + ")")
        UpdateProfile(fbprofilename)
        lg.warning("Sleeping for " + sys.argv[2] + " minutes...")
        time.sleep(sleepTime * 60)
        lg.warning("Done sleeping")

if __name__=="__main__":
    main()