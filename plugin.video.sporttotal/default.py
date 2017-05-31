#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import urlparse
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc
import xbmcvfs
import urllib, urllib2, socket, cookielib, re, os, shutil,json
import time
import datetime
from bs4 import BeautifulSoup

# Setting Variablen Des Plugins
global debuging
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])

args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString
defaultBackground = ""
defaultThumb = ""
cliplist=[]
filelist=[]
profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)

mainurl="http://www.myspass.de"
#Directory für Token Anlegen
if not xbmcvfs.exists(temp):       
       xbmcvfs.mkdirs(temp)
       
xbmcplugin.setContent(int(sys.argv[1]), 'musicvideos')
icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')
useThumbAsFanart=addon.getSetting("useThumbAsFanart") == "true"



def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 

def parameters_string_to_dict(parameters):
  paramDict = {}
  if parameters:
    paramPairs = parameters[1:].split("&")
    for paramsPair in paramPairs:
      paramSplits = paramsPair.split('=')
      if (len(paramSplits)) == 2:
        paramDict[paramSplits[0]] = paramSplits[1]
  return paramDict
  
    
def addDir(name, url, mode, iconimage, desc=""):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
  if useThumbAsFanart:
    if not iconimage or iconimage==icon or iconimage==defaultThumb:
      iconimage = defaultBackground    
    liz.setArt({ 'fanart': iconimage })
  else:
    liz.setArt({ 'fanart': defaultBackground })    
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok
  
def addLink(name, url, mode, iconimage, duration="", desc="",artist_id="",genre="",shortname="",production_year=0,zeit=0,liedid=0):  
  cd=addon.getSetting("password")  
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre,"Sorttitle":shortname,"Dateadded":zeit,"year":production_year })
  liz.setProperty('IsPlayable', 'true')
  liz.addStreamInfo('video', { 'duration' : duration })
  liz.setArt({ 'fanart': iconimage })   
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
  return ok


def getUrl(url,data="x"):        
        debug("Get Url: " +url)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        userAgent = "Dalvik/2.1.0 (Linux; U; Android 5.0;)"
        opener.addheaders = [('User-Agent', userAgent)]
        try:
          if data!="x" :
             content=opener.open(url,data=data).read()
          else:
             content=opener.open(url).read()
        except urllib2.HTTPError as e:
             #print e.code   
             cc=e.read()  
             struktur = json.loads(cc)  
             error=struktur["errors"][0] 
             error=unicode(error).encode("utf-8")
             debug("ERROR : " + error)
             dialog = xbmcgui.Dialog()
             nr=dialog.ok("Error", error)
             return ""
             
        opener.close()
        return content


      #addDir(namenliste[i], namenliste[i], mode+datum,logoliste[i],ids=str(idliste[i]))
   #xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   
  



params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))


def top20(url)      :
        content=getUrl(url)        
        htmlPage = BeautifulSoup(content, 'html.parser')        
        liste = htmlPage.find("div",{"class" :"place2"})        
        elemente=liste.findAll("div",{"class" :"template"})
        for element in elemente:        
          BegegnungLabel=element.find("span",{"class" :"BegegnungLabel"}).string.encode("utf-8")
          BegegnungLabel2=element.find("span",{"class" :"BegegnungLabel2"}).string.encode("utf-8")
          staffelnameLabel=element.find("span",{"class" :"staffelnameLabel"}).string.encode("utf-8")
          dates=element.findAll("span",{"class" :"Spieldatum"})
          datum=dates[0].string.encode("utf-8")
          zeit=dates[1].string.encode("utf-8")
          urln_sub=element.find("a",{"class" :"LiveLink"})['href']        
          urllink="https://www.sporttotal.tv/"+urln_sub
          addLink(BegegnungLabel +" "+BegegnungLabel2 +"( "+ datum+" "+zeit +" )", urllink, 'playvideo', "")    
        xbmcplugin.endOfDirectory(addon_handle)
def playvideo(url):
  content=getUrl(url) 
  file=re.compile('file: "(.+?)"', re.DOTALL).findall(content)[0]
  listitem = xbmcgui.ListItem(path=file)
  xbmcplugin.setResolvedUrl(addon_handle, True, listitem)

  
def liegen():  
  addDir("Regionalliega Nord", "https://www.sporttotal.tv/ligen.aspx?CM=agi1", 'Top20',"https://www.sporttotal.tv/cpics/block1-4.png")   
  addDir("BayernLiga Süd", "https://www.sporttotal.tv/ligen.aspx?CM=agi2", 'Top20',"https://www.sporttotal.tv/cpics/block2-4.png")   
  addDir("BayernLiga Nord", "https://www.sporttotal.tv/ligen.aspx?CM=agi3", 'Top20',"https://www.sporttotal.tv/cpics/block2-4.png")   
  addDir("Oberliega Niedersachsen", "https://www.sporttotal.tv/ligen.aspx?CM=agi4", 'Top20',"https://www.sporttotal.tv/cpics/block4-4.png")   
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
  
if mode is '':
    addDir("TOPSPIEL DER WOCHE", "https://www.sporttotal.tv/default.aspx", 'Top20',"")   
    addDir("Liegen", "", 'liegen',"")   
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
else:
  # Wenn Settings ausgewählt wurde
  if mode == 'Settings':
          addon.openSettings()
  if mode == 'Top20':
          top20(url)
  if mode == 'playvideo':
          playvideo(url) 
  if mode == 'liegen':
          liegen()           