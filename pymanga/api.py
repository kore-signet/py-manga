import requests
from bs4 import BeautifulSoup
import urllib.parse as urlparse
import re
import os
from .parsers import search_parsers, series_parsers, releases_parsers, adv_search_parser


def search(query):
    """
    Performs a name-based search of MangaUpdates.

    Parameters
    ----------
    query : str
        Name to search by.

    Returns
    -------
    dict : dict of {str : list}
        Results of search.

    See Also
    --------
    pymanga.parsers.search_parsers
    """

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
    """
    Do an 'advanced search' of MangaUpdates' manga.

    Parameters
    ----------
    params : dict
        Dict of parameters to search by.

        ::

            {
                'orderby': 'rating' or 'title' or 'year', # how to sort search results,
                'category': ['MangaUpdates','Categories/Tags'],
                'genre': ['Genres', 'To', 'Include'], # for a list of possible values
                'exclude_genre': ['Genres', 'To', 'Exclude' # see 'pymanga.genres'

                'licensed': empty or 'yes' or 'no',
                    # empty/not specified -> show all
                    # 'yes' -> show only licensed manga
                    # 'no' -> show only unlicensed manga

                'filter': empty or 'filtering option',
                    # empty/not specified -> show all
                    # 'scanlated' -> only completely scanlated manga
                    # 'completed' -> only completed manga (includes oneshots)
                    # 'oneshots' -> only show oneshots
                    # 'no_oneshots' -> excludes oneshots
                    # 'some_releases' -> only show manga with at least one release
                    # 'no_releases' -> only show manga with no releases

                'type': empty or 'type option',
                    # 'artbook'
                    # 'doujinshi'
                    # 'drama_cd'
                    # 'filipino'
                    # 'indonesian'
                    # 'manga'
                    # 'manhwa'
                    # 'manhua'
                    # 'novel'
                    # 'oel'
                    # 'thai'
                    # 'vietnamese'
                    # 'malaysian'
            }

    all_pages : bool, optional
        Fetch all results pages or not.

        Defaults to False.

        Note: the module automatically sleeps between requests if all_pages is set to true,
        as to not overload MangaUpdates.

        Consider using advanced_search_iter instead.

    page : int, optional
        What page of results to fetch.
        Defaults to 1.

    Returns
    -------
    results : list of dicts
        List of search results.
        ::

            [
                {
                    'name': 'Series Name',
                    'id': 'Series ID',
                    'rating': 'Average Rating',
                    'summary': 'Short summary',
                    'thumbnail': 'Thumbnail link' or None,
                    'year': 'Year manga started releasing',
                    'is_adult': True or False
                    # note! mangaupdates categorizes whole genres like 'Yuri' as adult
                    # so use this at your own discretion :)
                    # if this is true, thumbnail will always be None.
                }
            ]

    See Also
    --------
    pymanga.genres
    pymanga.api.advanced_search_iter
    """
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
    """
    Same as pymanga.api.advanced_search, but as a generator.

    Requests new pages from mangaupdates only as needed.

    See Also
    --------
    pymanga.api.advanced_search
    """
    first_batch, total_pages = advanced_search(params)
    yield from first_batch

    for p in range(2,total_pages+1):
        r, _ = advanced_search(params,page=p)
        yield from r

