import markdownify

def parse_series(content):
    manga = {}
    manga['title'] = str(content.find('span',class_='releasestitle').string)

    cols = content.find_all('div',class_='col-6',recursive=False)
    col_1 = cols[0]
    col_2 = cols[1]

    parse_col_1(col_1,manga)
    parse_col_2(col_2,manga)
    return manga

def parse_col_1(col,manga):
    contents = col.find_all('div',class_='sContent',recursive=False)

    manga['description'] = markdownify.markdownify(contents[0].encode_contents())
    manga['type'] = str(contents[1].string).replace('\n','')
    manga['related_series'] = str(contents[2].string).replace('\n','')
    manga['associated_names'] = str(contents[3].string).replace('\n','')
    if contents[4].a is None:
        manga['group'] = {'name': str(contents[4].string)}
    else:
        manga['group'] = {'name': str(contents[4].a.string), 'id': contents[4].a['href'].replace('https://www.mangaupdates.com/groups.html?id=','')}

    manga['latest_releases'] = []
    numbers = contents[5].find_all('i')[:-1]
    groups = contents[5].find_all('a')[:-1]
    dates = contents[5].find_all('span')

    for i in range(0,len(dates)):
        release = {
            'group': {
                'name': str(groups[i].string),
                'id': str(groups[i]['href'].replace('https://www.mangaupdates.com/groups.html?id=',''))
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


    manga['status'] = str(contents[6].string).replace('\n','')
    if str(contents[7].string).replace('\n','') == 'No':
        manga['completely_scanlated'] = False
    else:
        manga['completely_scanlated'] = True
    manga['anime_chapters'] = str(contents[8].string).replace('\n','')
    manga['user_reviews'] = str(contents[9].string).replace('\n','')

    manga['forum'] = {
        'status': str(contents[10].string),
        'link': 'https://www.mangaupdates.com/' + contents[10].a['href']
    }

    average_raw = contents[11].contents
    manga['average'] = {
        'average': str(average_raw[0]).replace('Average:','').replace(' ',''),
        'votes': str(average_raw[2]).replace('(','').replace(')',''),
        'bayesian': str(average_raw[5]).replace('<b>','').replace('</b>','')
    }

    manga['last_updated'] = str(contents[12].string).replace('\n','')

def parse_col_2(col,manga):
    contents = col.find_all('div',class_='sContent',recursive=False)

    manga['image'] = contents[0].center.img['src']

    manga['genres'] = []
    for genre in contents[1].find_all('a')[:-1]:
        manga['genres'].append(str(genre.u.string))

    manga['categories'] = []
    for cat_raw in contents[2].div.ul.find_all('li'):
        cat = cat_raw.find('a',rel='nofollow')
        manga['categories'].append({
            'category': str(cat.string),
            'score': str(cat['title']).replace('Score:','')
        })

    manga['category_recs'] = []
    for rec in contents[3].find_all('a'):
        manga['category_recs'].append({
            'name': str(rec.u.string),
            'id': rec['href'].replace('series.html?id=','')
        })

    manga['recs'] = str(contents[4].string).replace('\n','')

    manga['authors'] = []
    for author in contents[5].find_all('a'):
        manga['authors'].append({
            'name': str(author.u.string),
            'id': author['href'].replace('https://www.mangaupdates.com/authors.html?id=','')
        })

    manga['artists'] = []
    for artist in contents[6].find_all('a'):
        manga['artists'].append({
            'name': str(artist.u.string),
            'id': artist['href'].replace('https://www.mangaupdates.com/authors.html?id=','')
        })

    manga['year'] = str(contents[7].string).replace('\n','')

    manga['publisher'] = {
        'name': str(contents[8].a.u.string),
        'id': contents[8].a['href'].replace('https://www.mangaupdates.com/publishers.html?id=','')
    }

    # TODO: add publisher info
    manga['serialized'] = {
        'name': str(contents[9].a.u.string),
        'link': 'https://www.mangaupdates.com/' + contents[9].a['href']
    }

    manga['licensed'] = str(contents[10].string).replace('\n','')

    # TODO: add volume/ongoing info
    manga['english_publisher'] = {
        'name': str(contents[11].get_text()),
        'id': str(contents[11].a['href'].replace('https://www.mangaupdates.com/publishers.html?id=','') if contents[11].a else None)
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

    read_lists = contents[13].find_all('a')
    manga['reading_lists'] = {
        'reading': str(read_lists[0].u.string),
        'wish': str(read_lists[1].u.string),
        'unfinished': str(read_lists[2].u.string),
        'custom': str(read_lists[3].u.string)
    }
