"""Search configuration: keywords, target hospitals, and location filter."""

# Keywords reflecting Lindsey's background: new grad + ICU/critical care/cardiac focus.
SEARCH_KEYWORDS = [
    "new grad nurse residency",
    "graduate nurse ICU",
    "critical care nurse",
    "cardiac ICU nurse",
    "cardiovascular nurse",
    "telemetry nurse",
    "MICU nurse",
]

# Only keep results whose location text contains one of these (case-insensitive).
LOCATION_FILTERS = ["chicago", ", il", "illinois"]

# A job title must contain at least one of these to be considered a nursing role at all.
NURSING_TITLE_TERMS = ["nurse", " rn ", "rn,", "rn-", "rn(", "(rn)"]

# Terms that boost a job's relevance score based on Lindsey's specialty background.
SPECIALTY_TERMS = [
    "icu", "critical care", "cardiac", "cardiovascular", "cvicu", "micu",
    "cardiology", "telemetry", "new grad", "residency", "graduate nurse",
]

# Hospitals with a working Workday JSON search API -> fully automated results.
WORKDAY_EMPLOYERS = [
    {
        "name": "Advocate Health",
        "tenant": "aah",
        "host": "wd5",
        "site": "External",
    },
    {
        "name": "Ann & Robert H. Lurie Children's Hospital",
        "tenant": "luriechildrens",
        "host": "wd1",
        "site": "externalportal",
    },
]

# Hospitals/boards without a scrapable API -> generate direct search links instead.
QUICK_LINK_EMPLOYERS = [
    {
        "name": "Northwestern Medicine",
        "url_template": "https://jobs.nm.org/search-jobs/{query}",
    },
    {
        "name": "Rush University Medical Center",
        "url_template": "https://rush.fxrecruiter.com/?q={query}",
    },
    {
        "name": "UChicago Medicine",
        "url_template": "https://careers-ucm.icims.com/jobs/search?ss=1&searchKeyword={query}",
    },
    {
        "name": "UI Health",
        "url_template": "https://hospital.uillinois.edu/about-ui-health/career-opportunities",
    },
]

GENERAL_BOARDS = [
    {
        "name": "Indeed",
        "url_template": "https://www.indeed.com/jobs?q={query}&l=Chicago%2C+IL",
    },
    {
        "name": "LinkedIn",
        "url_template": "https://www.linkedin.com/jobs/search/?keywords={query}&location=Chicago%2C%20Illinois",
    },
]
