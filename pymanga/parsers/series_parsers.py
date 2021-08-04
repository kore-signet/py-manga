import markdownify
from bs4 import Comment
import re
import sys

def parse_series(content):
    """
    Parse series info from mangaupdates.

    Parameters
    ----------
    content : BeautifulSoup
        BeautifulSoup object of series page html.

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
    manga = {}
    manga['title'] = str(content.find('span',class_='releasestitle').string)

    cols = content.find_all('div',class_='col-6',recursive=False)
    col_1 = cols[0]
    col_2 = cols[1]

    _parse_col_1(col_1,manga)
    _parse_col_2(col_2,manga)
    return manga

def _parse_col_1(col,manga):
    contents = col.find_all('div',class_='sContent',recursive=False)

    desc_tag = contents[0]
    for c in desc_tag.findAll(text=lambda text:isinstance(text, Comment) or text.name == 'script'):
        c.extract()

    comment_expr = re.compile(r'<!--(?:.|\n)+?\/\/-->')
    manga['description'] = markdownify.markdownify(comment_expr.sub('',desc_tag.encode_contents().decode('utf-8'))).replace('[**M**ore...](javascript:dispdescMore())','').replace('[**L**ess...](javascript:dispdescLess())','').strip()
    manga['type'] = str(contents[1].string).replace('\n','')

    manga['related_series'] = []
    for link in contents[2].findAll('a'):
        manga['related_series'].append({
            'name': link.get_text(),
            'id': link.get('href','').replace('series.html?id=',''),
            'relation': str(link.nextSibling).strip().replace('(','').replace(')','')
        })


    manga['associated_names'] = [markdownify.markdownify(name) for name in contents[3].encode_contents().decode('utf-8').replace('\n','').replace('</br>','').split('<br>') if len(name) > 0 and name != 'N/A']

    if 'N/A' not in contents[4].get_text():
        if contents[4].a is None:
            manga['groups'] = [{ 'name': contents[4].get_text().strip(),'id': None }]
        else:
            manga['groups'] = []
            for group in contents[4].findAll('a',attrs={'title':'Group Info'}):
                manga['groups'].append({ 'name': group.get_text(), 'id': group['href'].replace('https://www.mangaupdates.com/groups.html?id=','')})
    else:
        manga['groups'] = []

    manga['latest_releases'] = []
    numbers = contents[5].find_all('i')[:-1]
    groups = contents[5].find_all('a')[:-1]
    dates = contents[5].find_all('span')

    for i in range(0,len(dates)):
        release = {
            'group': {
                'name': str(groups[i].string),
                'id': str(groups[i].get('href','').replace('https://www.mangaupdates.com/groups.html?id=',''))
            },
            'date': dates[i]['title']
        }

        # this is to check if there are volume numbers. its a bad solution, folks!
        if len(numbers) >= len(dates) * 2:
            release['volume'] = str(numbers[i].string)
            release['chapter'] = str(numbers[i+1].string)
        else:
            release['chapter'] =  str(numbers[i].string)

        manga['latest_releases'].append(release)


    manga['status'] = contents[6].get_text(separator='!@#').replace('\n','').split('!@#')
    if str(contents[7].string).replace('\n','') == 'No':
        manga['completely_scanlated'] = False
    else:
        manga['completely_scanlated'] = True

    manga['anime_chapters'] = None if 'N/A' in contents[8].get_text() else contents[8].encode_contents().decode('utf-8').replace('\n','').split('<br/>')
    manga['user_reviews'] = str(contents[9].string).replace('\n','')

    manga['forum'] = {
        'status': str(contents[10].string),
        'link': 'https://www.mangaupdates.com/' + contents[10].a.get('href','')
    }

    try:
        average_raw = contents[11].contents
        manga['average'] = {
            'average': str(average_raw[0]).replace('Average:','').replace(' ',''),
            'votes': str(average_raw[2]).replace('(','').replace(')',''),
            'bayesian': str(average_raw[5]).replace('<b>','').replace('</b>','')
        }
    except:
        manga['average'] = None

    manga['last_updated'] = str(contents[12].string).replace('\n','')

def _parse_col_2(col,manga):
    contents = col.find_all('div',class_='sContent',recursive=False)

    manga['image'] = contents[0].center.img['src']

    manga['genres'] = []
    for genre in contents[1].find_all('a')[:-1]:
        manga['genres'].append(str(genre.u.string))

    manga['categories'] = []
    if contents[2].div:
        for cat_raw in contents[2].div.ul.find_all('li'):
            cat = cat_raw.find('a',rel='nofollow')
            manga['categories'].append({
                'category': str(cat.string),
                'score': str(cat['title']).replace('Score:','')
            })

    manga['category_recs'] = []
    for rec in contents[3].find_all('a',recursive=True):
        if 'javascript' not in rec.get('href',''):
            manga['category_recs'].append({
                'name': rec.get_text(),
                'id': rec.get('href','').replace('series.html?id=','')
            })

    manga['recs'] = []
    for rec in contents[4].find_all('a',recursive=True):
        if 'javascript' not in rec.get('href',''):
            manga['recs'].append({
                'name': str(rec.get_text()),
                'id': rec.get('href','').replace('series.html?id=','')
            })

    manga['authors'] = []
    for author in contents[5].find_all('a'):
        manga['authors'].append({
            'name': str(author.get_text()),
            'id': author.get('href','').replace('https://www.mangaupdates.com/authors.html?id=','')  if contents[5].a else 'N/A'
        })

    manga['artists'] = []
    for artist in contents[6].find_all('a'):
        manga['artists'].append({
            'name': str(artist.get_text()),
            'id': artist.get('href','').replace('https://www.mangaupdates.com/authors.html?id=','')  if contents[6].a else 'N/A'
        })

    manga['year'] = str(contents[7].get_text()).replace('\n','')

    manga['publisher'] = {
        'name': str(contents[8].get_text().strip()),
        'id': contents[8].a.get('href','').replace('https://www.mangaupdates.com/publishers.html?id=','')  if contents[8].a else 'N/A'
    }

    # TODO: add publisher info
    manga['serialized'] = {
        'name': str(contents[9].get_text().strip()),
        'link': 'https://www.mangaupdates.com/' + contents[9].a.get('href','') if contents[9].a else ''
    }

    manga['licensed'] = True if 'Yes' in contents[10].get_text() else False

    # TODO: add volume/ongoing info
    manga['english_publisher'] = {
        'name': str(contents[11].get_text().strip()),
        'id': str(contents[11].a.get('href','').replace('https://www.mangaupdates.com/publishers.html?id=','') if contents[11].a else 'N/A')
    }

    pos_r = contents[12].contents

    manga['positions'] = {
        'weekly': str(pos_r[2].string),
        'weekly_change': str(pos_r[5].string).replace('(','').replace(')',''),
        'monthly': str(pos_r[9].string),
        'monthly_change': str(pos_r[12].string).replace('(','').replace(')',''),
        'tri_monthly': str(pos_r[16].string),
        'tri_monthly_change': str(pos_r[19].string).replace('(','').replace(')',''),
        'six_monthly': str(pos_r[23].string),
        'six_monthly_change': str(pos_r[26].string).replace('(','').replace(')',''),
        'yearly': str(pos_r[30].string),
        'yearly_change': str(pos_r[33].string).replace('(','').replace(')','')
    }

    read_lists = contents[13].find_all('b')
    manga['reading_lists'] = {
        'reading': str(read_lists[0].get_text().strip()),
        'wish': str(read_lists[1].get_text().strip()),
        'unfinished': str(read_lists[2].get_text().strip()),
        'custom': str(read_lists[3].get_text().strip())
    }
