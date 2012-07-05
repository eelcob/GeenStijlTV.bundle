####################################################################################################
NAME 			= L('Title')
PLUGIN_PREFIX  	= "/video/geenstijltv"

ART 			= 'art-default.png'
ICON 			= 'icon-default.png'
ICON_MORE		= 'icon-next.png'
ICON_ARCHIVE 	= "icon-archive.png"
ICON_RECENT 	= "icon-recent.png"
ICON_ZOEKEN 	= "icon-zoeken.png"

# URLS
URL_ROOT_URI       = "http://www.geenstijl.tv/"
URL_ARCHIEF        = URL_ROOT_URI + "archief.html"
URL_ZOEKEN         = URL_ROOT_URI + "fastsearch?query="

# Regexes
VIDLINK = Regex('videourl: \'(.*?)\',')
VIDLINK2 = Regex('xgstvplayer\(\'(.*?)\',')
VIDLINK3 = Regex('gstvplayer\(\'[0-9]+\', \'(.*?)\',')
THUMBLINK = Regex('GSvideo.preview = \'(.*?)\';')

####################################################################################################
def Start():
	Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
	Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
	
	ObjectContainer.title1 = NAME
	ObjectContainer.view_group = 'List'
	ObjectContainer.art = R(ART)  
	
	VideoClipObject.thumb = R(ICON)

	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:8.0) Gecko/20100101 Firefox/8.0'

####################################################################################################
def MainMenu():
	oc = ObjectContainer()
	
	oc.add(DirectoryObject(key = Callback(HomePage, pageUrl=URL_ROOT_URI, title=L('LastFive')), title=L('LastFive'), thumb=R(ICON_RECENT)))
	oc.add(DirectoryObject(key = Callback(ArchivePage, pageUrl=URL_ARCHIEF, title=L('Archive')), title=L('Archive'), thumb=R(ICON_ARCHIVE)))
	oc.add(InputDirectoryObject(key = Callback(SearchPage, pageUrl=URL_ZOEKEN, title=L('Search')), title=L('Search'), thumb=R(ICON_ZOEKEN), prompt=L('Search')))

	return oc

####################################################################################################
def HomePage(pageUrl, title):

	oc = ObjectContainer(title2=title)
	oc.view_group = 'Details'

	for result in HTML.ElementFromURL(pageUrl).xpath('//article[@id]'):  
		title = result.xpath('.//h1')[0].text
		summary = result.xpath('.//img')[0].text
		url = result.xpath('.//a')[0].get('href')
		thumb = Callback(GetThumb, url = url)
		
		oc.add(VideoClipObject(
		url = url,
		title = title,
		summary = summary,
		thumb=thumb
		))
		
	return oc	


####################################################################################################
def ArchivePage(pageUrl, title):

	oc = ObjectContainer(title2=title)
	oc.view_group = 'Details'
	
	for result in HTML.ElementFromURL(pageUrl).xpath('//o/li'):  		
		title = result.xpath('.//a')[0].text
		url = result.xpath('.//a')[0].get('href')

		oc.add(DirectoryObject(key = Callback(OpenArchiveMonthItem, title=title, url=url), title=title, thumb=R(ICON_ARCHIVE)))
		
	return oc	

####################################################################################################
def SearchPage(pageUrl, title, query):

	oc = ObjectContainer(title2=title)
	
	keywords = query.replace(" ", "%20")  
	pageUrl = pageUrl + keywords

	data = HTTP.Request(pageUrl).content.decode('latin-1')
	
	data = data.replace('<b style="color:black;background-color:#FFFF00">', "")
	data = data.replace('<b style="color:black;background-color:#00FFFF">', "")
	data = data.replace('<b style="color:black;background-color:#00FFFF">', "")
	data = data.replace('<b style="color:black;background-color:#FF9999">', "")
	data = data.replace('<b style="color:black;background-color:#FF66FF">', "")
	data = data.replace('</b>', "")
		
	for result in HTML.ElementFromString(data).xpath('//article[@class="artikel"]'):  	
		title = result.xpath('.//a')[0].text
		summary = result.xpath('.//p')[0].text
		url = result.xpath('.//a')[0].get('href')
		thumb = Callback(GetThumb, url = url)
		
		oc.add(VideoClipObject(
		url = url,
		title = title,
		summary = summary,
		thumb=thumb
		))
	
	if len(oc) == 0:
		oc = MessageContainer(L('Search'),L('NoResult'))

	return oc
	
####################################################################################################
def OpenArchiveMonthItem(title, url):

	oc = ObjectContainer(title2=title)
	oc.view_group = 'Details'
	
	for result in HTML.ElementFromURL(url).xpath('//article/ol/li'):  
		title = result.xpath('.//a')[0].text
		url = result.xpath('.//a')[0].get('href')
		summary = ""
		thumb = Callback(GetThumb, url = url)
		
		oc.add(VideoClipObject(
		url = url,
		title = title,
		summary = summary,
		thumb = thumb,
		))

	return oc	

####################################################################################################
def GetThumb(url):

	data = HTTP.Request(url).content
	content = HTML.ElementFromString(data)
	thumb = THUMBLINK.findall(data)
	
	try:
		thumb = thumb[0]
	except:
		try:
			thumb = content.xpath('.//article/img')[0].get('src')				
		except:
			Log.Debug('no images found')
			thumb = ""
	
	try:
		data = HTTP.Request(thumb, cacheTime=CACHE_1WEEK).content
		Log.Debug(thumb)
		return DataObject(data, 'image/jpeg')
	except:
		return Redirect(R(ICON))