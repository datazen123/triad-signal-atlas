"""Tells a human when the pipeline needs attention, and only then.

- Opens one GitHub issue labelled 'pipeline-health' that @mentions the repo
  owner. GitHub emails the owner for new issues, comments and @mentions.
- Adds a comment only when the set of problems changes (no daily spam).
- Comments and closes the issue automatically once everything recovers.
- Optional direct email over SMTP when these repository secrets exist:
  SMTP_HOST, SMTP_PORT (default 465), SMTP_USER, SMTP_PASS, ALERT_TO.

Usage: python pipeline/notify.py --job-status success|failure|cancelled
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import smtplib
import ssl
import sys
import urllib.request
from email.message import EmailMessage
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ATLAS_NAME, DATA, read_json  # noqa: E402

LABEL = "pipeline-health"
API = "https://api.github.com"


def gh(method, path, body=None):
    token, repo = os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPOSITORY")
    if not token or not repo:
        return None
    req = urllib.request.Request(
        f"{API}/repos/{repo}{path}", method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "triad-atlas-bot"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
        return json.loads(raw) if raw else None


def send_email(subject: str, body: str) -> bool:
    host, to = os.environ.get("SMTP_HOST"), os.environ.get("ALERT_TO")
    if not host or not to:
        return False
    msg = EmailMessage()
    msg["Subject"], msg["From"], msg["To"] = subject, os.environ.get("SMTP_USER", to), to
    msg.set_content(body)
    port = int(os.environ.get("SMTP_PORT", "465"))
    with smtplib.SMTP_SSL(host, port, context=ssl.create_default_context(), timeout=30) as s:
        if os.environ.get("SMTP_USER"):
            s.login(os.environ["SMTP_USER"], os.environ.get("SMTP_PASS", ""))
        s.send_message(msg)
    return True


def render(alerts, job_status, run_url, owner):
    lines = [f"@{owner} the {ATLAS_NAME} pipeline needs a look.", ""]
    if job_status not in ("success", None):
        lines += [f"**Workflow run ended with `{job_status}`.** The site was not redeployed; "
                  f"the previous version stays online. Log: {run_url}", ""]
    if alerts:
        lines += ["| Collector | Status | Failures in a row | Stale | Last error |", "|---|---|---|---|---|"]
        for a in alerts:
            err = (a.get("error") or "").replace("|", "/").replace("\n", " ")[:220]
            lines.append(f"| `{a['collector']}` | {a.get('status')} | {a.get('consecutive_failures')} | "
                         f"{'yes' if a.get('stale') else 'no'} | {err} |")
        lines += ["", "What already happened automatically: retries with backoff, alternative endpoints, "
                  "last-known-good data kept on the page, quarantined suspect results in `data/live/quarantine/`, "
                  "and a weekly back-off for collectors that keep failing.",
                  "", "Typical fix: an upstream API changed its URL or field names. Edit the collector in "
                  "`pipeline/collectors/`, run `python pipeline/doctor.py --only <name>` locally, and push. "
                  "This issue closes itself after the next clean run."]
    lines += ["", f"Run: {run_url}"]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--job-status", default="success")
    args = ap.parse_args(argv)

    health = read_json(DATA / "health.json", {}) or {}
    alerts = health.get("alerts", [])
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    owner = repo.split("/")[0] if repo else "owner"
    run_url = f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{repo}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"
    broken = bool(alerts) or args.job_status not in ("success",)

    fingerprint = hashlib.sha1(json.dumps(
        [[a["collector"], a.get("status"), bool(a.get("stale"))] for a in alerts] + [args.job_status],
        sort_keys=True).encode()).hexdigest()[:12]
    marker = f"<!-- fingerprint:{fingerprint} -->"

    try:
        issues = gh("GET", f"/issues?state=open&labels={LABEL}&per_page=5") or []
    except Exception as e:  # noqa: BLE001
        print(f"GitHub API unavailable ({e}); falling back to email only")
        issues = None
    issue = issues[0] if issues else None

    if broken:
        body = render(alerts, args.job_status, run_url, owner) + "\n\n" + marker
        changed = not issue or marker not in (issue.get("body") or "")
        if issues is not None:
            if issue is None:
                gh("POST", "/issues", {"title": "Atlas pipeline needs attention", "body": body, "labels": [LABEL]})
                print("opened issue")
            elif changed:
                gh("PATCH", f"/issues/{issue['number']}", {"body": body})
                gh("POST", f"/issues/{issue['number']}/comments", {"body": f"@{owner} the problem set changed:\n\n" + body})
                print("updated issue")
            else:
                print("issue already describes this problem; staying quiet")
        if changed:
            try:
                if send_email(f"{ATLAS_NAME}: pipeline needs attention", body.replace(marker, "")):
                    print("email sent")
            except Exception as e:  # noqa: BLE001
                print(f"email failed: {e}")
    elif issue:
        gh("POST", f"/issues/{issue['number']}/comments", {"body": "All collectors recovered and the site deployed. Closing automatically."})
        gh("PATCH", f"/issues/{issue['number']}", {"state": "closed", "state_reason": "completed"})
        print("closed recovered issue")
        try:
            send_email(f"{ATLAS_NAME}: recovered", "All collectors are healthy again.\n" + run_url)
        except Exception as e:  # noqa: BLE001
            print(f"email failed: {e}")
    else:
        print("all healthy")
    return 0


if __name__ == "__main__":
    sys.exit(main())
