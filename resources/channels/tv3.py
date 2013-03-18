# 3 News
# mms://content.mediaworks.co.nz/tv/News/TOPSTORIES.300k

import urllib, re, sys, time

from BeautifulSoup import BeautifulSoup, SoupStrainer

import resources.tools as tools
import resources.config as config
settings = config.__settings__
language = config.__language__
from resources.tools import webpage

class tv3:
 def __init__(self):
  self.base = sys.argv[0]
  self.channel = "TV3"
  self.channels = {"TV3": dict(), "Four": dict()}
  self.channels['TV3']['base'] = 'http://www.tv3.co.nz'
  self.channels['TV3']['ondemand'] = 'OnDemand'
  self.channels['TV3']['shows'] = 'Shows'
  self.channels['TV3']['rtmp'] = 'tv3'
  self.channels['Four']['base'] = 'http://www.four.co.nz'
  self.channels['Four']['ondemand'] = 'TV/OnDemand'
  self.channels['Four']['shows'] = 'TV/Shows'
  self.channels['Four']['rtmp'] = 'c4'
  self.urls = dict()
  self.urls['categories'] = ['Must Watch', 'Expiring Soon', 'Recently Added']
  # TitleAZ
  self.urls['base'] = 'http://www.tv3.co.nz'
  self.urls['base1'] = 'http://ondemand'
  self.urls['base2'] = 'co.nz'
  self.urls['rtmp1'] = 'rtmpe://nzcontent.mediaworks.co.nz:80'
  self.urls['rtmp2'] = '_definst_/mp4:'
  self.urls['flash1'] = 'rtmpe://flashcontent.mediaworks.co.nz:80'
  self.urls['flash2'] = 'mp4:'
  self.urls['news1'] = 'rtmpe://strm.3news.co.nz'
  self.urls['http1'] = 'http://flash.mediaworks.co.nz'
  self.urls['http2'] = 'streams/_definst_//'
  self.urls['video1'] = 'tabid'
  self.urls['video2'] = 'articleID'
  self.urls['video3'] = 'MCat'
  self.urls['video4'] = 'Default.aspx'
  self.urls['feedburner_re'] = '//feedproxy\.google\.com/'
  self.urls['cat'] = '/default404.aspx?tabid='
  self.urls['cat_re'] = '/default404\.aspx\?tabid='
  self.urls['img_re'] = '\.ondemand\.tv3\.co\.nz/ondemand/AM/'
  self.urls['img_re2'] = '\.ondemand\.tv3\.co\.nz/Portals/0-Articles/'
  self.xbmcitems = tools.xbmcItems(self.channel)
  self.prefetch = self.xbmcitems.booleansetting('%s_prefetch' % self.channel)

 def index(self, fake = True):
  for folder in self.channels.keys():
   item = tools.xbmcItem()
   item.info["Title"] = folder
   item.info["FileName"] = "%s?ch=TV3&channel=%s" % (self.base, folder)
   self.xbmcitems.items.append(item)
  self.xbmcitems.addall()

 def channelindex(self, channel): #Create second level folder for the hierarchy view, only showing items for the selected top level folder
  for category in self.urls['categories']:
   item = tools.xbmcItem()
   item.info["Title"] = category
   item.info["FileName"] = "%s?ch=TV3&channel=%s&cat=%s" % (self.base, channel, category.replace(" ", ""))
   self.xbmcitems.items.append(item)
  item = tools.xbmcItem()
  item.info["Title"] = language(30055)
  item.info["FileName"] = "%s?ch=TV3&channel=%s&cat=%s" % (self.base, channel, "shows")
  self.xbmcitems.items.append(item)
  item = tools.xbmcItem()
  item.info["Title"] = language(30065)
  item.info["FileName"] = "%s?ch=TV3&channel=%s&cat=%s" % (self.base, channel, "search")
  self.xbmcitems.items.append(item)
  self.xbmcitems.addall()

 def shows(self, channel): #Create a second level list of TV Shows from a TV3 webpage
  #doc = resources.tools.gethtmlpage("%s/Shows/tabid/64/Default.aspx" % ("http://www.tv3.co.nz")) #Get our HTML page with a list of video categories
  #doc = resources.tools.gethtmlpage("%s/Shows.aspx" % ("http://www.tv3.co.nz")) #Get our HTML page with a list of video categories
  page = webpage("%s/%s/%s" % (self.channels[channel]['base'], self.channels[channel]['ondemand'], "TitleAZ.aspx"))
  if page.doc:
   html_divtag = BeautifulSoup(page.doc)
   showsdiv = html_divtag.findAll('div', attrs = {"class": "grid_2"})
   if len(showsdiv) > 0:
    for show in showsdiv:
     item = tools.xbmcItem()
     title = show.find('p').find('a')
     if title:
      if title.string:
       if title['href'][len('http://www.'):len('http://www.') + 3] == channel[0:3].lower():
        item.info["Title"] = title.string.strip()
        image = show.find("img")
        if image:
         item.info["Thumb"] = image['src']
        item.info["FileName"] = "%s?ch=TV3&channel=%s&cat=%s&title=%s" % (self.base, channel, "show", urllib.quote(item.info["Title"].replace(" ", "")))
        self.xbmcitems.items.append(item)
    self.xbmcitems.addall()
   else:
    sys.stderr.write("showsindex: Couldn't find any videos in list")
  else:
   sys.stderr.write("showsindex: Couldn't get index webpage")


 def episodes(self, channel, cat): #Show video items from a normal TV3 webpage
  page = webpage("%s/%s/%s" % (self.channels[channel]['base'], self.channels[channel]['ondemand'], cat + ".aspx"))
  if page.doc:
   a_tag=SoupStrainer('div')
   html_atag = BeautifulSoup(page.doc, parseOnlyThese = a_tag)
   programs = html_atag.findAll(attrs={"class": "grid_2"})
   if len(programs) > 0:
    for soup in programs:
     item = self._itemdiv(soup, channel)
     if item:
      self.xbmcitems.items.append(item)
      if len(item.urls) > 0:
       if self.prefetch:
        self.xbmcitems.add(len(programs))
    if self.prefetch:
     self.xbmcitems.sort()
    else:
     self.xbmcitems.addall()
   else:
    sys.stderr.write("episodes: Couldn't find any videos")
  else:
   sys.stderr.write("episodes: Couldn't get videos webpage")

 def show(self, channel, title): #Show video items from a TV Show style TV3 webpage
  #page = webpage("%s/%s/%s" % (self.channels[channel]['base'], self.channels[channel]['shows'], title + ".aspx"))
  page = webpage("%s/%s/%s/%s" % (self.channels[channel]['base'], self.channels[channel]['shows'], title, "TVOnDemand.aspx"))
  if page.doc:
   div_tag = SoupStrainer('div')
   html_divtag = BeautifulSoup(page.doc, parseOnlyThese = div_tag)
   programblock = html_divtag.find(attrs={"class": "grid_8"})
   if programblock:
    #print programblock
    programs = programblock.findAll('div', attrs={"class": "grid_4"})
    if len(programs) > 0:
     for soup in programs:
      print soup
      self.xbmcitems.items.append(self._itemshow(channel, title, soup))
     self.xbmcitems.addall()
   else:
    sys.stderr.write("show: Couldn't find video list")
  else:
   sys.stderr.write("show: Couldn't get index webpage")

 def atoz(self, catid, provider): #Show video items from an AtoZ style TV3 webpage
  page = webpage("%s%s%s" % (self._base_url("tv3"), self.urls["cat"], catid))
  if page.doc:
   a_tag=SoupStrainer('div')
   html_atag = BeautifulSoup(page.doc, parseOnlyThese = a_tag)
   programs = html_atag.findAll(attrs={"class": "wideArticles"})
   if len(programs) > 0:
    for soup in programs:
     item = self._itematoz(soup, provider)
     self.xbmcitems.items.append(item)
     if len(item.urls) > 0:
      if self.prefetch:
       self.xbmcitems.add(len(programs))
    if self.prefetch:
     self.xbmcitems.sort()
    else:
     self.xbmcitems.addall()
   else:
    sys.stderr.write("atoz: Couldn't find any videos")
  else:
   sys.stderr.write("atoz: Couldn't get videos webpage")

 def search(self):
  results = self.xbmcitems.search()
  if results:
   self._search(results, "58")

 def _search(self, searchterm, catid): #Show video items from a normal TV3 webpage
  page = webpage("%s/search/tabid/%s/Default.aspx?amq=%s" % (self._base_url('tv3'), catid, searchterm.replace(" ", "+")))
  if page.doc:
   a_tag=SoupStrainer('div')
   html_atag = BeautifulSoup(page.doc, parseOnlyThese = a_tag)
   programs = html_atag.findAll(attrs={"class": "results"})
   if len(programs) > 0:
    for soup in programs:
     self.xbmcitems.items.append(self._itemsearch(soup, "tv3"))
     self.xbmcitems.items.append(self._itemsearch(soup, "four"))
    self.xbmcitems.addall()
   else:
    sys.stderr.write("_search: Couldn't find any videos")
  else:
   sys.stderr.write("_search: Couldn't get videos webpage")

 def _itemsearch(self, soup, provider): # Scrape items from a table-style HTML page
  baseurl = self._base_url(provider)
  item = tools.xbmcItem()
  title = soup.find("div", attrs={"class": 'catTitle'})
  if title:
   item.info["TVShowTitle"] = title.a.string.strip()
   href = re.match("%s/(.*?)/%s/([0-9]+)/%s/([0-9]+)/%s/([0-9]+)/" % (baseurl, self.urls["video1"], self.urls["video2"], self.urls["video3"]), title.a['href'])
   if href:
    image = soup.find("img")
    if image:
     item.info["Thumb"] = image['src']
    ep = soup.find("div", attrs={"class": 'epTitle'})
    if ep:
     if ep.a:
      item.info.update(self._seasonepisode(ep.a))
    date = soup.find("div", attrs={"class": 'epDate'})
  #  if date:
  #   sys.stderr.write(date.span[1].string.strip())
    item.titleplot()
    if self.prefetch:
     item.urls = self._geturls("%s,%s,%s,%s" % (href.group(1), href.group(2), href.group(3), href.group(4)), provider)
    else:
     item.playable = True
     item.info["FileName"] = "%s?ch=TV3&id=%s&provider=%s&info=%s" % (self.base, "%s,%s,%s,%s" % (href.group(1), href.group(2), href.group(3), href.group(4)), provider, item.infoencode())
    return item
   else:
    sys.stderr.write("_itemsearch: No href")
  else:
   sys.stderr.write("_itemsearch: No title")

 def _itemdiv(self, soup, channel): #Scrape items from a div-style HTML page
  baseurl = self.channels[channel]['base']
  item = tools.xbmcItem()
  #item.info["Studio"] = provider
  link = soup.find("a")
  if link:
   href = re.match("%s/(.*?)/%s/([0-9]+)/%s/([0-9]+)/%s/([0-9]+)/" % (baseurl, self.urls["video1"], self.urls["video2"], self.urls["video3"]), link['href'])
   if href:
    showname = soup.find("div")
    if showname:
     title = showname.string.strip()
     if title != "":
      item.info["TVShowTitle"] = title
      image = soup.find("img")
      if image:
       item.info["Thumb"] = image['src']
      se = soup.find("p")
      if se:
       item.info.update(self._seasonepisode(se))
      item.titleplot()
      if self.prefetch:
       item.urls = self._geturls("%s,%s,%s,%s" % (href.group(1), href.group(2), href.group(3), href.group(4)), channel)
      else:
       item.playable = True
       item.info["FileName"] = "%s?ch=TV3&channel=%s&id=%s&info=%s" % (self.base, channel, "%s,%s,%s,%s" % (href.group(1), href.group(2), href.group(3), href.group(4)), item.infoencode())
      return item
     else:
      sys.stderr.write("_itemdiv: No title")
    else:
     sys.stderr.write("_itemdiv: No link.string")
   else:
    sys.stderr.write("_itemdiv: No href")
  else:
   sys.stderr.write("_itemdiv: No link")

 def _itemshow(self, channel, title, soup): #Scrape items from a show-style HTML page
  baseurl = self.channels[channel]['base']
  item = tools.xbmcItem()
  link = soup.find("a")
  if link:
   print link
   if link.has_key('href'):
    print link['href']
    print "%s/(.*?)/%s/([0-9]+)/%s/([0-9]+)/%s/([0-9]+)/" % (baseurl, self.urls["video1"], self.urls["video2"], self.urls["video3"])
    href = re.match("%s/(.*?)/%s/([0-9]+)/%s/([0-9]+)/%s/([0-9]+)/" % (baseurl, self.urls["video1"], self.urls["video2"], self.urls["video3"]), link['href'])
    if href:
     title = showname.strip()
     if title != "":
      item.info["TVShowTitle"] = title
      image = soup.find("img")
      if image:
       item.info["Thumb"] = image['src']
      se = soup.find("h4")
      if se:
       sea = se.find('a')
       if sea:
        item.info.update(self._seasonepisode(sea).string.strip())
      plot = soup.find("p")
      if plot:
       if plot.string:
        item.info["PlotOutline"] = plot.string.strip()
      item.titleplot()
      if self.prefetch:
       item.urls = self._geturls("%s,%s,%s,%s" % (href.group(1), href.group(2), href.group(3), href.group(4)), channel)
      else:
       item.playable = True
       item.info["FileName"] = "%s?ch=TV3&channel=%s&id=%s&info=%s" % (self.base, channel, "%s,%s,%s,%s" % (href.group(1), href.group(2), href.group(3), href.group(4)), item.infoencode())
      return item
    else:
     sys.stderr.write("_itemshow: No title")
   else:
    sys.stderr.write("_itemshow: No href")
  else:
   sys.stderr.write("_itemshow: No link")

 def _itemtable(self, soup, provider, title): #Scrape items from a table-style HTML page
  item = tools.xbmcItem()
  link = soup.find('a')
  if link:
   if link.string:
    plot = link.string.strip()
    if plot != "":
     item.info["PlotOutline"] = plot
     item.info["TVShowTitle"] = title
     item.info.update(self._seasonepisode(link))
     item.titleplot()
     href = re.search("%s/(.*?)/%s/([0-9]+)/%s/([0-9]+)/%s/([0-9]+)/" % (self._base_url("tv3"), self.urls["video1"], self.urls["video2"], self.urls["video3"]), link['href'])
     if href:
      if self.prefetch:
       item.urls = self._geturls("%s,%s,%s,%s" % (href.group(1), href.group(2), href.group(3), href.group(4)), provider)
      else:
       item.playable = True
       item.info["FileName"] = "%s?ch=TV3&id=%s&provider=%s&info=%s" % (self.base, "%s,%s,%s,%s" % (href.group(1), href.group(2), href.group(3), href.group(4)), provider, item.infoencode())
     return item
    else:
     sys.stderr.write("_itemtable: No plot")
   else:
    sys.stderr.write("_itemtable: No link.string")
  else:
   sys.stderr.write("_itemtable: No link")

 def _itematoz(self, soup, provider): #Scrape items from an AtoZ-style HTML page
  baseurl = self._base_url(provider)
  item = tools.xbmcItem()
  if soup.find('h5'):
   link = soup.h5.find("a", attrs={"href": re.compile(baseurl)})
   if link:
    infoitems = {}
    href = re.match("%s/(.*?)/%s/([0-9]+)/%s/([0-9]+)/%s/([0-9]+)/" % (baseurl, self.urls["video1"], self.urls["video2"], self.urls["video3"]), link['href'])
    if href:
     if link.string:
      title = link.string.strip()
      if title != "":
       item.info["TVShowTitle"] = title
       image = soup.find("img", attrs={"src": re.compile(self.urls["IMG_RE2"]), "title": True})
       if image:
        item.info["Thumb"] = image['src']
       item.info.update(self._seasonepisode(soup.contents[4]))
       item.titleplot()
       plot = soup.find("span", attrs={"class": "lite"})
       if plot.string:
        cleanedplot = plot.string.strip()
        if cleanedplot:
         item.info["Plot"] = item.unescape(cleanedplot)
       if self.prefetch:
        item.urls = self._geturls("%s,%s,%s,%s" % (href.group(1), href.group(2), href.group(3), href.group(4)), channel)
       else:
        item.playable = True
        item.info["FileName"] = "%s?ch=%s&id=%s&provider=%s&info=%s" % (self.base, self.channel, "%s,%s,%s,%s" % (href.group(1), href.group(2), href.group(3), href.group(4)), provider, item.infoencode())
       if "FileName" in item.info or len(item.urls) > 0:
        return item
      else:
       sys.stderr.write("_itematoz: No title")
     else:
      sys.stderr.write("_itematoz: No link.string")
    else:
     sys.stderr.write("_itematoz: No href")
   else:
    sys.stderr.write("_itematoz: No link")
  else:
   sys.stderr.write("_itematoz: No h5")

 def play(self, id, channel, encodedinfo):
  item = tools.xbmcItem()
  item.infodecode(encodedinfo)
  item.fanart = self.xbmcitems.fanart
  item.urls = self._geturls(id, channel)
  self.xbmcitems.resolve(item, self.channel)

 def _geturls(self, id, channel): #Scrape a page for a given OnDemand video and build an RTMP URL from the info in the page, then play the URL
  urls = dict()
  ids = id.split(",")
  if len(ids) == 4:
   pageUrl = "%s/%s/%s/%s/%s/%s/%s/%s/%s" % (self.channels[channel]['base'], ids[0], self.urls["video1"], ids[1], self.urls["video2"], ids[2], self.urls["video3"], ids[3], self.urls["video4"])
   page = webpage(pageUrl)
  else:
   page = webpage(id) # Huh? - I guess this is feeding a full URL via the id variable
  if page.doc:
   videoid = re.search('var video ="/(.*?)/([0-9A-Z\-]+)/(.*?)";', page.doc)
   if videoid:
    #videoplayer = re.search('swfobject.embedSWF\("(http://static.mediaworks.co.nz/(.*?).swf)', page.doc)
    videoplayer = 'http://static.mediaworks.co.nz/video/jw/5.10/df.swf'
    if videoplayer:
     rnd = ""
     auth = re.search('random_num = "([0-9]+)";', page.doc)
     if auth:
      rnd = "?rnd=" + auth.group(1)
     swfverify = ' swfVfy=true swfUrl=%s%s pageUrl=%s' % (videoplayer, rnd, pageUrl)
     realstudio = 'tv3'
     site = re.search("var pageloc='(TV-)?(.*?)-", page.doc)
     if site:
      realstudio = site.group(2).lower()
     playlist = list()
     qualities = [330]
     #if re.search('flashvars.sevenHundred = "yes";', page.doc):
     qualities.append(700)
     #if re.search('flashvars.fifteenHundred = "yes";', page.doc):
     #qualities.append(1500)
     #if not re.search('flashvars.highEnd = "true";', page.doc): # flashvars.highEnd = "true";//true removes 56K option
     # qualities.append(56)
     geo = re.search('var geo= "(.*?)";', page.doc)
     if geo:
      if geo.group(1) == 'geo':
       for quality in qualities:
        urls[quality] = '%s/%s/%s/%s/%s/%s_%sK.mp4' % (self.urls["rtmp1"], self.channels[channel]['rtmp'], self.urls["rtmp2"], videoid.group(1), videoid.group(2), urllib.quote(videoid.group(3)), quality) + swfverify
      elif geo.group(1) == 'str':
       for quality in qualities:
        app = ' app=tv3/mp4:transfer' # + videoid.group(1)
        tcurl = ' tcUrl=rtmpe://flashcontent.mediaworks.co.nz:80/'
        playpath = ' playpath=%s/%s_%sK' % (videoid.group(2), videoid.group(3), quality)
        urls[quality] = '%s/%s/%s/%s/%s/%s_%sK' % (self.urls['news1'], "vod", self.urls["rtmp2"] + "3news", videoid.group(1), urllib.quote(videoid.group(2)), urllib.quote(videoid.group(3)), quality) + ' pageUrl=' + pageUrl
        #urls[quality] = '%s/%s/%s%s/%s/%s_%sK' % (self.urls["flash1"], self._rtmpchannel(realstudio), self.urls["flash2"], videoid.group(1), urllib.quote(videoid.group(2)), urllib.quote(videoid.group(3)), quality) + ' pageUrl=' + pageUrl
        #urls[quality] = '%s/%s/%s%s/%s/%s_%sK' % (self.urls["flash1"], self._rtmpchannel(realstudio), self.urls["flash2"], videoid.group(1), videoid.group(2), urllib.quote(videoid.group(3)), quality)
        #urls[quality] = 'rtmpe://flashcontent.mediaworks.co.nz:80/tv3/mp4:transfer'
        #urls[quality] = '%s/%s/%s%s/%s/%s_%sK' % (self.urls["flash1"], self._rtmpchannel(realstudio), self.urls["flash2"], videoid.group(1), videoid.group(2), urllib.quote(videoid.group(3)), quality) # + " swfVfy=true swfUrl=http://m1.2mdn.net/879366/DartShellPlayer9_14_39_2.swf"
        #urls[quality] = '%s/%s/%s%s/%s/%s_%sK' % (self.urls["flash1"], self._rtmpchannel(realstudio), self.urls["flash2"], videoid.group(1), videoid.group(2), urllib.quote(videoid.group(3)), quality) + tcurl + app + playpath + swfverify
        #urls[quality] = '%s/%s/%s%s/%s/%s_%sK' % (self.urls["flash1"], self._rtmpchannel(realstudio), self.urls["flash2"], videoid.group(1), videoid.group(2), urllib.quote(videoid.group(3)), quality) + playpath + swfverify
        #urls[quality] = '%s/%s/%s%s/%s/%s_%sK' % (self.urls["flash1"], self._rtmpchannel(realstudio), self.urls["flash2"], videoid.group(1), videoid.group(2), urllib.quote(videoid.group(3)), quality) + swfverify
    #  elif geo.group(1) == 'no':
    #   for quality in qualities:
    #    urls[quality] = '%s/%s/%s%s/%s/%s_%s.%s' % (self.urls["http1"], "four", self.urls["http2"], videoid.group(1), videoid.group(2), urllib.quote(videoid.group(3)), quality, "mp4")
    else:
     sys.stderr.write("_geturls: No videoplayer")
   else:
    sys.stderr.write("_geturls: No videoid")
  else:
   sys.stderr.write("_geturls: No page.doc")
  return urls

 def _seasonepisode(self, se): #Search a tag for season and episode numbers. If there's an episode and no season, assume that it's season 1
  if se:
   info = dict()
   info["PlotOutline"] = se.string.strip()
   season = re.search("(Cycle|Season) ([0-9]+)", se.string)
   seasonfound = 0
   if season:
    info["Season"] = int(season.group(2))
    seasonfound = 1
   episode = re.search("Ep(|isode) ([0-9]+)", se.string)
   if episode:
    info["Episode"] = int(episode.group(2))
    if not seasonfound:
     info["Season"] = 1
   return info

 def _dateduration(self, ad): #Search a tag for aired date and video duration
  if ad:
   info = dict()
   aired = re.search("([0-9]{2}/[0-9]{2}/[0-9]{2})", ad.contents[1])
   if aired:
    info["Premiered"] = tools.xbmcdate(aired.group(1))
    info["Date"] = info["Premiered"]
   duration = re.search("\(([0-9]+:[0-9]{2})\)", ad.contents[1])
   if duration:
    info["Duration"] = time.strftime("%M", time.strptime(duration.group(1), "%M:%S"))
   return info

 def _base_url(self, provider): #Build a base website URL for a given site (four or tv3)
  return "%s.%s.%s" % (self.urls['base1'], provider, self.urls['base2'])

 def _rtmpchannel(self, provider):
  if provider == "four":
   return "c4"
  return provider