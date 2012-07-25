import urllib, string, re, sys, time, os
from BeautifulSoup import BeautifulSoup, SoupStrainer, BeautifulStoneSoup

import xbmcgui, xbmcplugin, xbmcaddon

import resources.tools as tools
import resources.config as config
settings = config.__settings__
from resources.tools import webpage

class nzonscreen:
 def __init__(self):
  self.base = sys.argv[0]
  self.channel = "NZOnScreen"
  self.urls = dict()
  self.urls['base'] = 'http://www.nzonscreen.com'
  self.urls['json'] = '/html5/video_data/'
  self.xbmcitems = tools.xbmcItems()
  self.xbmcitems.fanart = os.path.join('extrafanart', self.channel + '.jpg')

 def url(self, folder):
  u = self.urls
  return "/".join((u['base'], u['content'], folder, u['page']))

 def _xml(self, doc):
  try:
   document = minidom.parseString(doc)
  except:
   pass
  else:
   if document:
    return document.documentElement
  sys.stderr.write("No XML Data")
  return False

 def index(self, filter = "/explore/"):
  filterarray = filter.strip('/').split('/')
  filterlevel = len(filterarray)
  url = self.urls['base'] + filter
  #sys.stderr.write("URL: " + url)
  #sys.stderr.write('explore_filter_%s' % str(filterlevel))
  page = webpage(url, 'chrome', 'nzos_html5=true')
  #page = webpage(self.urls['base'])
  if page.doc:
   #resources.tools.gethtmlpage("http://www.nzonscreen.com/html5/opt_in", "chrome", 1) # Get a cookie for this session to enable the HTML5 video tag
   div_tag = SoupStrainer('div')
   html_divtag = BeautifulSoup(page.doc, parseOnlyThese = div_tag)
   sections = html_divtag.find(attrs={'id' : 'explore_filter_%s' % str(filterlevel)})
   if sections:
    links = sections.findAll('a')
    if len(links) > 0:
     for link in links:
 #     if link.string:
 #     sys.stderr.write(link.contents[0].string)
      item = tools.xbmcItem()
      info = item.info
      info["FileName"] = "%s?ch=%s&filter=%s" % (self.base, self.channel, urllib.quote(link["href"]))
      #info["Title"] = link.contents[0].string.strip()
      if link.string:
       info["Title"] = link.string.strip()
      else:
       filterarray = link["href"].split('/')
       info["Title"] = filterarray[len(filterarray) - 1].capitalize()
 #     info["Thumb"] = 
      self.xbmcitems.items.append(item)
     if filterlevel == 1:
      item = tools.xbmcItem()
      info = item.info
      info["FileName"] = "%s?ch=%s&filter=search" % (self.base, self.channel)
      info["Title"] = "Search"
      self.xbmcitems.items.append(item)
    else:
 #    if filterarray[filterlevel] == 
     nav = html_divtag.find(attrs={'class' : 'nav_pagination'})
     if nav:
      pages = nav.findAll('a')
      if pages:
       for page in pages:
        if page.string:
         lastpage = page.string.strip()
         #url = page['href']
       for i in range(1, int(lastpage)):
        item = tools.xbmcItem()
        info = item.info
        info["FileName"] = "%s?ch=%s&filter=%s&page=%s" % (self.base, self.channel, urllib.quote(filter), str(i))
        info["Title"] = 'Page %s' % str(i)
        self.xbmcitems.items.append(item)
    self.xbmcitems.addall()
   else:
    sys.stderr.write("Couldn't find menu")
  else:
   sys.stderr.write("Couldn't get page")

 def page(self, filter, page):
  url = "%s%s?page=%s" % (self.urls['base'], filter, page)
  page = webpage(url, 'chrome', 'nzos_html5=true')
  if page.doc:
   div_tag = SoupStrainer('div')
   html_divtag = BeautifulSoup(page.doc, parseOnlyThese = div_tag)
   results = html_divtag.find(attrs={'id' : 'filter_result_set'})
   if results:
    rows = results.findAll('tr')
    if len(rows) > 0:
     for row in rows:
      cells = row.findAll('td')
      if len(cells) > 0:
       item = tools.xbmcItem()
       info = item.info
       item.units = "MB"
       for cell in cells:
        if cell['class'] == 'image':
         info['Thumb'] = "%s%s" % (self.urls['base'], cell.div.div.a.img['src'])
         title = re.search("/title/(.*)", cell.a['href'])
         if title:
          info['FileName'] = self._geturl(title.group(1), False)
        elif cell['class'] == 'title_link title':
         info['Title'] = item.unescape(cell.a.contents[0])
        elif cell['class'] == 'year':
         pass
        elif cell['class'] == 'category':
         pass
        elif cell['class'] == 'director':
         pass
        elif cell['class'] == 'added':
         info["Date"] = tools.xbmcdate(cell.contents[0], ".")
       if 'FileName' in info:
        self.xbmcitems.items.append(item)
     self.xbmcitems.addall()
    else:
     sys.stderr.write("No rows found")
   else:
    sys.stderr.write("Couldn't find items")
  else:
   sys.stderr.write("Couldn't get page")

 def search(self):
  import xbmc
  keyboard = xbmc.Keyboard("", "Search for a Video")
  #keyboard.setHiddenInput(False)
  keyboard.doModal()
  if keyboard.isConfirmed():
   self.page("search", keyboard.getText())

 def play(self, title): #, info
  item = tools.xbmcItem(False)
  info = item.info
  info["Title"] = ""
  info["FileName"] = self._geturl(title, True)
  item.path = info["FileName"]
  self.xbmcitems.add(item, 1)

 def bitrates(self, title): #, info
  #self.xbmcitems.addurls(self._videourls(title))
  for bitrate, url in self._videourls(title).iteritems():
   item = tools.xbmcItem()
   info = item.info
   info['Title'] = str(bitrate) + 'MB'
   info['FileName'] = item.stack(url)
   self.xbmcitems.items.append(item)
  self.xbmcitems.addall()

 def _geturl(self, title, play):
  if settings.getSetting('%s_quality_play' % self.channel) == 'true':
   return "%s?ch=%s&bitrates=%s" % (self.base, self.channel, title) #self.xbmcitems.addurls(self._videourls(title))
  elif play:
   return self.xbmcitems.url(self._videourls(title), settings.getSetting('%s_quality' % self.channel))
  else:
   return "%s?ch=%s&title=%s" % (self.base, self.channel, title)

 def _videourls(self, title):
  url = "%s%s%s" % (self.urls['base'], self.urls['json'], title)
  page = webpage(url)
  if page.doc:
   import json
   videos = json.loads(page.doc)
   allurls = dict()
   returnurls = dict()
   #bitrates = list()
   filesizes = dict()
   for name, value in videos[0].iteritems():
    if name[-4:] == '_res':
     #bitrates.append(name[:-4])
     bitrate = name[:-4]
     allurls[bitrate] = list()
     filesizes[bitrate] = 0
   for video in videos:
    for bitrate, temp in allurls.iteritems():
     #print bitrate
     allurls[bitrate].append(video[bitrate + '_res'])
     filesizes[bitrate] = filesizes[bitrate] + video[bitrate + '_res_mb']
   for bitrate, urls in allurls.iteritems():
    #returnurls[str(filesizes[bitrate])] = urls
    returnurls[filesizes[bitrate]] = urls
   return returnurls
#   for bitrate, urls in allurls.iteritems():
#    item.urls[bitrate] = item.stack(urls)
#   uri = item.stack(allurls['hi_res'])
#   return uri
