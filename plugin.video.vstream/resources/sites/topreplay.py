#-*- coding: utf-8 -*-
#Vstream https://github.com/Kodi-vStream/venom-xbmc-addons
# plus vraiment le meme site
from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.comaddon import progress, dialog, VSlog, xbmc
from resources.lib.util import Quote
import re, requests

UA = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'

SITE_IDENTIFIER = 'topreplay'
SITE_NAME = 'TopReplay'
SITE_DESC = 'Replay TV'

URL_MAIN = 'https://www.topreplay.video'
URL_SEARCH = (URL_MAIN + '/?s=', 'showMovies')
URL_SEARCH_MISC = (URL_MAIN + '/?s=', 'showMovies')
FUNCTION_SEARCH = 'showMovies'

REPLAYTV_GENRES = (True, 'showGenre')
REPLAYTV_NEWS = (URL_MAIN , 'showMovies')
REPLAYTV_REPLAYTV = ('http://' , 'load')


def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Recherche', 'search.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', REPLAYTV_NEWS[0])
    oGui.addDir(SITE_IDENTIFIER, REPLAYTV_NEWS[1], 'Nouveautés', 'replay.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', REPLAYTV_GENRES[0])
    oGui.addDir(SITE_IDENTIFIER, REPLAYTV_GENRES[1], 'Genres', 'replay.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showSearch():
    oGui = cGui()

    sSearchText = oGui.showKeyBoard()
    if (sSearchText != False):
        sUrl = URL_SEARCH[0] + sSearchText
        showMovies(sUrl)
        oGui.setEndOfDirectory()
        return


def showGenre():
    oGui = cGui()
    oParser = cParser()

    oRequestHandler = cRequestHandler(URL_MAIN)
    sHtmlContent = oRequestHandler.request()
    reducesHtmlContent = oParser.abParse(sHtmlContent, 'class="main-menu menu bsm-pure clearfix">','<span class="menu-handler">')

    sPattern = '<a href="([^"]+)">([^<]+)<\/a>'
    aResult = oParser.parse(reducesHtmlContent, sPattern)
    if (aResult[0] == True):
        total = len(aResult[1])
        progress_ = progress().VScreate(SITE_NAME)
        for aEntry in aResult[1]:
            progress_.VSupdate(progress_, total)
            if progress_.iscanceled():
                break

            sTitle = aEntry[1]
            if 'Contactez' in sTitle:
                continue
            sUrl = aEntry[0]

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl)
            oGui.addDir(SITE_IDENTIFIER, 'showMovies', sTitle , 'replay.png', oOutputParameterHandler)

        progress_.VSclose(progress_)

    oGui.setEndOfDirectory()


def showMovies(sSearch = ''):
    oGui = cGui()
    oParser = cParser()

    if sSearch:
        sUrl = sSearch.replace(' ', '+')
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sPattern = 'data-src="([^"]+)".+?class="title"> *<a href="([^"]+)".+?class="post-title post-url">([^<]+)<\/a>'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == False):
        oGui.addText(SITE_IDENTIFIER)

    if (aResult[0] == True):
        for aEntry in aResult[1]:
            sThumb = aEntry[0]
            sUrl = aEntry[1]
            sTitle = aEntry[2]
            if 'Générateur compte' in sTitle:
                continue

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oGui.addMisc(SITE_IDENTIFIER, 'showLinks', sTitle, 'replay.png', sThumb, '', oOutputParameterHandler)

        sNextPage = __checkForNextPage(sHtmlContent)
        if (sNextPage != False):
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            number = re.search('/page/([0-9]+)', sNextPage).group(1)
            oGui.addNext(SITE_IDENTIFIER, 'showMovies', '[COLOR teal]Page ' + number + ' >>>[/COLOR]', oOutputParameterHandler)

    if not sSearch:
        oGui.setEndOfDirectory()


def __checkForNextPage(sHtmlContent):
    oParser = cParser()
    sPattern = '<a class="nextpostslink" rel="next" href="([^"]+)">'
    aResult = oParser.parse(sHtmlContent, sPattern)
    if (aResult[0] == True):
        return aResult[1][0]

    return False


