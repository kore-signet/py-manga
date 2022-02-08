import re


def parse_results(soup):
    """
    Parse search results from the advanced search page.

    Parameters
    ----------
    content : BeautifulSoup
        BeautifulSoup object of the search page content.

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
    """
    results = []
    for series in soup.find_all("div", attrs={"class": "col-12 col-lg-6 p-3 text"}):
        box = series.div.find_all("div", recursive=False)

        info = box[1].div.find_all("div", recursive=False)

        ratings_text = re.search(
            r"(?P<year>\d{4})*(?: - )*(?:(?P<rating>\d+\.(\d+)) \/ 10\.0)*",
            info[3].get_text(),
        )

        thumbnail = box[0].find("img")
        is_adult = False
        if not thumbnail:
            is_adult = bool(box[0].find(lambda tag: tag.get_text() == "AdultContent"))
        else:
            thumbnail = thumbnail["src"]
            # when a manga is considered to contain 'Adult Content', mangaupdates replaces the thumbnail with a divsoup that renders to a centered 'Adult Content' on a white background.

        results.append(
            {
                "name": info[0].find("a", dict(href=True)).u.b.get_text(),
                "id": info[0]
                .find("a", dict(href=True))["href"]
                .replace("https://www.mangaupdates.com/series.html?id=", ""),
                "genres": info[1].a["title"].split(", "),
                "summary": info[2].get_text(),
                "year": ratings_text.group("year"),
                "rating": ratings_text.group("rating"),
                "thumbnail": thumbnail,
                "is_adult": is_adult,
            }
        )
    return results
