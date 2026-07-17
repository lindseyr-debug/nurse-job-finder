"""Fetch Rush University Medical Center job postings from their public sitemap.

Rush's interactive search page is disallowed for crawlers in robots.txt, but
they publish a sitemap feed specifically for crawling (referenced in their
own robots.txt), which lists every individual job posting URL. That's what
this reads -- no search endpoint is touched, no bot-detection is bypassed.
"""

import re
from urllib.parse import unquote

import requests

SITEMAP_URL = "https://rush.fxrecruiter.com/feeds/xml-sitemap"
DETAIL_PATTERN = re.compile(
    r"<loc>(https://rush\.fxrecruiter\.com/jobs/details/united-states/il/([a-z-]+)/[^<]+/(\d+))</loc>"
)

ACRONYMS = {"rn", "icu", "cso", "ed", "crna", "np", "picu", "nicu", "micu", "cvicu", "bmt", "cna", "lpn", "or"}
HEADERS = {"User-Agent": "nurse-job-finder/1.0 (personal job search tool)"}


def _slug_to_title(url):
    # e.g. .../chicago/work-type/registered-nurse-2-float-cso-icu/6964 -> "Registered Nurse 2 Float Cso Icu"
    slug = url.rstrip("/").rsplit("/", 2)[-2]
    words = unquote(slug).split("-")
    return " ".join(w.upper() if w.lower() in ACRONYMS else w.capitalize() for w in words)


def _city_to_location(city_slug):
    return ", ".join([" ".join(w.capitalize() for w in city_slug.split("-")), "IL"])


def fetch_jobs():
    try:
        response = requests.get(SITEMAP_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"  [warn] Rush: sitemap request failed ({exc})")
        return []

    jobs = []
    for url, city_slug, job_id in DETAIL_PATTERN.findall(response.text):
        jobs.append(
            {
                "title": _slug_to_title(url),
                "hospital": "Rush University Medical Center",
                "location": _city_to_location(city_slug),
                "posted": "",
                "url": url,
                "matched_keyword": None,
            }
        )
    return jobs
