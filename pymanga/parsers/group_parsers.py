from markdownify import markdownify
import re
from .utils import extract_href_or_text, parse_count


def parse_group(contents, note_format="markdown"):
    """
    Parse group info from mangaupdates.

    Parameters
    ----------
    content : BeautifulSoup
        BeautifulSoup object of the group page content.
    note_format : str, optional
        Format to transform the note into. can be 'plain', 'raw' or 'markdown'. defaults to 'markdown'.

    Returns
    -------
    series : dict
        Series information.
        ::

            {
                'name': 'Group name',
                'IRC': 'IRC link',
                'website': 'link',
                'forum': 'forum link, usually mangadex',
                'discord': 'link to discord server',
                'twitter': 'link to twitter',
                'facebook': 'link to facebook',
                'release_frequency': 'release frequency',
                'number_of_release': 'number of scanlated releases',
                'active': 'the status of the group',
                'total_series' : 'number of scanlated series',
                'genres': 'genre count of scanlated series',
                'categories': 'category count of scanlated series',
                'notes': 'useful information, like previous name'
                'series': [
                    {
                        'id': 'series id',
                        'name': 'series name',
                    }
                ]
                'releases': [
                    # TODO
                ]
            }

    """
    info = contents[0]
    # TODO
    releases = contents[1]
    series = contents[2]

    # info
    info_tags = info.find("div", class_="row").find_all(
        "div", class_="col-6", recursive=False
    )
    try:
        if note_format == "markdown":
            notes = markdownify(str(info_tags[27]))
        elif note_format == "raw":
            notes = str(info_tags[27])
        else:
            notes = info_tags[27].get_text()
    except IndexError:
        notes = ""

    group = dict(
        name=info_tags[1].get_text(),
        IRC=extract_href_or_text(info_tags[3]),
        website=extract_href_or_text(info_tags[5]),
        forum=extract_href_or_text(info_tags[7]),
        discord=extract_href_or_text(info_tags[9]),
        twitter=extract_href_or_text(info_tags[11]),
        facebook=extract_href_or_text(info_tags[13]),
        release_frequency=info_tags[15].get_text(),
        number_of_release=info_tags[17].get_text(),
        active=info_tags[19].get_text(),
        total_series=info_tags[21].get_text(),
        genres=parse_count(info_tags[23].get_text()),
        categories=parse_count(info_tags[25].get_text()),
        notes=notes,
    )

    series_parsed = []
    for s in series.find_all("div", class_="col-6"):
        if s.find("a") is None:
            continue
        id = (
            s.find("a")
            .get("href")
            .replace("https://www.mangaupdates.com/series.html?id=", "")
        )
        name = s.get_text()
        series_parsed.append(dict(id=id, name=name))
    group["series"] = series_parsed

    group["releases"] = []

    return group
