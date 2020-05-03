import requests
from bs4 import BeautifulSoup
from .parsers import search_parsers, series_parsers, releases_parsers

def search(query):
    r = requests.post('https://mangaupdates.com/search.html',params={'search':query})
    soup = BeautifulSoup(r.text,'html.parser')
    lists = soup.find('div',class_='center-side-bar').find_all('div',class_='row',recursive=False)[1].find('div',id='main_content').find_all('div',class_='row')

    results = {}
    try:
        results['releases'] = search_parsers.parse_releases(lists[0])
    except:
        results['releases'] = []
    try:
        results['series'] = search_parsers.parse_series(lists[1])
    except:
        results['series'] = []
    try:
        results['scanlators'] = search_parsers.parse_scanlators(lists[2])
    except:
        results['scanlators'] = []
    try:
        results['authors'] = search_parsers.parse_authors(lists[3])
    except:
        results['authors'] = []
    return results

def series(id):
    r = requests.get('https://mangaupdates.com/series.html',params={'id': id})
    soup = BeautifulSoup(r.text,'html.parser')
    content = soup.find('div',class_='center-side-bar').find_all('div',class_='row',recursive=False)[1].find('div',id='main_content').find('div',class_='p-2',recursive=False).find('div',class_='row',recursive=False)
    series = {}
    try:
        series = series_parsers.parse_series(content)
    except:
        series = {}
    return series

def releases(id):
    r = requests.post('https://www.mangaupdates.com/releases.html',params={'stype': 'series','search': id,'page':1},data={'perpage':100})
    soup = BeautifulSoup(r.text,'html.parser')
    content = soup.find('div',class_='center-side-bar').find_all('div',class_='row',recursive=False)[1].find('div',id='main_content').find('div',class_='p-2',recursive=False).find('div',class_='row',recursive=False)
    releases = []
    try:
        releases = releases_parsers.parse_releases(content)
    except:
        releases = []
    return releases
