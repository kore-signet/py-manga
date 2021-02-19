import requests
from bs4 import BeautifulSoup
import urllib.parse as urlparse
import re
import os
import traceback
from .parsers import search_parsers, series_parsers, releases_parsers, adv_search_parser

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

# Warning: this can take a long time on general searches with the 'all_pages' option enabled!
def advanced_search(params,all_pages=False,page=1):
    params['page'] = page
    params['perpage'] = 100

    # do some quality of life processing (turn list args. into properly escaped parameters)
    params['genre'] = '_'.join(params.get('genre',[]))
    params['exclude_genre'] = '_'.join(params.get('exclude_genre',[]))
    params['category'] ='_'.join(params.get('category',[]))

    if 'name' in params:
        params['search'] = params['name']

    payload = urlparse.urlencode(params,safe='+')

    r = requests.get('https://mangaupdates.com/series.html',params=payload)
    soup = BeautifulSoup(r.text,'html.parser')
    # find page count. i know regex is a crime but.

    pages = re.search(r'Pages \((\d+)\)',r.text)
    if pages:
        pages = int(pages.group(1))
    else:
        pages = 1

    results = adv_search_parser.parse_results(soup)

    # if all pages is set, request every page and append their results to the return value

    if all_pages and pages > 1:
        for p in range(page+1,pages+1):
            r, _ = advanced_search(params,page=p)
            results = results + r

        os.sleep(1) # be polite!

    return (results,pages)

# advanced search, but with a generator!
def advanced_search_iter(params):
    first_batch, total_pages = advanced_search(params)
    yield from first_batch

    for p in range(2,total_pages+1):
        r, _ = advanced_search(params,page=p)
        yield from r

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
