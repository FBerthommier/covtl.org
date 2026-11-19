# NOTEBOOKLM-SETUP.md — one-time configuration

Do these steps in order. Steps 1–4 need the site owner's Google account;
step 5 is done by the maintainer in the GitHub settings.

## 1. Create the Drive mirror folder

1. In Google Drive, create a folder named exactly **`NotebookLM-Corpus/`**.
2. Note its **folder id** — the last segment of its URL:
   `https://drive.google.com/drive/folders/<DRIVE_FOLDER_ID>`.

## 2. Create the Google service account

1. Google Cloud Console → create (or pick) a project → enable the
   **Google Drive API**.
2. IAM → Service Accounts → create one (e.g. `notebooklm-sync`).
3. Keys → add key → JSON: a private key file is downloaded. Treat it as
   a password.
4. The agent only needs the `drive.file` scope: it sees just the folder
   shared with it.

## 3. Share the folder with the service account

In the `NotebookLM-Corpus/` folder: Share → add the service account's
`…@…iam.gserviceaccount.com` address with **Editor** right. (Sharing a
folder with a service account gives it access without domain-wide
delegation.)

## 4. Configure the GitHub secrets

Repository `FBerthommier/covtl.org` → Settings → Secrets and variables →
Actions → New repository secret:

| Secret | Value |
|---|---|
| `GOOGLE_CREDENTIALS` | the **whole JSON content** of the service-account key file (paste it raw) |
| `DRIVE_FOLDER_ID` | the folder id from step 1 |

Never commit a key or a token; these values live only in Secrets.

## 5. Create the NotebookLM notebook and import the sources

1. https://notebooklm.google.com → New notebook → name it
   (e.g. « COVTL — articulatory speech synthesis »).
2. Add sources → **Google Drive** → select the 7 documents in
   `NotebookLM-Corpus/` (they are already mirrored there by the workflow,
   or run it once in full mode first — see below).
3. Check each source shows the current document version.
4. Share settings → **Anyone with the link — Viewer**.
5. Copy the public link (`https://notebooklm.google.com/notebook/<id>`).
6. Open the link in a private window / another account to test access.

## 6. Wire the site button

In `index.html`, the tagged `notebooklm-link` block:
replace `href="#notebooklm-pending"` with the notebook URL and remove
`data-pending="true"` (one-attribute edit; the greyed style and the click
guard disappear with it). Also fill `notebook_url:` in
`notebooklm-manifest.yaml`. Commit.

## 7. First full sync

Repository → Actions → **notebooklm-sync** → Run workflow →
`dry_run = false`. The run summary reports added/updated/unchanged/errors.
Re-run with `dry_run = true` anytime to inspect without writing.
