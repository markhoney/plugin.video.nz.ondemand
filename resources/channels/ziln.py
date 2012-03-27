import urllib, string, re, sys, time, os
from BeautifulSoup import BeautifulSoup, SoupStrainer, BeautifulStoneSoup
from xml.dom import minidom

import xbmcgui, xbmcplugin, xbmcaddon

import resources.tools as tools
import resources.config as config
settings = config.__settings__
from resources.tools import webpage


ziln_urls = dict()


class ziln:
 def __init__(self):
  self.base = sys.argv[0]
  self.channel = "Ziln"
  self.urls = dict()
  self.urls['base'] = 'http://www.ziln.co.nz'
  self.urls["rtmp1"] = 'rtmp://flash1.e-cast.co.nz'
  self.urls["rtmp2"] = 'ecast'
  self.urls["rtmp3"] = 'mp4:/ziln'
  self.xbmcitems = tools.xbmcItems()
  self.xbmcitems.fanart = os.path.join('extrafanart', self.channel + '.jpg')
  
 def index(self):
  item = tools.xbmcItem()
  info = item.info
  info["Title"] = config.__language__(30053)
  info["Count"] = 1
  info["FileName"] = "%s?ch=Ziln&folder=channels" % sys.argv[0]
  self.xbmcitems.items.append(item)
  item = tools.xbmcItem()
  info = item.info
  info["Title"] = config.__language__(30065)
  info["Count"] = 2
  info["Thumb"] = "DefaultVideoPlaylists.png"
  info["FileName"] = "%s?ch=Ziln&folder=search" % sys.argv[0]
  self.xbmcitems.items.append(item)
  self.xbmcitems.addall()

 def programmes(self, type, urlext):
  if type == "channel":
   folder = 1
   url = self.urls['base']
  elif type == "video":
   folder = 0
   #url = "%s/channel/%s" % (ziln_urls["ZILN"], urlext)
   url = "%s/assets/php/slider.php?channel=%s" % (self.urls['base'], urlext)
  elif type == "search":
   folder = 0
   url = "%s/search?search_keyword=%s" % (self.urls['base'], urlext.replace(" ", "+"))
  page = webpage(url)
  if page.doc:
   if type == "channel" or type == "search":
    div_tag = SoupStrainer('div')
    html_divtag = BeautifulSoup(page.doc, parseOnlyThese = div_tag)
    programmes = html_divtag.findAll(attrs={'class' : 'programmes'})
   elif type == "video":
    div_tag = SoupStrainer('body')
    html_divtag = BeautifulSoup(page.doc, parseOnlyThese = div_tag)
    programmes = html_divtag.findAll(attrs={'class' : 'slider slider-small'})
   if type == "search":
    type = "video"
   if len(programmes) > 0:
    for programme in programmes:
     list = programme.find('ul')
     if list:
      listitems = list.findAll('li')
      if len(listitems) > 0:
       count = 0
       for listitem in listitems:
        link = listitem.find('a', attrs={'href' : re.compile("^/%s/" % type)})
        if link.img:
         if re.search("assets/images/%ss/" % type, link.img["src"]):
          #item = tools.xbmcItem()
          item = tools.xbmcItem()
          info = item.info
          if listitem.p.string:
           info["Title"] = listitem.p.string.strip()
          else:
           info["Title"] = link.img["alt"]
          info["Thumb"] = "%s/%s" % (self.urls['base'], link.img["src"])
          #channelurl = re.search("/%s/(.*)" % type, link["href"]).group(1)
          channelurl = re.search("assets/images/%ss/([0-9]*?)-mini.jpg" % type, link.img["src"]).group(1)
          #infourl = "&info=%s" % urllib.quote(str(info))
          if type == "video":
           item.folder = False
           info["FileName"] = "%s?ch=Ziln&%s=%s" % (self.base, type, urllib.quote(channelurl))
           #info["FileName"] = self._geturl(channelurl)
          else:
           info["FileName"] = "%s?ch=Ziln&%s=%s" % (self.base, type, urllib.quote(channelurl))
          self.xbmcitems.items.append(item)
       self.xbmcitems.addall()
     else:
      sys.stderr.write("Search returned no results")
   else:
    sys.stderr.write("Couldn't find any programs")
  else:
   sys.stderr.write("Couldn't get page")

 def search(self):
  results = self.xbmcitems.search()
  if results:
   self.programmes("search", results)

 def play(self, index): #, info
  item = tools.xbmcItem(False)
  info = item.info
  info["Title"] = ""
  uri = self._geturl(index)
  info["FileName"] = uri
  item.path = uri
  self.xbmcitems.add(item, 1)
   
   # <jwplayer:hd.file>/assets/videos/airsidetv/files/720p/airnz_777_200s_lax_HD.mp4</jwplayer:hd.file>
   # <media:content bitrate="1800"  url="/assets/videos/airsidetv/files/520p/airnz_777_200s_lax_1000kb.mp4" type="video/x-mp4"/>


 def _geturl(self, index):
  page = webpage("%s/playlist/null/%s" % (self.urls['base'], index))
  if page.doc:
   soup = BeautifulStoneSoup(page.doc)
   #return "%s%s" % (self.urls['base'], soup.find('media:content')["url"])
   return "%s%s" % (self.urls['base'], urllib.quote(soup.find('media:content')["url"]))