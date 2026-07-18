# Nurse Job Finder

A personal automation that searches for new grad / ICU / cardiac nursing jobs in Chicago and builds a local dashboard of results.

## What it does

- Pulls **live openings** directly from hospitals whose career sites expose a public job-search API: Advocate Health and Ann & Robert H. Lurie Children's Hospital (both via Workday).
- Also pulls live openings from **Rush University Medical Center** via their public sitemap feed (their interactive search page blocks crawlers, but they publish a sitemap specifically for this purpose).
- Filters results down to actual nursing roles and scores them by relevance to critical care / cardiac / ICU specialties.
- Generates ready-to-click **search links** (pre-filled with your keywords) for sites that explicitly disallow automated access via `robots.txt` — Northwestern Medicine (search page blocked) and UChicago Medicine (entire site blocked) — plus UI Health, Indeed, and LinkedIn.
- Marks postings as 🆕 **new** if they weren't found in a previous run, and sends a text alert (optional, see below) when new matches appear.

This tool only *finds and lists* openings — it never fills out or submits an application, and it never fetches from a site whose `robots.txt` says not to. You always review and apply yourself.

## Text notifications (optional)

Copy `.env.example` to `.env` and fill in your own Gmail address, a Gmail
[App Password](https://myaccount.google.com/apppasswords), and your phone's
email-to-SMS gateway address. `.env` is gitignored and never leaves your
machine. Without it, the script just skips sending a text.

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
notifier.py           sends the optional text alert
sources/workday.py    Workday JSON API client
sources/rush.py       Rush sitemap-based job listing fetcher
sources/quicklinks.py generates pre-filled search links
data/seen_jobs.json   tracks which jobs have already been shown (for "new" badges)
output/dashboard.html the generated results page
.env.example          template for text-notification credentials (copy to .env)
```
