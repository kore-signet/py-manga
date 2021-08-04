def parse_releases(content):
    """
    Parse latest releases of a manga

    Parameters
    ----------
    content : BeautifulSoup
        BeautifulSoup object of the releases page content.

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
    releases = content.find_all("div", class_="text", recursive=False)[:-1]
    results = []

    for i in range(0, len(releases), 5):
        release = {}

        release["series"] = {
            "name": releases[i + 1].get_text(),
            "id": releases[i + 1]
            .a["href"]
            .replace("https://www.mangaupdates.com/series.html?id=", ""),
        }

        vol = releases[i + 2].get_text()
        release["vol"] = vol if vol else None
        release["chapter"] = releases[i + 3].get_text()
        release["group"] = {
            "name": releases[i + 4].get_text(),
            "id": releases[i + 4]
            .a["href"]
            .replace("https://www.mangaupdates.com/groups.html?id=", ""),
        }
        results.append(release)

    return results
