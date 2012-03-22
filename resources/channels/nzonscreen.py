import urllib, string, re, sys, time, os
from BeautifulSoup import BeautifulSoup, SoupStrainer, BeautifulStoneSoup

import xbmcgui, xbmcplugin, xbmcaddon

import resources.tools as tools
import resources.config as config
from resources.tools import webpage


nzonscreen_urls = dict()
nzonscreen_urls["NZONSCREEN"] = 'http://www.nzonscreen.com'
nzonscreen_urls["Fanart"] = 'extrafanart/NZOnScreen.jpg'

class nzonscreen:
 def __init__(self):
  self.base = sys.argv[0]
  self.channel = "NZOnScreen"
  self.bitrates = ['hi_res', 'lo_res']
  
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
      info["FileName"] = "%s?ch=NZOnScreen&filter=%s" % (sys.argv[0], urllib.quote(link["href"]))
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
      info["FileName"] = "%s?ch=NZOnScreen&filter=search" % (sys.argv[0])
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
         url = page['href']
       for i in range(1, int(lastpage)):
        item = tools.xbmcItem()
        info = item.info
        info["FileName"] = "%s?ch=NZOnScreen&filter=%s&page=%s" % (sys.argv[0], urllib.quote(filter), str(i))
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
       item = tools.xbmcItem(False)
       info = item.info
       for cell in cells:
        if cell['class'] == 'image':
         info['Thumb'] = "%s%s" % (nzonscreen_urls["NZONSCREEN"], cell.div.div.a.img['src'])
         title = re.search("/title/(.*)", cell.a['href'])
         if title:
          info['FileName'] = "%s?ch=NZOnScreen&title=%s" % (sys.argv[0], title.group(1))
        elif cell['class'] == 'title_link title':
         info['Title'] = tools.unescape(cell.a.contents[0])
        elif cell['class'] == 'year':
         pass
        elif cell['class'] == 'category':
         pass
        elif cell['class'] == 'director':
         pass
        elif cell['class'] == 'added':
         info["Date"] = tools.xbmcdate(cell.contents[0], ".")
       self.xbmcitems.items.append(item)
     self.xbmcitems.addall()

 def search(self):
  import xbmc
  keyboard = xbmc.Keyboard("", "Search for a Video")
  #keyboard.setHiddenInput(False)
  keyboard.doModal()
  if keyboard.isConfirmed():
   PROGRAMMES("search", keyboard.getText())

 def play(self, title): #, info
  url = "%s%s%s" % (self.urls['base'], self.urls['json'], title)
  page = webpage(url)
  if page.doc:
   import json
   videos = json.loads(page.doc)
   item = tools.xbmcItem(False)
   info = item.info
   info['Title'] = title
   allurls = dict()
   for bitrate in self.bitrates:
    allurls[bitrate] = list()
   for video in videos:
    for bitrate in self.bitrates:
     allurls[bitrate].append(video[bitrate])
   for bitrate, urls in allurls.iteritems():
    item.urls[bitrate] = item.stack(urls)
   info["Thumb"] = self.urls['base'] + videos[0]['pre_roll_path']
   uri = item.urls['hi_res']
   info["FileName"] = uri
   item.path = uri
   self.xbmcitems.add(item, 1)
