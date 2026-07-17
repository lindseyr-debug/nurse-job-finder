"""Generate pre-filled search links for sites that can't be safely scraped."""

from urllib.parse import quote


def build_quick_links(employers, keywords):
    """Return a list of {name, keyword, url} for one representative keyword per employer."""
    links = []
    for employer in employers:
        template = employer["url_template"]
        if "{query}" in template:
            for keyword in keywords:
                links.append(
                    {
                        "name": employer["name"],
                        "keyword": keyword,
                        "url": template.format(query=quote(keyword)),
                    }
                )
        else:
            links.append({"name": employer["name"], "keyword": None, "url": template})
    return links
