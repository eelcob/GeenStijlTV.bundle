NAME 			= L('Title')
ART 			= "art-default.png"
ICON 			= "icon-default.png"
ICON_MORE		= "icon-next.png"
ICON_ARCHIVE 	= "icon-archive.png"
ICON_RECENT 	= "icon-recent.png"
ICON_ZOEKEN 	= "icon-zoeken.png"

# URLS
URL_ROOT_URI	= "http://www.geenstijl.tv/"
URL_ARCHIEF		= URL_ROOT_URI + "archief.html"
URL_ZOEKEN		= URL_ROOT_URI + "fastsearch?query="

# Regexes
THUMBLINK = Regex("GSvideo.preview = '(.*?)';")

####################################################################################################
def Start():

	Plugin.AddPrefixHandler("/video/geenstijltv", MainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
	Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")

	ObjectContainer.title1 = NAME
	ObjectContainer.view_group = 'List'
	ObjectContainer.art = R(ART)  

	VideoClipObject.thumb = R(ICON)

	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:13.0) Gecko/20100101 Firefox/13.0.1'

####################################################################################################
def MainMenu():

	oc = ObjectContainer()

	oc.add(DirectoryObject(key = Callback(HomePage, title=L('LastFive')), title=L('LastFive'), thumb=R(ICON_RECENT)))
	oc.add(DirectoryObject(key = Callback(ArchivePage, title=L('Archive')), title=L('Archive'), thumb=R(ICON_ARCHIVE)))
	oc.add(InputDirectoryObject(key = Callback(SearchPage, title=L('Search')), title=L('Search'), thumb=R(ICON_ZOEKEN), prompt=L('Search')))

	return oc

####################################################################################################
def HomePage(title):

	oc = ObjectContainer(title2=title, view_group='Details')

	for result in HTML.ElementFromURL(URL_ROOT_URI).xpath('//article[@id]'):
		title = result.xpath('./h1/text()')[0]
		summary = result.xpath('./p/text()')[0]
		url = result.xpath('.//strong/a')[0].get('href')
		thumb = Callback(GetThumb, url = url)
		
		oc.add(VideoClipObject(
			url = url,
			title = title,
			summary = summary,
			thumb = thumb
		))

	return oc

####################################################################################################
def ArchivePage(title):

	oc = ObjectContainer(title2=title, view_group='Details')

	for result in HTML.ElementFromURL(URL_ARCHIEF).xpath('//o/li'):
		title = result.xpath('.//a')[0].text
		url = result.xpath('.//a')[0].get('href')

		oc.add(DirectoryObject(key = Callback(OpenArchiveMonthItem, title=title, url=url), title=title, thumb=R(ICON_ARCHIVE)))

	return oc

####################################################################################################
def SearchPage(title, query):

	oc = ObjectContainer(title2=title)

	keywords = query.replace(" ", "%20")
	url = '%s%s' % (URL_ZOEKEN, keywords)

	data = HTTP.Request(url).content.decode('latin-1')

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
			thumb = thumb
		))

	if len(oc) == 0:
		oc = MessageContainer(L('Search'), L('NoResult'))

	return oc

####################################################################################################
def OpenArchiveMonthItem(title, url):

	oc = ObjectContainer(title2=title, view_group='Details')

	for result in HTML.ElementFromURL(url).xpath('//article/ol/li'):
		title = result.xpath('.//a')[0].text
		url = result.xpath('.//a')[0].get('href')
		thumb = Callback(GetThumb, url = url)

		oc.add(VideoClipObject(
			url = url,
			title = title,
			thumb = thumb
		))

	return oc

####################################################################################################
def GetThumb(url):

	data = HTTP.Request(url).content
	image = THUMBLINK.findall(data)

	try:
		thumb = image[0]
	except:
		try:
			content = HTML.ElementFromString(data)
			thumb = content.xpath('//article/img')[0].get('src')
		except:
			Log.Debug('no images found')
			thumb = None

	if thumb:
		try:
			data = HTTP.Request(thumb, cacheTime=CACHE_1WEEK).content
			return DataObject(data, 'image/jpeg')
		except:
			pass

	return Redirect(R(ICON))
