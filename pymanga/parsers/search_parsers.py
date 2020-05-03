def parse_releases(list):
    releases = list.find_all('div',class_='text')[:-1]
    results = []

    for i in range(0,len(releases),5):
        release = {}

        release['date'] = str(releases[i].string)

        series_link = releases[i+1]
        if series_link.a is None:
            release['name'] = str(series_link.string)
        else:
            release['name'] = str(series_link.a.string)
            release['id'] = series_link.a['href'].replace('https://www.mangaupdates.com/series.html?id=','')

        release['vol'] = str(releases[i+2].string)
        release['chp'] = str(releases[i+3].string)
        release['group'] = str(releases[i+4].string)

        results.append(release)

    return results

def parse_series(list):
    series = list.find_all('div',class_='text')[:-1]
    results = []

    for i in range(0,len(series),4):
        manga = {}

        series_link = series[i]
        if series_link.a is None:
            manga['name'] = str(series_link.string)
        else:
            manga['name'] = str(series_link.a.string)
            manga['id'] = series_link.a['href'].replace('https://www.mangaupdates.com/series.html?id=','')

        manga['genres'] = str(series[i+1].a.string).replace(' ','').split(',')
        manga['year'] = str(series[i+2].string)
        manga['rating'] = str(series[i+3].string)

        results.append(manga)

    return results

def parse_scanlators(list):
    scanlators = list.find_all('div',class_='text')[:-1]
    results = []

    for i in range(0,len(scanlators),3):
        group = {}

        group_link = scanlators[i]
        if group_link.a is None:
            group['name'] = str(group_link.string)
        else:
            group['name'] = str(group_link.a.string)
            group['id'] = group_link.a['href'].replace('https://www.mangaupdates.com/groups.html?id=','')

        group['active'] = str(scanlators[i+1].string)

        group_contact = scanlators[i+2]
        if group_contact.a is None:
            group['contact'] = str(group_contact.string)
        else:
            group['contact'] = group_contact.a['href']

        results.append(group)

    return results

def parse_authors(list):
    authors = list.find_all('div',class_='text')[:-1]
    results = []

    for i in range(0,len(authors),3):
        author = {}

        author_link = authors[i]
        if author_link.a is None:
            author['name'] = str(author_link.string)
        else:
            author['name'] = str(author_link.a.string)
            author['id'] = author_link.a['href'].replace('https://www.mangaupdates.com/authors.html?id=','')

        author['series'] = str(authors[i+1].string)

        author['genres'] = []

        for gen in authors[i+2].find_all('a'):
            author['genres'].append(str(gen.string))

        results.append(author)

    return results

