"""Search for new grad / ICU / cardiac nursing jobs in Chicago and build a dashboard.

Run manually with:
    python job_finder.py

Or let the scheduled task run it daily -- see README.md for setup.
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

import config
import notifier
from sources import quicklinks, rush, workday

PROJECT_DIR = Path(__file__).parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "output"
DOCS_DIR = PROJECT_DIR / "docs"
SEEN_JOBS_FILE = DATA_DIR / "seen_jobs.json"
DASHBOARD_FILE = OUTPUT_DIR / "dashboard.html"
PUBLISHED_FILE = DOCS_DIR / "index.html"


def load_seen_jobs():
    if SEEN_JOBS_FILE.exists():
        return json.loads(SEEN_JOBS_FILE.read_text())
    return {}


def save_seen_jobs(seen):
    DATA_DIR.mkdir(exist_ok=True)
    SEEN_JOBS_FILE.write_text(json.dumps(seen, indent=2))


def dedupe_jobs(jobs):
    by_url = {}
    for job in jobs:
        by_url[job["url"]] = job
    return list(by_url.values())


def filter_and_score_jobs(jobs):
    """Keep only actual, entry-level, Chicago-proper nursing roles, scored by specialty relevance."""
    relevant = []
    for job in jobs:
        title_lower = job["title"].lower()
        location_lower = job["location"].lower()

        if not any(term in title_lower for term in config.NURSING_TITLE_TERMS):
            continue
        if any(term in title_lower for term in config.EXPERIENCED_LEVEL_TERMS):
            continue
        if any(term in title_lower for term in config.PEDS_EXCLUDE_TERMS):
            continue
        is_chicago = any(term in location_lower for term in config.LOCATION_FILTERS) or any(
            name in location_lower for name in config.CHICAGO_FACILITY_NAMES
        )
        if not is_chicago:
            continue
        if any(term in location_lower for term in config.EXCLUDED_LOCATIONS):
            continue

        job["relevance_score"] = sum(1 for term in config.SPECIALTY_TERMS if term in title_lower)
        relevant.append(job)
    return relevant


def mark_new_jobs(jobs, seen, run_time):
    for job in jobs:
        if job["url"] not in seen:
            seen[job["url"]] = run_time
            job["is_new"] = True
        else:
            job["is_new"] = False
            job["first_seen"] = seen[job["url"]]
    return jobs


def render_dashboard(jobs, quick_links, run_time):
    jobs_sorted = sorted(
        jobs, key=lambda j: (not j["is_new"], -j["relevance_score"], j["hospital"], j["title"])
    )

    job_rows = "\n".join(
        f"""
        <tr class="{'new' if job['is_new'] else ''}" data-job-url="{job['url']}">
            <td>{'🆕 ' if job['is_new'] else ''}{job['title']}</td>
            <td>{job['hospital']}</td>
            <td>{job['location']}</td>
            <td>{job['posted']}</td>
            <td>{'⭐' * job['relevance_score'] if job['relevance_score'] else ''}</td>
            <td><a href="{job['url']}" target="_blank">View &amp; Apply</a></td>
            <td>
                <button type="button" class="status-btn" data-status="applied">Mark Applied</button>
                <button type="button" class="status-btn" data-status="not_interested">Not Interested</button>
            </td>
        </tr>"""
        for job in jobs_sorted
    )

    quick_link_rows = "\n".join(
        f"""<li><a href="{link['url']}" target="_blank">{link['name']}</a>{f" — {link['keyword']}" if link['keyword'] else ''}</li>"""
        for link in quick_links
    )

    new_count = sum(1 for j in jobs if j["is_new"])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Chicago Nursing Job Finder</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Arial, sans-serif; margin: 2rem; background: #f7f7f9; color: #222; }}
  h1 {{ margin-bottom: 0.2rem; }}
  .meta {{ color: #666; margin-bottom: 1.5rem; }}
  table {{ border-collapse: collapse; width: 100%; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  th, td {{ text-align: left; padding: 0.6rem 0.8rem; border-bottom: 1px solid #eee; }}
  th {{ background: #2b3a55; color: white; }}
  tr.new {{ background: #eaf7ea; }}
  a {{ color: #2b3a55; }}
  .section {{ margin-top: 2.5rem; }}
  ul {{ columns: 2; }}
</style>
</head>
<body>
  <h1>Chicago Nursing Job Finder</h1>
  <div class="meta">Last updated: {run_time} &middot; {len(jobs)} live openings found ({new_count} new since last run)</div>

  <p id="hidden-summary" style="display:none;">
    <a href="#" id="show-hidden-link">Show hidden jobs</a> &middot;
    <a href="#" id="clear-hidden-link">Clear all marks</a>
  </p>

  <table>
    <thead>
      <tr><th>Title</th><th>Hospital</th><th>Location</th><th>Posted</th><th>Match</th><th></th><th></th></tr>
    </thead>
    <tbody>
      {job_rows if jobs else '<tr><td colspan="7">No live results from automated sources this run.</td></tr>'}
    </tbody>
  </table>

  <div class="section">
    <h2>Quick search links (other hospitals &amp; job boards)</h2>
    <p>These sites can't be safely auto-searched, so here are direct links pre-filled with relevant search terms.</p>
    <ul>
      {quick_link_rows}
    </ul>
  </div>

  <script>
    (function () {{
      var STORAGE_KEY = 'jobStatuses'; // maps job url to 'applied' or 'not_interested'
      var STATUS_LABELS = {{ applied: 'Applied', not_interested: 'Not interested' }};

      function getStatuses() {{
        try {{ return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{{}}'); }}
        catch (e) {{ return {{}}; }}
      }}
      function saveStatuses(statuses) {{
        localStorage.setItem(STORAGE_KEY, JSON.stringify(statuses));
      }}

      var statuses = getStatuses();
      var rows = document.querySelectorAll('tr[data-job-url]');
      var showingHidden = false;

      function refreshRows() {{
        var hiddenCount = 0;
        rows.forEach(function (row) {{
          var status = statuses[row.getAttribute('data-job-url')];
          if (status) hiddenCount++;
          row.style.display = (status && !showingHidden) ? 'none' : '';
          row.style.opacity = (status && showingHidden) ? '0.5' : '1';
          row.title = status ? STATUS_LABELS[status] : '';
        }});
        document.getElementById('hidden-summary').style.display = hiddenCount > 0 ? 'block' : 'none';
      }}

      rows.forEach(function (row) {{
        row.querySelectorAll('.status-btn').forEach(function (btn) {{
          btn.addEventListener('click', function () {{
            statuses[row.getAttribute('data-job-url')] = btn.getAttribute('data-status');
            saveStatuses(statuses);
            refreshRows();
          }});
        }});
      }});

      document.getElementById('show-hidden-link').addEventListener('click', function (e) {{
        e.preventDefault();
        showingHidden = !showingHidden;
        this.textContent = showingHidden ? 'Hide those jobs again' : 'Show hidden jobs';
        refreshRows();
      }});

      document.getElementById('clear-hidden-link').addEventListener('click', function (e) {{
        e.preventDefault();
        if (confirm('Clear all applied/not-interested marks? This brings back every hidden job.')) {{
          statuses = {{}};
          saveStatuses(statuses);
          refreshRows();
        }}
      }});

      refreshRows();
    }})();
  </script>
</body>
</html>
"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    DASHBOARD_FILE.write_text(html, encoding="utf-8")

    DOCS_DIR.mkdir(exist_ok=True)
    PUBLISHED_FILE.write_text(html, encoding="utf-8")


def publish_to_github_pages(run_time):
    """Commit and push docs/index.html so GitHub Pages serves the latest dashboard."""
    try:
        subprocess.run(["git", "add", "docs/index.html"], cwd=PROJECT_DIR, check=True, capture_output=True)
        result = subprocess.run(
            ["git", "commit", "-m", f"Update dashboard - {run_time}"],
            cwd=PROJECT_DIR, capture_output=True, text=True,
        )
        if "nothing to commit" in result.stdout:
            print("  [publish] No dashboard changes to publish.")
            return
        subprocess.run(["git", "push"], cwd=PROJECT_DIR, check=True, capture_output=True)
        print("  [publish] Dashboard published to GitHub Pages.")
    except subprocess.CalledProcessError as exc:
        print(f"  [publish] Failed to publish dashboard: {exc.stderr}")


def main():
    run_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    print(f"Running job search at {run_time}...")

    jobs = workday.fetch_all(config.WORKDAY_EMPLOYERS, config.SEARCH_KEYWORDS)

    print("  Fetching Rush University Medical Center sitemap...")
    jobs += rush.fetch_jobs()

    jobs = dedupe_jobs(jobs)
    jobs = filter_and_score_jobs(jobs)
    print(f"Found {len(jobs)} matching nursing postings.")

    seen = load_seen_jobs()
    jobs = mark_new_jobs(jobs, seen, run_time)
    save_seen_jobs(seen)

    quick_links = quicklinks.build_quick_links(config.QUICK_LINK_EMPLOYERS, config.SEARCH_KEYWORDS)
    quick_links += quicklinks.build_quick_links(config.GENERAL_BOARDS, config.SEARCH_KEYWORDS)

    render_dashboard(jobs, quick_links, run_time)
    print(f"Dashboard written to {DASHBOARD_FILE}")

    publish_to_github_pages(run_time)

    new_jobs = [j for j in jobs if j["is_new"]]
    notifier.send_new_job_alert(new_jobs)


if __name__ == "__main__":
    main()
