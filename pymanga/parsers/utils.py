import re


def extract_href_or_text(content):
    if content.find("a") is not None:
        return content.find("a").get("href")
    else:
        return content.get_text()


def extract_img_or_text(content):
    if content.find("img") is not None:
        return content.find("img").get("src")
    else:
        return content.get_text()


def parse_count(text):
    result = dict()
    categories = text.split(",")
    for cat in categories:
        if len(cat) == 0:
            continue
        parsed = re.search("([^()]+)\(([^()]+)\)", cat)
        name = parsed.group(1).strip()
        count = parsed.group(2).strip()
        result[name] = int(count)
    return result


def map_none(val, f):
    return f(val) if val is not None else None


def get_content_by_title(tag, title):
    return tag.find("div", class_="sCat", string=title).find_next(
        "div", class_="sContent"
    )
