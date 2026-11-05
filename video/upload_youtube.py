#!/usr/bin/env python3
"""Upload the tutorial video to YouTube (Data API), with subtitles and a thumbnail.

    python upload_youtube.py --auth                  # one-time browser sign-in, saves .secrets/youtube_token.json
    python upload_youtube.py --check                 # sign-in check only: shows the channel, uploads nothing
    python upload_youtube.py                         # upload as PRIVATE (default)
    python upload_youtube.py --privacy unlisted

Uses its own token in .secrets/ (gitignored). The OAuth client is the ECCU one by default (CLIENT env var).
The ECCU token is never read or modified.
Quota: video insert 1600 + captions 400 + thumbnail 50 units of the 10,000 daily.
"""
import argparse
import os
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
VIDEO, SRT, THUMB = OUT / "aws_cis_assessment_tutorial.mp4", OUT / "aws_cis_assessment_tutorial.srt", OUT / "thumbnail.png"
TOKEN = Path(os.environ.get("TOKEN", ROOT / ".secrets" / "youtube_token.json"))
CLIENT = Path(os.environ.get("CLIENT", Path.home() / "Videos/ECCU/CCSE/.secrets/cloud_client_secret.json"))
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

TITLE = "AWS Cloud Security Posture Assessment: CIS Benchmark Remediation, Start to Finish"
INTRO = """A complete walkthrough of a cloud security engagement: assess an AWS account against the CIS AWS Foundations Benchmark v4.0, triage by real risk, fix what matters most with Terraform, and prove the improvement. 62 failing checks down to 38, with the challenges, the mistakes and the lessons left in.

Covered: requirements and scope, the builder vs scanner identity split, a deliberately misconfigured Terraform sandbox, Prowler and ScoutSuite, severity vs priority triage, false-positive tuning with a justified mutelist, a remediation backlog mapped to CIS, NIST CSF and ISO 27001, remediation, verification, and a safe teardown.

Eight real challenges and how each was solved: the wrong default profile, a builder with no rights, a baseline that skipped security groups, ScoutSuite crashing on a new Python, a gap in Prowler's per-port checks, Terraform ignoring removed rule blocks, a stale IAM credential report, and a destroy that would have undone real fixes.

Everything shown ran in a training environment. The client (VaultBridge Financial) is simulated and every misconfiguration was planted on purpose. The AWS account ID is not shown.
"""
TAGS = ["AWS security", "CIS benchmark", "CIS AWS Foundations", "cloud security", "Prowler", "ScoutSuite", "Terraform",
        "CSPM", "AWS IAM", "cloud security posture management", "DevSecOps", "security tutorial", "misconfiguration"]


def authorise():
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT), SCOPES)
    c = flow.run_local_server(port=0, prompt="consent", access_type="offline",
                              authorization_prompt_message="Open this URL and choose the channel to upload to:\n{url}")
    TOKEN.parent.mkdir(exist_ok=True)
    TOKEN.write_text(c.to_json())
    TOKEN.chmod(0o600)
    print(f"saved {TOKEN}")


def creds():
    if not TOKEN.exists():
        raise SystemExit("Not signed in. Run: python upload_youtube.py --auth")
    c = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if not c.valid:
        c.refresh(Request())
        TOKEN.write_text(c.to_json())
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--auth", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"])
    a = ap.parse_args()
    if a.auth:
        return authorise()
    yt = build("youtube", "v3", credentials=creds(), cache_discovery=False)
    ch = yt.channels().list(part="snippet", mine=True).execute()["items"][0]
    print(f"channel: {ch['snippet']['title']}  ({ch['id']})")
    if a.check:
        return
    chapters = (OUT / "chapters.txt").read_text()
    desc = f"{INTRO}\nChapters\n{chapters}"
    body = {"snippet": {"title": TITLE, "description": desc, "tags": TAGS, "categoryId": "27", "defaultLanguage": "en",
                        "defaultAudioLanguage": "en"},
            "status": {"privacyStatus": a.privacy, "selfDeclaredMadeForKids": False, "embeddable": True}}
    media = MediaFileUpload(str(VIDEO), mimetype="video/mp4", chunksize=8 * 1024 * 1024, resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        st, resp = req.next_chunk()
        if st:
            print(f"  uploaded {int(st.progress() * 100)}%", flush=True)
    vid = resp["id"]
    print(f"video: https://www.youtube.com/watch?v={vid}  privacy={resp['status']['privacyStatus']}")
    try:
        yt.captions().insert(part="snippet", body={"snippet": {"videoId": vid, "language": "en", "name": "English", "isDraft": False}},
                             media_body=MediaFileUpload(str(SRT), mimetype="application/octet-stream")).execute()
        print("captions: uploaded")
    except HttpError as e:
        print("captions: FAILED", e.resp.status, str(e)[:160])
    if THUMB.exists():
        try:
            yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(THUMB), mimetype="image/png")).execute()
            print("thumbnail: set")
        except HttpError as e:
            print("thumbnail: FAILED", e.resp.status, str(e)[:160])


if __name__ == "__main__":
    sys.exit(main())
