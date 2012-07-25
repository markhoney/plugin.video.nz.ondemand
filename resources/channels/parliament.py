# http://inthehouse.co.nz/

import os, sys, xbmcaddon, resources.tools, resources.config
from datetime import date

import resources.tools as tools
import resources.config as config
settings = config.__settings__


class parliament:
 def item(self):
  self.channel = 'Parliament'
  item = tools.xbmcItem()
  item.fanart = os.path.join('extrafanart', self.channel + '.jpg')
  info = item.info
  info["Title"] = 'Parliament TV (Live Stream)'
  info["Thumb"] = os.path.join(settings.getAddonInfo('path'), "resources/images/%s.png" % self.channel)
  info["Plot"] = "Parliament TV provides live broadcasts from the House of Representatives. Question time is replayed each day at 6pm and 10pm."
  info["Date"] = date.today().strftime("%d.%m.%Y")
  for quality in [56, 128, 384]:
   item.urls[quality] = "%s%s" % ("mms://wms-parliament.harmonycdn.net/parlserv-house", str(quality))
  for quality in [512]:
   item.urls[quality] = "%s%s%s" % ("rtsp://Qts1.ptv.parliament.nz/ptv-", quality, ".sdp")
#  quality = '384'
#  if settings.getSetting('%s_stream' % self.channel) == "Apple Quicktime":
#   quality = '512'
#  if settings.getSetting('%s_quality' % self.channel) == "Low":
#   quality = '56'
#  elif settings.getSetting('%s_quality' % self.channel) == "Medium":
#   quality = '128'
#  info["FileName"] = "%s%s" % ("mms://wms-parliament.harmonycdn.net/parlserv-house", quality)
#  if settings.getSetting('%s_stream' % self.channel) == "Apple Quicktime":
#   info["FileName"] = "%s%s%s" % ("rtsp://Qts1.ptv.parliament.nz/ptv-", quality, ".sdp")
  return item