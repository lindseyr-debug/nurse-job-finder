# Nurse Job Finder

A personal automation that searches for new grad / ICU / cardiac nursing jobs in Chicago and builds a local dashboard of results.

## What it does

- Pulls **live openings** directly from hospitals whose career sites expose a public job-search API (currently Advocate Health and Ann & Robert H. Lurie Children's Hospital, both via Workday).
- Filters results down to actual nursing roles and scores them by relevance to critical care / cardiac / ICU specialties.
- Generates ready-to-click **search links** (pre-filled with your keywords) for hospitals and job boards that can't be safely auto-searched: Northwestern Medicine, Rush, UChicago Medicine, UI Health, Indeed, and LinkedIn.
- Marks postings as 🆕 **new** if they weren't found in a previous run.

This tool only *finds and lists* openings — it never fills out or submits an application. You always review and apply yourself.

## Usage

Run manually any time:

```
python job_finder.py
```

Then open `output/dashboard.html` in a browser.

It's also set up to run automatically every day at 8:00 AM via Windows Task Scheduler (task name: `NurseJobFinder`). Check or change the schedule with:

```
Get-ScheduledTask -TaskName "NurseJobFinder"
```

## Customizing

Edit `config.py` to change:
- `SEARCH_KEYWORDS` — the search terms used per employer
- `NURSING_TITLE_TERMS` / `SPECIALTY_TERMS` — what counts as a nursing role and what boosts relevance
- `WORKDAY_EMPLOYERS` — add more hospitals here if they also run on Workday (test with `sources/workday.py` first)
- `QUICK_LINK_EMPLOYERS` / `GENERAL_BOARDS` — the quick-link sites

## Project structure

```
config.py            search keywords, employer list, location filter
job_finder.py         main script: fetch, filter, score, render dashboard
sources/workday.py    Workday JSON API client
sources/quicklinks.py generates pre-filled search links
data/seen_jobs.json   tracks which jobs have already been shown (for "new" badges)
output/dashboard.html the generated results page
```
