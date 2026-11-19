#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Frédéric Berthommier
# SPDX-License-Identifier: GPL-3.0-or-later
"""notebooklm_sync.py - GitHub -> Google Drive mirror agent for NotebookLM.

Reads notebooklm-manifest.yaml (at the repository root), downloads each
document from its authoritative GitHub raw URL, compares fingerprints with
the files already present in the Drive folder NotebookLM-Corpus/, and
updates ONLY what changed (in-place update, preserving Drive file ids).

GitHub remains the source of truth; Drive is only an operational mirror.

Modes
-----
--dry-run  : no Drive call at all. Downloads the documents from GitHub,
             computes fingerprints, prints the report the real run would
             produce. Also the fallback when credentials are absent.
full mode  : requires GOOGLE_CREDENTIALS (service-account JSON, as a raw
             string or the path of a file) and DRIVE_FOLDER_ID in the
             environment. Never deletes: documents present in Drive but
             absent from the manifest are only REPORTED, with no
             automatic destruction.

Usage: python notebooklm_sync.py [--dry-run] [--report-file report.json]
"""
import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone

import yaml

MANIFEST = os.path.join(os.path.dirname(__file__), "..",
                        "notebooklm-manifest.yaml")
DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.file"]
MIME = {"pdf": "application/pdf",
        "md": "text/markdown",
        "yaml": "application/yaml",
        "docx": "application/vnd.openxmlformats-officedocument"
                ".wordprocessingml.document"}
REPORT = {"started_at": None, "mode": None, "added": [], "updated": [],
          "unchanged": [], "dry-run": [], "removed_from_manifest": [],
          "errors": [], "documents_total": 0}


def log(msg):
    print(datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") + " "
          + msg, flush=True)


def load_manifest(path):
    with open(path, encoding="utf-8") as f:
        m = yaml.safe_load(f)
    assert m.get("manifest_version") == 1, "unsupported manifest_version"
    docs = m.get("documents") or []
    ids = [d["id"] for d in docs]
    assert len(ids) == len(set(ids)), "duplicate ids in manifest"
    return m, docs


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "notebooklm-sync"})
    r = urllib.request.urlopen(req, timeout=300)
    with open(dest, "wb") as f:
        for chunk in iter(lambda: r.read(1 << 20), b""):
            f.write(chunk)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def md5_file(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def drive_connect():
    creds_spec = os.environ.get("GOOGLE_CREDENTIALS", "")
    folder_id = os.environ.get("DRIVE_FOLDER_ID", "")
    if not creds_spec or not folder_id:
        return None, None
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    if os.path.exists(creds_spec):
        with open(creds_spec, encoding="utf-8") as f:
            info = json.load(f)
    else:
        info = json.loads(creds_spec)
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=DRIVE_SCOPES)
    return build("drive", "v3", credentials=creds,
                 cache_discovery=False), folder_id


def drive_list_folder(service, folder_id):
    files = {}
    page_token = None
    q = f"'{folder_id}' in parents and trashed = false"
    while True:
        res = service.files().list(
            q=q, spaces="drive",
            fields="nextPageToken, files(id,name,md5Checksum,size)",
            pageToken=page_token).execute()
        for f in res.get("files", []):
            files[f["name"]] = f
        page_token = res.get("nextPageToken")
        if not page_token:
            return files


def drive_create(service, folder_id, name, local_path, mime):
    from googleapiclient.http import MediaFileUpload
    media = MediaFileUpload(local_path, mimetype=mime, resumable=True)
    return service.files().create(
        body={"name": name, "parents": [folder_id]},
        media_body=media, fields="id,name").execute()


def drive_update(service, file_id, local_path, mime):
    from googleapiclient.http import MediaFileUpload
    media = MediaFileUpload(local_path, mimetype=mime, resumable=True)
    return service.files().update(fileId=file_id, media_body=media,
                                  fields="id,name").execute()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="report only - never talk to Google Drive")
    ap.add_argument("--report-file", default=None,
                    help="write the JSON report to this path")
    ap.add_argument("--manifest", default=MANIFEST)
    a = ap.parse_args()

    REPORT["started_at"] = datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    manifest, docs = load_manifest(a.manifest)
    REPORT["documents_total"] = len(docs)
    notebook_url = (manifest.get("notebook_url") or "").strip()
    log(f"manifest: {len(docs)} documents, notebook_url="
        f"{'set' if notebook_url else 'PENDING (not created yet)'}")

    full_mode = False
    if a.dry_run:
        log("DRY RUN requested - Drive will not be touched")
    else:
        service, folder_id = drive_connect()
        if service is not None:
            full_mode = True
            log(f"Drive folder {folder_id}: connecting")
        else:
            log("credentials absent (GOOGLE_CREDENTIALS/DRIVE_FOLDER_ID) "
                "- falling back to DRY RUN")
            REPORT["errors"].append(
                "Drive credentials absent - ran in dry-run mode")
    REPORT["mode"] = "full" if full_mode else "dry-run"

    drive_files = {}
    if full_mode:
        service, folder_id = drive_connect()
        drive_files = drive_list_folder(service, folder_id)
        log(f"Drive folder: {len(drive_files)} file(s) found")

    workdir = tempfile.mkdtemp(prefix="notebooklm-sync-")
    try:
        for doc in docs:
            did = doc["id"]
            name = doc["path"]
            try:
                local = os.path.join(workdir, name)
                download(doc["url"], local)
                digest = sha256_file(local)
                log(f"{did}: downloaded {name} sha256={digest[:12]}…")

                if not full_mode:
                    state = "dry-run"
                else:
                    existing = drive_files.get(name)
                    if existing is None:
                        drive_create(service, folder_id, name, local,
                                     MIME.get(doc.get("format"),
                                              "application/octet-stream"))
                        state = "added"
                    elif existing.get("md5Checksum") == md5_file(local):
                        state = "unchanged"
                    else:
                        drive_update(service, existing["id"], local,
                                     MIME.get(doc.get("format"),
                                              "application/octet-stream"))
                        state = "updated"
                REPORT[state].append({"id": did, "path": name,
                                      "sha256": digest})
                log(f"{did}: {state}")
            except Exception as exc:
                REPORT["errors"].append(f"{did}: {exc!r}")
                log(f"{did}: ERROR {exc!r}")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    # documents in Drive but no longer in the manifest: report only,
    # NEVER delete automatically.
    if full_mode:
        manifest_names = {d["path"] for d in docs}
        for name in sorted(drive_files):
            if name not in manifest_names:
                REPORT["removed_from_manifest"].append(
                    {"name": name, "drive_id": drive_files[name]["id"],
                     "action": "left in place - manual validation required"})
                log(f"{name}: absent from manifest - LEFT IN PLACE")

    REPORT["finished_at"] = datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    report_json = json.dumps(REPORT, indent=1, ensure_ascii=False)
    if a.report_file:
        with open(a.report_file, "w", encoding="utf-8", newline="\n") as f:
            f.write(report_json)
    print(report_json)

    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a",
                  encoding="utf-8") as f:
            f.write("### NotebookLM sync report\n\n"
                    f"- mode: {REPORT['mode']}\n"
                    f"- documents: {REPORT['documents_total']}\n"
                    f"- added: {len(REPORT['added'])} · "
                    f"updated: {len(REPORT['updated'])} · "
                    f"unchanged: {len(REPORT['unchanged'])} · "
                    f"removed-from-manifest: "
                    f"{len(REPORT['removed_from_manifest'])} · "
                    f"errors: {len(REPORT['errors'])}\n")
    return 0 if not REPORT["errors"] else 1


if __name__ == "__main__":
    sys.exit(main())