def series(id):
    """
    Get series info from mangaupdates.

    Parameters
    ----------
    id : str
        Series id.

    Returns
    -------
    series : dict
        Series information.
        ::

            {
                # main info
                'title': 'Series Name',
                'year':
                'type': 'Type of series (manhwa,manhua,manga,et)',
                'status': 'n Volumes (Ongoing or Complete or etc..)'
                'image': 'cover image link',
                'last_updated': 'December 3rd 2020, 5:32pm PST', # last time page was updated
                # authors & artists
                'artists': [
                    {
                        'id': 'Artist's Manga Updates ID',
                        'name': 'Artist's Name'
                    }
                ],
                'authors': [
                    {
                        'id': 'Author's Manga Updates ID',
                        'name': 'Author's Name'
                    }
                ],
                # relations
                'associated_names': [ # often in different languages, so make sure you can handle unicode.
                     'Name one',
                     'Name two'
                ],
                'related_series': [
                    {
                        'id': 'Related Series ID',
                        'name': 'Related Series Name',
                        'relation': 'Relation to current manga'
                    }
                ],
                'anime_chapters': [ # if it doesn't have an anime, list will be empty
                    'Starts at Vol x, Chap y',
                    'Ends at Vol z, Chap w'
                ],
                # description & genre
                'genres': [
                    'Genre',
                    ...
                ],
                'categories': [
                    {
                        'category': 'Category Name',
                        'score': '16 (16,0)'
                    }
                ],
                'description': 'Lorem ipsum dolor sit amet..',
                # publishing info
                'publisher': {
                    'id': 'publisher ID',
                    'name': 'publisher name'
                },
                'serialized': {
                    'link': 'mangaupdates link to where it was serialized',
                    'name': 'name of where it was serialized'
                },
                'licensed': True or False # whether this series was licensed in english,
                'english_publisher': {
                    'id': 'English Publisher ID',
                    'name': 'English Publisher Name + Volume Info'
                },
                # scanlation info
                'completely_scanlated': True or False,
                'latest_releases': [
                    {
                        'chapter': 'chapter number',
                        'volume': 'volume number if present',
                        'date': 'n days ago',
                        'group': {
                            'id': 'Scanlation Group ID',
                            'name': 'Scanlation Group Name'
                        }
                    }
                ],
                'groups': [ # all scanlation groups that published releases for this series
                    {
                        'id': 'Scanlation Group ID',
                        'name': 'Scanlation Group Name'
                    }
                ],
                # recommendations
                'category_recs': [
                    {
                        'id': 'Recommended Series ID',
                        'name': 'Recommended Series Name'
                    }
                ],
                'recs': [
                    {
                        'id': 'Recommended Series ID',
                        'name': 'Recommended Series Name'
                    }
                ],
                # user-related info
                'positions': {
                    'monthly': '779',
                    'monthly_change': '+155',
                    'six_monthly': '1244',
                    'six_monthly_change': '+76',
                    'tri_monthly': '1120',
                    'tri_monthly_change': '-17',
                    'weekly': '431',
                    'weekly_change': '+121',
                    'yearly': '1277',
                    'yearly_change': '-162'
                },
                'average': { # ratings
                    'average': 'average rating',
                    'bayesian': 'bayesian average rating',
                    'votes': 'n votes'
                },
                'reading_lists': {
                    'custom': 'n',
                    'reading': 'n',
                    'unfinished': 'n',
                    'wish': 'n'
                },
                'forum': {
                    'link': 'https://www.mangaupdates.com/topics.php?fid=120202',
                    'status': 'None'
                }
            }

    """
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
    """
    Get latest releases of a manga

    Parameters
    ----------
    id : str
        Manga ID.

    Returns
    -------
    releases : list of dicts
        List of latest releases of a manga.
        List is ordered latest-to-oldest
        ::

            [
                {
                    'chapter': 'chapter number',
                    'vol': 'volume number' or None,
                    'series': {
                        'name': 'Manga Name',
                        'id': 'Manga ID'
                    },
                    'group': {
                        'name': 'Scanlation Group Name',
                        'id': 'Scanlation Group ID'
                    }
                }
            ]
    """
    r = requests.post('https://www.mangaupdates.com/releases.html',params={'stype': 'series','search': id,'page':1},data={'perpage':100})
    soup = BeautifulSoup(r.text,'html.parser')
    content = soup.find('div',class_='center-side-bar').find_all('div',class_='row',recursive=False)[1].find('div',id='main_content').find('div',class_='p-2',recursive=False).find('div',class_='row',recursive=False)
    releases = []
    try:
        releases = releases_parsers.parse_releases(content)
    except:
        releases = []
    return releases
