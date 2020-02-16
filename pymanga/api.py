import requests
from bs4 import BeautifulSoup
from .parsers import search_parsers, series_parsers, release_parsers
#from parsers import search_parsers, series_parsers, releases_parsers

def search(query):
    r = requests.post('https://mangaupdates.com/search.html',params={'search':query})
    soup = BeautifulSoup(r.text,'html.parser')
    lists = soup.find('div',class_='center-side-bar').find_all('div',class_='row',recursive=False)[1].find('div',id='main_content').find_all('div',class_='row')
    results = {
        'releases': search_parsers.parse_releases(lists[0]),
        'series': search_parsers.parse_series(lists[1]),
        'scanlators': search_parsers.parse_scanlators(lists[2]),
        'authors': search_parsers.parse_authors(lists[3])
    }
    return results

def series(id):
    r = requests.get('https://mangaupdates.com/series.html',params={'id': id})
    soup = BeautifulSoup(r.text,'html.parser')
    content = soup.find('div',class_='center-side-bar').find_all('div',class_='row',recursive=False)[1].find('div',id='main_content').find('div',class_='p-2',recursive=False).find('div',class_='row',recursive=False)
    return series_parsers.parse_series(content)

def releases(id):
    r = requests.post('https://www.mangaupdates.com/releases.html',params={'stype': 'series','search': id,'page':1},data={'perpage':100})
    soup = BeautifulSoup(r.text,'html.parser')
    content = soup.find('div',class_='center-side-bar').find_all('div',class_='row',recursive=False)[1].find('div',id='main_content').find('div',class_='p-2',recursive=False).find('div',class_='row',recursive=False)
    return releases_parsers.parse_releases(content)
