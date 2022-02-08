from .utils import (
    map_none,
    extract_href_or_text,
    extract_img_or_text,
    get_content_by_title,
)
import markdownify
import html2text


def parse_genres(tag):
    genres = {}
    for link in tag.find_all("a"):
        genres[link.get_text()] = int(
            link.next_sibling.get_text().replace("(", "").replace(")", "")
        )
    return genres


def parse_author(soup, desc_format="plain"):
    author = {}
    author["header_name"] = soup.find(
        "span", class_=["releasestitle", "tabletitle"]
    ).get_text()
    # content that is just either text or a link
    normal_content = [
        ("name", "Name (in native language)"),
        ("birth_place", "Birth Place"),
        ("birth_date", "Birth Date"),
        ("zodiac", "Zodiac"),
        ("last_updated", "Last Updated"),
        ("blood_type", "Blood Type"),
        ("gender", "Gender"),
        ("website", "Official Website"),
        ("twitter", "Twitter"),
        ("facebook", "Facebook"),
    ]
    for (key, title) in normal_content:
        author[key] = map_none(get_content_by_title(soup, title), extract_href_or_text)

    author["image"] = map_none(get_content_by_title(soup, "Image"), extract_img_or_text)
    genres = get_content_by_title(soup, "Genres")
    if genres:
        author["genres"] = parse_genres(genres)
    else:
        author["genres"] = None

    desc = get_content_by_title(soup, "Comments")
    try:
        if desc_format == "markdown":
            desc = markdownify(str(desc))
        elif desc_format == "raw":
            desc = str(desc)
        elif desc_format == "plain":
            text_converter = html2text.HTML2Text()
            text_converter.ignore_links = True
            text_converter.unicode_snob = True
            text_converter.ignore_emphasis = True
            text_converter.ignore_anchors = True
            text_converter.ignore_images = True
            desc = text_converter.handle(str(desc))
        else:
            desc = desc.get_text()
    except IndexError:
        desc = ""

    author["comments"] = desc
    author["associated_names"] = [
        markdownify.markdownify(name)
        for name in get_content_by_title(soup, "Associated Names")
        .encode_contents()
        .decode("utf-8")
        .replace("\n", "")
        .replace("</br>", "")
        .split("<br>")
        if len(name) > 0 and name != "N/A"
    ]

    # find the "Series Title (Click for series info)" div as a marker to navigate the rest of the series table. cut out the headers and the footer note
    series_table = (
        soup.find("a", string="Series Title")
        .find_parent("div")
        .find_next_siblings("div")[2:-1]
    )
    author_series = []
    i = 0
    while i < len(series_table):
        series = {}
        series["title"] = series_table[i].get_text()
        series_link = series_table[i].find("a")
        if series_link:
            series["id"] = series_link["href"].replace(
                "https://www.mangaupdates.com/series.html?id=", ""
            )
        else:
            series["id"] = None

        series["genres"] = [
            text.strip() for text in series_table[i + 1].get_text().split(",")
        ]
        series["year"] = series_table[i + 2].get_text()
        author_series.append(series)
        i += 3

    author["series"] = author_series

    return author
