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
# Chicago proper only -- not the wider Illinois suburbs.
LOCATION_FILTERS = ["chicago"]

# Never show postings at these locations, even if they otherwise match
# (checked against title + location text combined, case-insensitive).
# The UChicago Medicine entries are satellite/suburb clinics in their system
# (Ingalls network south suburbs + NW Indiana) that get named in the job
# title rather than a dedicated location field.
EXCLUDED_LOCATIONS = [
    "oak park",
    "orland park", "harvey", "flossmoor", "matteson", "tinley park",
    "crown point", "merrillville", "munster", "dyer", "schererville",
]

# Some employers list single-location jobs as just "<Facility Name> -
# <Street Address>" or "<Org Name> | <Dept>", with no city/state text at
# all -- so the literal "chicago" check in LOCATION_FILTERS misses real
# Chicago facilities. These are known facility/org names that are actually
# within Chicago city limits: Advocate Illinois Masonic and Advocate
# Trinity (per advocatehealth.com; the rest of Advocate's system, e.g.
# Lutheran General, Sherman, Christ Medical Center, is suburban and
# correctly stays excluded), and University of Chicago Medical Center's
# main Hyde Park campus (their satellite/suburb clinics are excluded above
# via EXCLUDED_LOCATIONS instead, since they're named in the title).
# Deliberately NOT including "UCM Medical Group" -- that's their outpatient
# clinic network spread across many suburbs with no city given, so it's
# excluded by default rather than risk showing a suburb as a false match.
CHICAGO_FACILITY_NAMES = [
    "illinois masonic", "advocate trinity",
    "university of chicago medical center", "uchicago medicine",
]

# A job title must contain at least one of these to be considered a nursing role at all.
NURSING_TITLE_TERMS = ["nurse", " rn ", "rn,", "rn-", "rn(", "(rn)"]

# Terms that boost a job's relevance score based on Lindsey's specialty background.
SPECIALTY_TERMS = [
    "icu", "critical care", "cardiac", "cardiovascular", "cvicu", "micu",
    "cardiology", "telemetry", "new grad", "residency", "graduate nurse",
]

# Many hospitals (Rush included) use a clinical ladder: RN 1 / new grad,
# RN 2+ requires prior experience. Exclude titles indicating an experience
# level above entry, since Lindsey is a new grad.
EXPERIENCED_LEVEL_TERMS = [
    "registered nurse 2", "registered nurse 3", "registered nurse ii", "registered nurse iii",
    "rn 2", "rn 3", "rn2", "rn3", "rn ii", "rn iii",
    "experienced",
]

# Hospitals with a working Workday JSON search API -> fully automated results.
# Ann & Robert H. Lurie Children's Hospital removed -- it's a pediatric
# hospital and every posting there is a peds role, which isn't relevant.
WORKDAY_EMPLOYERS = [
    {
        "name": "Advocate Health",
        "tenant": "aah",
        "host": "wd5",
        "site": "External",
    },
]

# Exclude pediatric/peds roles from any employer (e.g. Rush's PICU/NICU units).
PEDS_EXCLUDE_TERMS = ["pediatric", "peds", "picu", "nicu", "children's", "neonatal"]

# Hospitals/boards without a scrapable API -> generate direct search links instead.
# Northwestern Medicine's robots.txt disallows crawling /search-jobs/.
# UChicago Medicine moved off this list -- their real application system
# (Oracle Cloud, see sources/uchicago.py) has no robots.txt restriction.
QUICK_LINK_EMPLOYERS = [
    {
        "name": "Northwestern Medicine",
        "url_template": "https://jobs.nm.org/search-jobs/{query}",
    },
    {
        "name": "UI Health",
        "url_template": "https://hospital.uillinois.edu/about-ui-health/career-opportunities",
    },
]

# Published GitHub Pages URL -- linked from text alerts so you can view the
# full dashboard from your phone.
DASHBOARD_URL = "https://lindseyr-debug.github.io/nurse-job-finder/"

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
