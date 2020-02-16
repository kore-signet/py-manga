def parse_releases(content):
    releases = content.find_all('div',class_='text',recursive=False)[:-1]
    results = []

    for i in range(0,len(releases),5):
        release = {}
        release['series'] = {
            'name': str(releases[i+1].a.string),
            'id': releases[i+1].a['href'].replace('https://www.mangaupdates.com/series.html?id=','')
        }
        release['vol'] = str(releases[i+2].string)
        release['chapter'] = str(releases[i+3].string)
        release['group'] = {
            'name': str(releases[i+4].a.string),
            'id': releases[i+4].a['href'].replace('https://www.mangaupdates.com/groups.html?id=','')
        }
        results.append(release)

    return results
