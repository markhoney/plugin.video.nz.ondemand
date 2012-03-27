# Generic functions

import sys, re, os
import resources.config as config
settings = config.__settings__
from xml.dom import minidom
from xml.parsers.expat import ExpatError
# import xbmc # http://xbmc.sourceforge.net/python-docs/xbmc.html
import xbmcgui # http://xbmc.sourceforge.net/python-docs/xbmcgui.html
import xbmcplugin # http://xbmc.sourceforge.net/python-docs/xbmcplugin.html

#def initaddon:
# import shutil, os
# shutil.rmtree(__cache__)
# os.mkdir(__cache__)

class webpage:
 def __init__(self, url = "", agent = 'ps3', cookie = ""):
  self.doc = ""
  self.agent = agent
  self.cookie = cookie
  if url:
   self.url = url
   self.get(url)

 def get(self, url):
  import urllib2
  opener = urllib2.build_opener()
  urllib2.install_opener(opener)
  print "Requesting URL: %s" % (url)
  req = urllib2.Request(url)
  req.add_header('User-agent', self.fullagent(self.agent))
  if self.cookie:
   req.add_header('Cookie', self.cookie) # 'nzos_html5=true' for NZOnScreen
  try:
   response = urllib2.urlopen(req, timeout = 20)
   self.doc = response.read()
   response.close()
  except urllib2.HTTPError, err:
   sys.stderr.write("urllib2.HTTPError requesting URL: %s" % (err.code))
  else:
   return self.doc

 def xml(self):
  from xml.dom import minidom
  try:
   document = minidom.parseString(self.doc)
   if document:
    self.xmldoc = document.documentElement
    return self.xmldoc
  except: # ExpatError: # Thrown if the content contains just the <xml> tag and no actual content. Some of the TVNZ .xml files are like this :(
   return False

 def html(self):
  from BeautifulSoup import BeautifulSoup
  try:
   return BeautifulSoup(self.doc)
  except:
   pass

 def fullagent(self, agent):
  if agent == "ps3":
   return 'Mozilla/5.0 (PLAYSTATION 3; 3.55)'
  elif agent == 'iphone':
   return 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1C25 Safari/419.3'
  elif agent == 'ipad':
   return 'Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10'
  else: # Chrome
   return 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.204 Safari/534.16'



class xbmcItem:
 def __init__(self, folder = True):
  self.folder = folder
  self.path = ""
  self.info = dict()
  self.info["Icon"] = "DefaultVideo.png"
  self.info["Thumb"] = ""
  self.urls = dict()

 def applyURL(self, bitrate):
  if bitrate in self.urls:
   self.info["FileName"] = self.urls[bitrate]

 def stack(self, urls): #Build a URL stack from multiple URLs for the XBMC player
  if len(urls) == 1:
   return urls[0]
  elif len(urls) > 1:
   return "stack://" + " , ".join([url.replace(',', ',,').strip() for url in urls])
  return False
  
 def sxe(self):
  if 'Season' in self.info and 'Episode' in self.info:
   return str(self.info["Season"]) + "x" + str(self.info["Episode"]).zfill(2)
  return False
  
 def unescape(self, s): #Convert escaped HTML characters back to native unicode, e.g. &gt; to > and &quot; to "
  from htmlentitydefs import name2codepoint
  return re.sub('&(%s);' % '|'.join(name2codepoint), lambda m: unichr(name2codepoint[m.group(1)]), s)

 def titleplot(self): #Build a nice title from the program title and sub-title (given as PlotOutline)
  if self.info['PlotOutline']:
   self.info['Title'] = "%s - %s" % (self.info['TVShowTitle'], self.info['PlotOutline'])

 def url(self, urls = False, quality = 'High'): # Low, Medium, High
  if not urls:
   urls = self.urls
  if quality == 'Medium' and len(self.urls) > 2:
   del urls[max(urls.keys())]
  if quality == 'Low':
   return self.stack(urls[min(urls.keys())])
  else:
   return self.stack(urls[max(urls.keys())])


