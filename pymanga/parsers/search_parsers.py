def parse_releases(list):
    """
    Parse releases from a MangaUpdate's search results page.

    Parameters
    ----------
    list : BeautifulSoup
        BeautifulSoup object of the releases section of the search page.

    Returns
    -------
    releases : list of dicts
        List of recent releases found by the search.
        ::

            [
                {
                    'id': 'Series Id',
                    'name': 'Series name',
                    'chp': 'chapter number',
                    'vol': 'number' or None,
                    'date': '02/21/21', # Date in month/day/year
                    'group': {
                        'name': 'Scanlation Group',
                        'id': 'Scanlation Group Id'
                    }
                }
            ]
    """
    releases = list.find_all("div", class_="text")[:-1]
    results = []

    for i in range(0, len(releases), 5):
        release = {}

        release["date"] = str(releases[i].string)

        series_link = releases[i + 1]
        if series_link.a is None:
            release["name"] = str(series_link.string)
        else:
            release["name"] = str(series_link.a.string)
            release["id"] = series_link.a["href"].replace(
                "https://www.mangaupdates.com/series.html?id=", ""
            )

        vol = releases[i + 2].get_text()
        release["vol"] = vol if vol else None
        release["chp"] = str(releases[i + 3].string)
        release["group"] = {
            "name": releases[i + 4].get_text(),
            "id": releases[i + 4]
            .a["href"]
            .replace("https://www.mangaupdates.com/groups.html?id=", ""),
        }

        results.append(release)

    return results


def parse_series(list):
    """
    Parse series from a MangaUpdate's search results page.

    Parameters
    ----------
    list : BeautifulSoup
        BeautifulSoup object of the series section of the search results page.

    Returns
    -------
    series : list of dicts
        List of manga found by the search.
        ::

            [
                {
                    'name': 'Manga Name',
                    'id': 'Manga Id',
                    'rating': '7.80' # average (?) rating of manga on mangaupdates,
                    'year': '2018', # year manga started releasing
                    'genres': ['Drama', 'Shoujo Ai', 'S...'] # genres this series is a part of
                    # (note: sometimes, the last item of this will be cut off with ...)
                }
            ]
    """

    series = list.find_all("div", class_="text")[:-1]
    results = []

    for i in range(0, len(series), 4):
        manga = {}

        series_link = series[i]
        if series_link.a is None:
            manga["name"] = str(series_link.string)
        else:
            manga["name"] = str(series_link.a.string)
            manga["id"] = series_link.a["href"].replace(
                "https://www.mangaupdates.com/series.html?id=", ""
            )

        manga["genres"] = [
            genre.strip() for genre in series[i + 1].get_text().split(",")
        ]
        manga["year"] = str(series[i + 2].string)
        manga["rating"] = str(series[i + 3].string)

        results.append(manga)

    return results


def parse_scanlators(list):
    """
    Parse scanlation groups from a MangaUpdate's search results page.

    Parameters
    ----------
    list : BeautifulSoup
        BeautifulSoup object of the scanlators section of the search results page.

    Returns
    -------
    scanlators : list of dicts
        List of scanlation groups found by the search.
        ::

            [
                {
                    'name': 'Scanlation Group Name',
                    'id': 'Scanlation Group ID',
                    'active': True or False,
                    'contact': [
                        'contact link',
                        ...
                    ]
                }
            ]
    """
    scanlators = list.find_all("div", class_="text")[:-1]
    results = []

    for i in range(0, len(scanlators), 3):
        group = {}

        group_link = scanlators[i]
        if group_link.a is None:
            group["name"] = str(group_link.string)
        else:
            group["name"] = str(group_link.a.string)
            group["id"] = group_link.a["href"].replace(
                "https://www.mangaupdates.com/groups.html?id=", ""
            )

        group["active"] = True if scanlators[i + 1].get_text() == "Yes" else False

        group_contact = scanlators[i + 2]
        if group_contact.a is None:
            group["contact"] = group_contact.get_text()
        else:
            group["contact"] = [a["href"] for a in group_contact.find_all("a")]

        results.append(group)

    return results


def parse_authors(list):
    """
    Parse authors from a MangaUpdate's search results page.

    Parameters
    ----------
    list : BeautifulSoup
        BeautifulSoup object of the authors section of the search results page.

    Returns
    -------
    series : list of dict
        List of authors found by the search.
        ::

            [
                {
                    'name': 'Author Name',
                    'id': 'ID',
                    'series': int(Number of series author has done),
                    'genres': ['Genre',...] # most numerous genre(s)
                                            # in this author's work
                }
            ]
    """
    authors = list.find_all("div", class_="text")[:-1]
    results = []

    for i in range(0, len(authors), 3):
        author = {}

        author_link = authors[i]
        if author_link.a is None:
            author["name"] = author_link.get_text()
        else:
            author["name"] = author_link.get_text()
            author["id"] = author_link.a["href"].replace(
                "https://www.mangaupdates.com/authors.html?id=", ""
            )

        author["series"] = int(authors[i + 1].get_text())

        author["genres"] = []

        for gen in authors[i + 2].find_all("a"):
            author["genres"].append(gen.get_text())

        results.append(author)

    return results
