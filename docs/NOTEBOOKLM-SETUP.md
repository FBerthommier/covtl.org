# NOTEBOOKLM-SETUP.md — one-time configuration (free variant, no Google Cloud)

Do these steps in order. Everything happens with **your own Google
account** — no billing account, no credit card, no Google Cloud project,
no GitHub secrets.

## 1. Create the Drive mirror folder

1. In Google Drive, create a folder named exactly **`NotebookLM-Corpus/`**.
2. Leave it empty: it will hold ONLY the documents listed in the
   manifest.

## 2. Install the sync agent (Apps Script)

1. Open https://script.google.com → **New project**.
2. Delete the default code, paste the whole content of
   [`docs/NotebookLM-AppsScript.gs`](NotebookLM-AppsScript.gs) (this
   repository), rename the project (e.g. `notebooklm-sync`).
3. Enable the advanced Drive service: **Editor → Services (+)** → select
   **Drive API** → Add. (This is the v2 advanced service, needed to
   update files in place and read their MD5.)
4. Save. Select the `syncNotebookLm` function in the toolbar and click
   **Run**. Google asks for authorization once — review and allow
   (warning about "unverified app" is normal: it is your own script).
5. **Check**: View → Logs (or "Executions") shows the report:
   `added: 7` on the first run, then `unchanged: 7` on a second run —
   and the 7 documents are visible in `NotebookLM-Corpus/`.

## 3. Optional: automatic refresh

Editor → clock icon (**Triggers**) → Add trigger → function
`syncNotebookLm`, time-based, weekly (or use the provided
`installWeeklyTrigger()` helper once). Manual runs remain possible
anytime. Every run is a fingerprint-diff: only changed documents are
transferred.

## 4. Create the NotebookLM notebook and import the sources

1. https://notebooklm.google.com → **New notebook** → name it
   (e.g. « COVTL — articulatory speech synthesis »).
2. Add sources → **Google Drive** → select the 7 documents in
   `NotebookLM-Corpus/`.
3. Check each source opens and shows the current version.
4. Share settings → **Anyone with the link — Viewer**.
5. Copy the public link (`https://notebooklm.google.com/notebook/<id>`).
6. Open the link in a private window to test access.

## 5. Wire the site button

In `index.html`, the tagged `notebooklm-link` block: replace
`href="#notebooklm-pending"` with the notebook URL and remove
`data-pending="true"` (one-attribute edit; the greyed style and the
click guard disappear with it). Also fill `notebook_url:` in
`notebooklm-manifest.yaml`. Commit — or hand the link to the maintainer.

## 6. Keep the two manifest files in sync

The Apps Script reads `notebooklm-manifest.json` (its JSON twin — Apps
Script has no YAML parser). Whenever you edit
`notebooklm-manifest.yaml`, regenerate/commit the JSON twin too
(both live at the repository root). The GitHub Actions workflow
`notebooklm-sync` stays available as a dry-run verification report
(it reads the YAML and writes nothing).

## Deprecated alternative (kept for the record)

A service-account variant (Google Cloud + GitHub secrets + Actions
writing to Drive) exists in git history (`scripts/notebooklm_sync.py`
still supports it) but is NOT the recommended path: Google Cloud now
requires a billing account attached to projects. The Apps Script variant
above needs none of that.
