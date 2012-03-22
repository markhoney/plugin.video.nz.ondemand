#/*
# *   Copyright (C) 2010 Mark Honeychurch
# *   based on the TVNZ Addon by JMarshall
# *
# *
# * This Program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2, or (at your option)
# * any later version.
# *
# * This Program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; see the file COPYING. If not, write to
# * the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# * http://www.gnu.org/copyleft/gpl.html
# *
# */

#ToDo:
# Fix sorting methods (they don't all seem to work properly)
# Scan HTML data for broadcast dates (in AtoZ, table view, etc)
# Find somewhere to add expiry dates?
# Add an option to show an advert before the program (I can't find the URLs for adverts at the moment)

#Useful list of categories
# http://ondemand.tv3.co.nz/Host/SQL/tabid/21/ctl/Login/portalid/0/Default.aspx

#XBMC Forum Thread
# http://forum.xbmc.org/showthread.php?t=37014


# Import external libraries

import os, cgi, sys, urlparse, urllib
import xbmcaddon, xbmcgui, xbmcplugin

import resources.tools as tools
import resources.config as config

#tools.initaddon()

settings = config.__settings__

# Decide what to run based on the plugin URL

params = cgi.parse_qs(urlparse.urlparse(sys.argv[2])[4])
if params:
 if params["ch"][0] == "TV3":
  from resources.channels.tv3 import tv3 as tv3class
  tv3 = tv3class()
  if params.get("folder", "") <> "":
   tv3.folderindex(params["folder"][0])
  elif params.get("cat", "") <> "":
   if params["cat"][0] == "tv":
    tv3.episodes(params["catid"][0], "tv3")
   elif params["cat"][0] == "atoz":
    tv3.atoz(params["catid"][0], "tv3")
   elif params["cat"][0] == "tv3":
    tv3.episodes(params["catid"][0], "tv3")
   elif params["cat"][0] == "c4tv":
    tv3.episodes(params["catid"][0], "c4tv")
   elif params["cat"][0] == "shows":
    tv3.show(urllib.unquote(params["catid"][0]), urllib.unquote(params["title"][0]), "tv3")
  elif params.get("id", "") <> "":
   tv3.play(params["id"][0], eval(urllib.unquote(params["info"][0])))
  else:
   if config.__settings__.getSetting('TV3_folders') == 'true':
    tv3.index()
   else:
    tv3.index()
 elif params["ch"][0] == "TVNZ":
  #import resources.channels.tvnz as tvnz
  #import resources.channels.tvnz
  #tvnz = resources.channels.tvnz.tvnz
  from resources.channels.tvnz import tvnz as tvnzclass
  tvnz = tvnzclass()
  #if params.get("type", "") == "":
  if not "type" in params:
   tvnz.index()
  else:
   if params["type"][0] == "shows":
    tvnz.episodes(params["id"][0])
    #tvnz.EPISODE_LIST(params["id"][0])
    #tools.addsorting(["label"], "episodes")
   elif params["type"][0] == "singleshow":
    tvnz.episodes(params["id"][0])
    #tvnz.SHOW_EPISODES(params["id"][0])
    #tools.addsorting(["date"], "episodes")
   elif params["type"][0] == "alphabetical":
    tvnz.show(params["id"][0])
    #tvnz.SHOW_LIST(params["id"][0])
    #tools.addsorting(["label"], "tvshows")
   elif params["type"][0] == "distributor":
    tvnz.SHOW_DISTRIBUTORS(params["id"][0])
    tools.addsorting(["label"], "tvshows")
   elif params["type"][0] == "search":
    tvnz.search()
    #tools.addsorting(["label"], "tvshows")
   elif params["type"][0] == "video":
    tvnz.play(params["id"][0], eval(urllib.unquote(params["info"][0])))
    #tvnz.RESOLVE(params["id"][0], eval(urllib.unquote(params["info"][0])))
 elif params["ch"][0] == "Ziln":
  from resources.channels.ziln import ziln as zilnclass
  ziln = zilnclass()
  if params.get("folder", "") <> "":
   if params["folder"][0] == "channels":
    ziln.programmes("channel", "")
   elif params["folder"][0] == "search":
    ziln.search()
  elif params.get("channel", "") <> "":
   ziln.programmes("video", params["channel"][0])
  elif params.get("video", "") <> "":
   ziln.play(params["video"][0]) #, eval(urllib.unquote(params["info"][0]))
  else:
   ziln.index()
 elif params["ch"][0] == "NZOnScreen":
  from resources.channels.nzonscreen import nzonscreen as nzonscreenclass
  nzonscreen = nzonscreenclass()
  if params.get("page", "") <> "":
   nzonscreen.page(urllib.unquote(params["filter"][0]), params["page"][0])
  elif params.get("filter", "") <> "":
   if params["filter"][0] == "search":
    nzonscreen.search()
   else:
    nzonscreen.index(urllib.unquote(params["filter"][0]))
  elif params.get("title", "") <> "":
   nzonscreen.play(params["title"][0])
  else:
   nzonscreen.index()
# elif params["ch"][0] == "iSKY":
#  import isky
#  isky.INDEX()
 else:
  sys.stderr.write("Invalid Channel ID")
else:
 channels = ["TV3", "TVNZ", "NZOnScreen"]
 if settings.getSetting('Ziln_hide') == "false":
  channels.append("Ziln")
 xbmc = tools.xbmcItems()
 for channel in channels:
  item = tools.xbmcItem()
  item.fanart = os.path.join('extrafanart', "%s.jpg" % channel)
  info = item.info
  info["Title"] = channel
  info["Thumb"] = os.path.join(settings.getAddonInfo('path'), "resources/images/%s.png" % channel)
  info["FileName"] = "%s?ch=%s" % (sys.argv[0], channel)
  xbmc.items.append(item)
# for item in xbmc.items:
  #sys.stderr.write(item.info["FileName"])
#  xbmc.message(item.info["FileName"])
 if settings.getSetting('Parliament_hide') == "false":
  from resources.channels.parliament import parliament as parliamentclass
  parliament = parliamentclass()
  xbmc.items.append(parliament.item())
 if settings.getSetting('Shine_hide') == "false":
  from resources.channels.shine import shine as shineclass
  shine = shineclass()
  xbmc.items.append(shine.item())
 xbmc.sorting.append('UNSORTED')
 xbmc.addall()
