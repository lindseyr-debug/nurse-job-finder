"""Fetch job postings from UChicago Medicine's Oracle Cloud recruiting site.

This is their actual current application system (the nursing-careers page
on uchicagomedicine.org links here) -- separate from the older iCIMS site,
which is still linked from some pages but whose robots.txt disallows all
crawling. This Oracle Cloud host has no robots.txt at all, and this calls
the same public JSON API their own search page uses in the browser.
"""

import requests

HOST = "https://fa-etnf-saasfaprod1.fa.ocs.oraclecloud.com"
SITE_NUMBER = "CX_1001"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "nurse-job-finder/1.0 (personal job search tool)",
}


def fetch_jobs(keyword, limit=25):
    """Return a list of normalized job dicts for one keyword search."""
    finder = f"findReqs;siteNumber={SITE_NUMBER},keyword={keyword},facetsList=LOCATIONS;limit={limit};offset=0"
    url = f"{HOST}/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
    params = {"onlyData": "true", "expand": "requisitionList", "finder": finder}

    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"  [warn] UChicago Medicine: request failed ({exc})")
        return []

    items = response.json().get("items", [])
    if not items:
        return []

    jobs = []
    for req in items[0].get("requisitionList", []):
        jobs.append(
            {
                "title": req.get("Title", "Untitled"),
                "hospital": "University of Chicago Medicine",
                # ShortDescriptionStr carries the real department/campus text;
                # PrimaryLocation from this API is only ever state-level.
                "location": req.get("ShortDescriptionStr", "") or req.get("PrimaryLocation", ""),
                "posted": req.get("PostedDate", ""),
                "url": f"{HOST}/hcmUI/CandidateExperience/en/sites/{SITE_NUMBER}/job/{req['Id']}",
                "matched_keyword": keyword,
            }
        )
    return jobs


def fetch_all(keywords):
    all_jobs = []
    for keyword in keywords:
        print(f"  Searching UChicago Medicine for '{keyword}'...")
        all_jobs.extend(fetch_jobs(keyword))
    return all_jobs