class xbmcItems:
 def __init__(self):
  self.items = list()
  self.fanart = "fanart.jpg"
  self.sorting = ["UNSORTED", "LABEL"] # ALBUM, ALBUM_IGNORE_THE, ARTIST, ARTIST_IGNORE_THE, DATE, DRIVE_TYPE, DURATION, EPISODE, FILE, GENRE, LABEL, LABEL_IGNORE_THE, MPAA_RATING, NONE, PLAYLIST_ORDER, PRODUCTIONCODE, PROGRAM_COUNT, SIZE, SONG_RATING, STUDIO, STUDIO_IGNORE_THE, TITLE, TITLE_IGNORE_THE, TRACKNUM, UNSORTED, VIDEO_RATING, VIDEO_RUNTIME, VIDEO_TITLE, VIDEO_YEAR
  self.type = ""
  
 def addindex(self, index, total = 0):
  self.add(self, self.items[index], total)

 def add(self, item, total = 0): #Add a list item (media file or folder) to the XBMC page
  # http://xbmc.sourceforge.net/python-docs/xbmcgui.html#ListItem
  if hasattr(item, 'info'):
   info = item.info
   #if hasattr(info, 'FileName'):
   if 'FileName' in info:
    liz = xbmcgui.ListItem(label = info["Title"], iconImage = info["Icon"], thumbnailImage = info["Thumb"])
    try:
     fanart = item.fanart
    except:
     fanart = self.fanart
    liz.setProperty('fanart_image', os.path.join(settings.getAddonInfo('path'), fanart))
    liz.setInfo(type = "video", infoLabels = info)
    if not item.folder:
     liz.setProperty("IsPlayable", "true")
    if item.path:
     liz.setPath(item.path)
     try:
      xbmcplugin.setResolvedUrl(handle = config.__id__, succeeded = True, listitem = liz)
     except:
      self.message("Couldn't play item.")
    else:
     return xbmcplugin.addDirectoryItem(handle = config.__id__, url = info["FileName"], listitem = liz, isFolder = item.folder, totalItems = total)
   else:
    sys.stderr.write("No FileName given")

 def addall(self):
  total = len(self.items)
  for item in self.items:
   self.add(item, total)
  self._sort()

 def addurls(self, urls):
  total = len(urls)
  for bitrate, url in urls.iteritems():
   item = xbmcItem(False)
   item.info['Title'] = str(bitrate)
   item.info['FileName'] = item.stack(url)
   #print item.info['FileName']
   #self.add(item, total)
  #self._sort()
   self.items.append(item)
  self.addall()

 def urls(self, urls):
  total = len(urls)
  for bitrate, url in urls.iteritems():
   item = xbmcItem(False)
   item.info['Title'] = str(bitrate)
   item.info['FileName'] = item.stack(url)
   #print item.info['FileName']
   #self.add(item, total)
  #self._sort()
   self.items.append(item)
  self.addall()

 def _sort(self):
  import xbmcplugin
  for method in self.sorting:
   xbmcplugin.addSortMethod(handle = config.__id__, sortMethod = getattr(xbmcplugin, "SORT_METHOD_" + method))
   #xbmcplugin.addSortMethod(handle = config.__id__, sortMethod = xbmcplugin.SORT_METHOD_UNSORTED)
  if self.type:
   xbmcplugin.setContent(handle = config.__id__, content = self.type)
  xbmcplugin.endOfDirectory(config.__id__)

 def search(self):
  import xbmc
  keyboard = xbmc.Keyboard("", "Search for a Video")
  #keyboard.setHiddenInput(False)
  keyboard.doModal()
  if keyboard.isConfirmed():
   return keyboard.getText()
  return False

 def url(self, urls, quality = 'High'): # Low, Medium, High
  if quality == 'Medium' and len(self.urls) > 2:
   del urls[max(urls.keys())]
  if quality == 'Low':
   return self.stack(urls[min(urls.keys())])
  else:
   return self.stack(urls[max(urls.keys())])

 def stack(self, urls): #Build a URL stack from multiple URLs for the XBMC player
  if len(urls) == 1:
   return urls[0]
  elif len(urls) > 1:
   return "stack://" + " , ".join([url.replace(',', ',,').strip() for url in urls])
  return False

 def message(self, message, title = "Warning"): #Show an on-screen message (useful for debugging)
  import xbmcgui
  dialog = xbmcgui.Dialog()
  if message:
   if message <> "":
    dialog.ok(title, message)
   else:
    dialog.ok("Message", "Empty message text")
  else:
   dialog.ok("Message", "No message text")

 def log(self, message):
  sys.stderr.write(message)
  



def xbmcdate(inputdate, separator = "/"): #Convert a date in "%d/%m/%y" format to an XBMC friendly format
 import time, xbmc
 return time.strftime(xbmc.getRegion("datelong").replace("DDDD,", "").replace("MMMM", "%B").replace("D", "%d").replace("YYYY", "%Y").strip(), time.strptime(inputdate, "%d" + separator + "%m" + separator + "%y"))



