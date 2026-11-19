# NOTEBOOKLM-MAINTENANCE.md — day-to-day operation, incidents, recovery

## What happens on a documentation change

1. Corrected documents are committed in their **source repository**
   (covtl-pipeline / covtl-console / covtl-sandhi) — that is where the
   documents live.
2. If the content of a manual changes in a way NotebookLM should see,
   edit `notebooklm-manifest.yaml` in **this** repository
   (`last_modified`, `version` fields) and commit.
3. The push triggers `notebooklm-sync`: changed documents are updated
   **in place** in `NotebookLM-Corpus/` (Drive file ids preserved, so the
   NotebookLM sources keep pointing at the same files). Google then
   refreshes the Drive-based sources in the notebook on its own.

Adding a document = add a manifest entry (new stable id) + run the sync +
add the source in the notebook (manual, see below).
Retiring a document = move its entry to `excluded:` (never delete the
entry entirely) + run the sync + remove the source from the notebook
(manual). The file stays in Drive, reported as removed-from-manifest,
until you delete it by hand.

## Editing the notebook composition (manual, by design)

There is no official NotebookLM API for editing notebooks: composition
changes (add/remove sources, re-share) are done in the NotebookLM UI.
The sync only keeps the Drive mirror correct; it does not touch the
notebook.

## Reading a sync report

Actions → notebooklm-sync → open the run: the summary and the
`notebooklm-sync-report` artifact list, per document: added / updated /
unchanged / removed-from-manifest / errors, with the run mode
(`full` = Drive written; `dry-run` = report only).

## Common incidents

| Symptom | Cause | Fix |
|---|---|---|
| run falls back to dry-run although secrets exist | secret name mismatch, or Drive API not enabled on the project | check secret names (`GOOGLE_CREDENTIALS`, `DRIVE_FOLDER_ID`) and the API |
| 403 on Drive calls | the service account is not Editor on the folder, or the JSON is stale | re-share `NotebookLM-Corpus/` with the service account; rotate the key |
| a file keeps being "updated" every run | remote `md5Checksum` unavailable or a sync conflict | open the Drive file, check its version history, re-upload once manually |
| a document fails to download | source repo moved/renamed the file | fix the `url` in the manifest (ids must NOT change) |
| NotebookLM shows an old version | Drive → NotebookLM refresh is Google-side | open the source in the notebook and confirm the Drive file version; give it a few minutes |

## Recovery

- A bad document in Drive: fix the source on GitHub, re-run the sync in
  full mode (in-place update) — do not delete the Drive file (it would
  break the notebook source id).
- A broken manifest (syntax, duplicate ids): the workflow fails before
  any Drive call; fix and re-run.
- Rollback of the site page: `git revert` — the gateway does not touch
  the site HTML.
- Service-account key rotation: create a new key, update the
  `GOOGLE_CREDENTIALS` secret, revoke the old key in Google Cloud
  Console.

## Current limits (documented honestly)

- NotebookLM composition is manual (no official API).
- The service account sees only the folder shared with it (`drive.file`
  scope) — nothing else in the owner's Drive.
- Only PDF/MD/YAML formats are declared today; `docx` is supported by
  the agent's MIME table but no such document is in the corpus yet.
