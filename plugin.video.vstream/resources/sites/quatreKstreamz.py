# -*- coding: utf-8 -*-
# vStream https://github.com/Kodi-vStream/venom-xbmc-addons

import re

from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.comaddon import progress

SITE_IDENTIFIER = 'quatreKstreamz'
SITE_NAME = '4kstreamz'
SITE_DESC = ' films et series'

URL_MAIN = 'https://www.4kstreamz.co/'

MOVIE_NEWS = (URL_MAIN + '/list-films.html', 'showMovies')
MOVIE_GENRES = (True, 'showGenres')
MOVIE_ANNEES = (True, 'showYears')
URL_SEARCH = (URL_MAIN + 'recherche/', 'showMovies')
URL_SEARCH_MOVIES = (URL_SEARCH[0], 'showMovies')
URL_SEARCH_SERIES = (URL_SEARCH[0], 'showMovies')
SERIE_NEWS = (URL_MAIN + 'series.html', 'showMovies')

def load():
    oGui = cGui()
    
    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_SEARCH[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Recherche', 'search.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_NEWS[0])
    oGui.addDir(SITE_IDENTIFIER, MOVIE_NEWS[1], 'Films (Derniers ajouts)', 'news.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_GENRES[0])
    oGui.addDir(SITE_IDENTIFIER, MOVIE_GENRES[1], 'Films (Genres)', 'genres.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_ANNEES[0])
    oGui.addDir(SITE_IDENTIFIER, MOVIE_ANNEES[1], 'Films (Par années)', 'genres.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', SERIE_NEWS[0])
    oGui.addDir(SITE_IDENTIFIER, SERIE_NEWS[1], 'Series (Derniers ajouts)', 'news.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showSearch():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sSearchText = oGui.showKeyBoard()
    if (sSearchText != False):
        sUrl = sUrl + sSearchText 
        showMovies(sUrl)
        oGui.setEndOfDirectory()
        return

def showYears():
    oGui = cGui()
    for i in reversed(range(1921, 2021)):
        sYear = str(i)
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + 'filmspar?annee='+ sYear )  # / inutile
        oGui.addDir(SITE_IDENTIFIER, 'showMovies', sYear, 'annees.png', oOutputParameterHandler)
    oGui.setEndOfDirectory()


def showGenres():

    oGui = cGui()
    oParser = cParser()

    sUrl = URL_MAIN 
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    sStart = '<h4 class="head nop">Genre'
    sEnd = '<div class="menu_first">'
    sHtmlContent = oParser.abParse(sHtmlContent, sStart, sEnd)

    sPattern = 'a href="([^"]+)" class="an">([^<]+)'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == False):
        oGui.addText(SITE_IDENTIFIER)
    TriAlpha = []
    if (aResult[0] == True):
        for aEntry in aResult[1]:
            sUrl =  aEntry[0]
            sTitle = aEntry[1].capitalize()
            TriAlpha.append((sTitle, sUrl))

        # Trie des genres par ordre alphabétique
        TriAlpha = sorted(TriAlpha, key=lambda genre: genre[0])

        for sTitle, sUrl in TriAlpha:
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl)
            oGui.addDir(SITE_IDENTIFIER, 'showMovies', sTitle, 'genres.png', oOutputParameterHandler)
        oGui.setEndOfDirectory()