def showLinks():
    oGui = cGui()
    oParser = cParser()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sPattern = '<a href="(https://mon-tele.com/.+?)".+?>([^<]+)'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == False):
        oGui.addText(SITE_IDENTIFIER)

    if (aResult[0] == True):
        for aEntry in aResult[1]:
            sHosterUrl = aEntry[0]
            sTitle = sMovieTitle + ' ' + aEntry[1]

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sHosterUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oGui.addMisc(SITE_IDENTIFIER, 'showHosters', sTitle, 'replay.png', sThumb, '', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def showHosters():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')

    if 'mon-tele' in sUrl:
        dialog().VSinfo('Décodage en cours', "Patientez", 5)
        s = requests.Session()

        response = s.get(sUrl, headers={'User-Agent':UA})
        sHtmlContent = str(response.content)
        cookie_string = "; ".join([str(x)+"="+str(y) for x,y in s.cookies.items()])

        oParser = cParser()
        sPattern = '<input type="hidden".+?value="([^"]+)"'
        aResult = oParser.parse(sHtmlContent, sPattern)

        from resources.lib import librecaptcha
        test = librecaptcha.get_token(
            api_key="6LezIsIZAAAAABMSqc7opxGc3xyCuXtAtV4VlTtN",
            site_url="https://mon-tele.com/",
            user_agent= UA,
            gui=False,
            debug=False,
        )
        
        if (aResult[0] == True):
            data = "_method="+aResult[1][0]+"&_csrfToken="+aResult[1][1]+"&ref=&f_n="+aResult[1][2]+"&g-recaptcha-response="+test+"&_Token%5Bfields%5D="+Quote(aResult[1][3])+"&_Token%5Bunlocked%5D="+Quote(aResult[1][4])

            oRequestHandler = cRequestHandler(sUrl)
            oRequestHandler.setRequestType(1)
            oRequestHandler.addHeaderEntry('Referer', sUrl)
            oRequestHandler.addHeaderEntry('Accept', ' text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
            oRequestHandler.addHeaderEntry('User-Agent', UA)
            oRequestHandler.addHeaderEntry('Content-Length', len(data))
            oRequestHandler.addHeaderEntry('Content-Type', "application/x-www-form-urlencoded")
            oRequestHandler.addHeaderEntry('Cookie', cookie_string)
            oRequestHandler.addParametersLine(data)
            sHtmlContent = oRequestHandler.request()

        oParser = cParser()
        sPattern = '<input type="hidden".+?value="([^"]+)"'
        aResult = oParser.parse(sHtmlContent, sPattern)

        if (aResult[0] == True):
            data = "_method="+aResult[1][0]+"&_csrfToken="+aResult[1][1]+"&ad_form_data="+Quote(aResult[1][2])+"&_Token%5Bfields%5D="+Quote(aResult[1][3])+"&_Token%5Bunlocked%5D="+Quote(aResult[1][4])

            #Obligatoire pour validé les cookies.
            xbmc.sleep(15000)
            oRequestHandler = cRequestHandler("https://mon-tele.com/obtenirliens/links/go")
            oRequestHandler.setRequestType(1)
            oRequestHandler.addHeaderEntry('Referer', sUrl)
            oRequestHandler.addHeaderEntry('Accept', 'application/json, text/javascript, */*; q=0.01')
            oRequestHandler.addHeaderEntry('User-Agent', UA)
            oRequestHandler.addHeaderEntry('Content-Length', len(data))
            oRequestHandler.addHeaderEntry('Content-Type', "application/x-www-form-urlencoded; charset=UTF-8")
            oRequestHandler.addHeaderEntry('X-Requested-With','XMLHttpRequest')
            oRequestHandler.addHeaderEntry('Cookie', cookie_string)
            oRequestHandler.addParametersLine(data)
            sHtmlContent = oRequestHandler.request()

            sPattern = 'url":"([^"]+)"'
            aResult = oParser.parse(sHtmlContent, sPattern)
            if (aResult[0] == True):
                sHosterUrl = aResult[1][0]
                oHoster = cHosterGui().checkHoster(sHosterUrl)
                if (oHoster != False):
                    oHoster.setDisplayName(sMovieTitle)
                    oHoster.setFileName(sMovieTitle)
                    cHosterGui().showHoster(oGui, oHoster, sHosterUrl, sThumb)
    else:   
        sHosterUrl = sUrl
        oHoster = cHosterGui().checkHoster(sHosterUrl)
        if (oHoster != False):
            oHoster.setDisplayName(sMovieTitle)
            oHoster.setFileName(sMovieTitle)
            cHosterGui().showHoster(oGui, oHoster, sHosterUrl, sThumb)

    oGui.setEndOfDirectory()
