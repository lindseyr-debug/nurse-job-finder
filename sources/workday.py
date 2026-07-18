"""Fetch job postings from a Workday-powered career site's public search API.

This calls the same JSON endpoint the career site's own search page uses
in the browser -- no HTML scraping, no login, no bypassing of any access
controls. Results are the same postings any visitor could see.
"""

import time

import requests

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "nurse-job-finder/1.0 (personal job search tool)",
}


def fetch_jobs(employer, keyword, limit=20):
    """Return a list of normalized job dicts for one employer + keyword search.

    Location filtering happens later (in job_finder.filter_and_score_jobs),
    not here -- some employers (e.g. Advocate Health, now merged with Atrium
    Health across multiple states) need every candidate to reach that more
    complete check, since a plain city-name substring match here would
    wrongly drop real Chicago facilities whose listing text is just
    "<Facility Name> - <Street Address>" with no city in it at all.
    Note: Workday's API rejects limit values above 20 with a 400 error.
    """
    url = f"https://{employer['tenant']}.{employer['host']}.myworkdayjobs.com/wday/cxs/{employer['tenant']}/{employer['site']}/jobs"
    payload = {"appliedFacets": {}, "limit": limit, "offset": 0, "searchText": keyword}

    try:
        response = requests.post(url, json=payload, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"  [warn] {employer['name']}: request failed ({exc})")
        return []

    postings = response.json().get("jobPostings", [])

    jobs = []
    for posting in postings:
        job_url = f"https://{employer['tenant']}.{employer['host']}.myworkdayjobs.com/en-US/{employer['site']}{posting['externalPath']}"
        jobs.append(
            {
                "title": posting.get("title", "Untitled"),
                "hospital": employer["name"],
                "location": posting.get("locationsText", ""),
                "posted": posting.get("postedOn", ""),
                "url": job_url,
                "matched_keyword": keyword,
            }
        )

    return jobs


def fetch_all(employers, keywords):
    all_jobs = []
    for employer in employers:
        for keyword in keywords:
            print(f"  Searching {employer['name']} for '{keyword}'...")
            all_jobs.extend(fetch_jobs(employer, keyword))
            time.sleep(1)  # be polite -- don't hammer their API
    return all_jobs