def showMovies(sSearch=''):
    oGui = cGui()
    oParser = cParser()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')

    if sSearch:

        sUrl = sSearch.replace(' ', '-').replace('%20', '-')+ '.html'
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    if 'list-films.html' in sUrl or '/films/page' in sUrl:
        sPattern = '<a class="movie_single.+?href="([^"]+).+?img src="([^"]+).+?class="nop">([^<]+).+?class="qualitos">([^<]+).+?class="synopsis nop">([^<]+)'
    else:
        sPattern = '<a class="movie_single.+?href="([^"]+).+?img src="([^"]+).+?class="nop">([^<]+)'
    
    aResult = oParser.parse(sHtmlContent, sPattern)
    if (aResult[0] == False):
        oGui.addText(SITE_IDENTIFIER)
     
    if (aResult[0] == True):
        total = len(aResult[1])
        progress_ = progress().VScreate(SITE_NAME)
        for aEntry in aResult[1]:
            progress_.VSupdate(progress_, total)
            if progress_.iscanceled():
                break
            sUrl2 = aEntry[0]
            sThumb = aEntry[1]
            if 'http' not in sUrl2:
                sUrl2 = URL_MAIN[:-1] + sUrl2
            if 'http' not in sThumb:
                sThumb = URL_MAIN[:-1] + sThumb 
                 
            sTitle = aEntry[2].strip()
            sQual = ''
            sDesc = ''
            if 'list-films.html'  in sUrl or '/films/page' in sUrl:
                sQual = aEntry[3]              
                sDesc = aEntry[4]
            
            sDisplayTitle = ('%s [%s] ') % (sTitle, sQual)

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl2)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sDesc', sDesc)

            if '/series' not in sUrl2:
                oGui.addMovie(SITE_IDENTIFIER, 'showLinks', sDisplayTitle, '', sThumb,sDesc  , oOutputParameterHandler)
            else:
                oGui.addTV(SITE_IDENTIFIER, 'showSaisons', sDisplayTitle, '', sThumb, sDesc, oOutputParameterHandler)

        progress_.VSclose(progress_)
 
    if not sSearch:
        sNextPage = __checkForNextPage(sHtmlContent)
        if (sNextPage != False):
            sNumber = re.search('page-([0-9]+)|([0-9]+)$', sNextPage).group(0)## page-XX.html ou  annee-aaaa/XX
            sNumber = sNumber .replace('page-', '')
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            oGui.addNext(SITE_IDENTIFIER, 'showMovies', '[COLOR teal]Page ' + sNumber + ' >>>[/COLOR]', oOutputParameterHandler)

        oGui.setEndOfDirectory()


def __checkForNextPage(sHtmlContent):
    oParser = cParser()
    if 'suivanthds' in sHtmlContent:# genre
        sPattern = 'suivanthds.+?href="([^"]+)' 
    elif 'CurrentPage': # film année serie
        sPattern = "CurrentPage.+?href='([^']+)"
    else:
        # verifier cas
        return False

    aResult = oParser.parse(sHtmlContent, sPattern)
    if (aResult[0] == True):
        return URL_MAIN[:-1] + aResult[1][0]
    return False


def showSaisons():
    oGui = cGui()
    oParser = cParser()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sThumb = oInputParameterHandler.getValue('sThumb')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sYear = oInputParameterHandler.getValue('sYear')
    sDesc = oInputParameterHandler.getValue('sDesc')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sPattern = 'itemprop="description">([^<]+)'
    aResult = oParser.parse(sHtmlContent, sPattern)
    if (aResult[0] == True):
        sDesc = ('[I][COLOR grey]%s[/COLOR][/I] %s') % ('Synopsis :', aResult[1][0])

    start=sHtmlContent.find('<div class="contentomovies">')

    sHtmlContent = sHtmlContent[start:]

    sPattern = '<a href="([^"]+).+?class="nop">Saison([^<]+)'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == False):
        oGui.addText(SITE_IDENTIFIER)

    if (aResult[0] == True):
        for aEntry in reversed(aResult[1]):
            sUrl2 = aEntry[0]
            saison = aEntry[1].replace(' ', '')
            
            sTitle = ("%s %s") % (sMovieTitle, ' Saison ' + saison)

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl2)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oOutputParameterHandler.addParameter('sDesc', sDesc)
            oOutputParameterHandler.addParameter('sMovieTitle', sMovieTitle)
            oOutputParameterHandler.addParameter('sYear', sYear)
            oGui.addEpisode(SITE_IDENTIFIER, 'ShowEpisodes', sTitle, '', sThumb, sDesc, oOutputParameterHandler)

    oGui.setEndOfDirectory()


def ShowEpisodes():
    oGui = cGui()
    oParser = cParser()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')
    sDesc = oInputParameterHandler.getValue('sDesc')
    sYear = oInputParameterHandler.getValue('sYear')

    isaison = ''
    sPattern = 'saison.(.+?)'
    aResult = oParser.parse(sUrl , sPattern)
    if (aResult[0] == True):
        isaison = ' Saison '  + aResult[1][0].replace(' ', '')
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    sStart = '<div class="contentomovies">'
    sEnd = '<div class="keywords"'
    sHtmlContent = oParser.abParse(sHtmlContent, sStart, sEnd)
    sPattern = '<a href="([^"]+).+?class="titverle">.+?class="nop">Épisode([^<]+)'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == False):
        oGui.addText(SITE_IDENTIFIER)

    if (aResult[0] == True):
        for aEntry in aResult[1]:
            sUrl2 =  aEntry[0]
            nepisode = aEntry[1].replace(' ', '')
            if 'http' not in sUrl2:
                sUrl2 = URL_MAIN[:-1] + sUrl2

            sTitle = sMovieTitle   + isaison + ' episode' + nepisode

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl2)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oOutputParameterHandler.addParameter('sMovieTitle', sMovieTitle)
            oOutputParameterHandler.addParameter('sYear', sYear)
            oOutputParameterHandler.addParameter('sDesc', sDesc)
            oGui.addEpisode(SITE_IDENTIFIER, 'showLinks', sTitle, '', sThumb, sDesc, oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showLinks(): 
    
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')
    sDesc = oInputParameterHandler.getValue('sDesc')

    oParser = cParser()

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sPattern = 'itemprop="description">([^<]+)'
    aResult = oParser.parse(sHtmlContent, sPattern)
    if (aResult[0] == True):
        sDesc = ('[I][COLOR grey]%s[/COLOR][/I] %s') % ('Synopsis :', aResult[1][0])

    sPattern = 'data-url="([^"]+).+?data-code="([^"]+).+?<span>([^<]+)|<img src=".(vf|vostfr).png'

    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == True):
        for aEntry in aResult[1]:
            if aEntry[3]:
                Slang = ' (' + aEntry[3].upper() + ')'

            if aEntry[0]:
                dataurl =  aEntry[0]
                datacode = aEntry[1]
                sHost = aEntry[2].lower()
                if isblackhost(sHost):
                    continue

                sUrl2 = URL_MAIN +'Players.php?PPl=' + dataurl + '&CData=' + datacode
                sDisplayTitle = ('%s [COLOR coral]%s[/COLOR]') % (sTitle + Slang, sHost)
                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', sUrl2)
                oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
                oOutputParameterHandler.addParameter('sDesc', sDesc) 
                oOutputParameterHandler.addParameter('sThumb', sThumb)
                oOutputParameterHandler.addParameter('referer', sUrl)
                oGui.addLink(SITE_IDENTIFIER, 'showHosters', sDisplayTitle, sThumb, sDesc, oOutputParameterHandler)

    sPattern = "class=.Playersbelba.+?PPl=(.+?)CData=([^']+).+?<.span>.+?<span>([^<]+)|<img src=\".(vf|vostfr).png"
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == True):
        for aEntry in aResult[1]:
            if aEntry[3]:
                Slang = ' (' + aEntry[3].upper() + ')'

            if aEntry[0]:
                dataurl =  aEntry[0]
                datacode = aEntry[1]
                sHost = aEntry[2]
                sUrl2 = URL_MAIN +'Players.php?PPl=' + dataurl + 'CData=' + datacode

                sDisplayTitle = ('%s [COLOR coral]%s[/COLOR]') % (sTitle + Slang, sHost)

                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', sUrl2)
                oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
                oOutputParameterHandler.addParameter('sDesc', sDesc) 
                oOutputParameterHandler.addParameter('sThumb', sThumb)
                oOutputParameterHandler.addParameter('referer', sUrl)
                oGui.addLink(SITE_IDENTIFIER, 'showHosters', sDisplayTitle, sThumb, sDesc, oOutputParameterHandler)
    oGui.setEndOfDirectory() 


def showHosters():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')
    referer = oInputParameterHandler.getValue('referer')

    oRequest = cRequestHandler(sUrl)
    oRequest.addHeaderEntry('Referer', referer)
    oRequest.request()
    urlreal=oRequest.getRealUrl()
    if URL_MAIN in urlreal:
        oRequest = cRequestHandler(sUrl)
        oRequest.addHeaderEntry('Referer', referer)
        oRequest.request()
        sHtmlContent=oRequest.request()

        oParser = cParser()
        sPattern = 'class="DownloadSection.+?href="([^"]+)'
        aResult = oParser.parse(sHtmlContent, sPattern)
        if (aResult[0] == True):
            sHosterUrl = aResult[1][0]
            oHoster = cHosterGui().checkHoster(sHosterUrl)
            if (oHoster != False):
                oHoster.setDisplayName(sMovieTitle)
                oHoster.setFileName(sMovieTitle)
                cHosterGui().showHoster(oGui, oHoster, sHosterUrl, sThumb)

    else:
        sHosterUrl = urlreal
        oHoster = cHosterGui().checkHoster(sHosterUrl)
        if (oHoster != False):
            oHoster.setDisplayName(sMovieTitle)
            oHoster.setFileName(sMovieTitle)
            cHosterGui().showHoster(oGui, oHoster, sHosterUrl, sThumb)
 
    oGui.setEndOfDirectory()


def isblackhost(url):
    black_host = ['4k player', 'streamango', 'openload', 'verystream']
    urllower = url.lower()
    for host in black_host:
        if host.lower() in urllower:
            return True
    return False
