# NOTEBOOKLM-MAINTENANCE.md — day-to-day operation, incidents, recovery

## What happens on a documentation change

1. Corrected documents are committed in their **source repository**
   (covtl-pipeline / covtl-console / covtl-sandhi) — that is where the
   documents live.
2. If the content of a manual changes in a way NotebookLM should see,
   edit `notebooklm-manifest.yaml` in **this** repository
   (`last_modified`, `version` fields), regenerate the JSON twin
   `notebooklm-manifest.json`, and commit both.
3. Run the Apps Script (`syncNotebookLm`) — manually from
   script.google.com or via the weekly trigger: changed documents are
   updated **in place** in `NotebookLM-Corpus/` (Drive file ids
   preserved, so the NotebookLM sources keep pointing at the same
   files). Google then refreshes the Drive-based sources in the notebook
   on its own. The GitHub Actions lane gives an independent dry-run
   verification report at each manifest push.

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

- **Apps Script**: script.google.com → project → Executions: each run
  logs added / updated / unchanged / removed-from-manifest / errors.
- **GitHub Actions** (verification lane): Actions → notebooklm-sync →
  run summary + `notebooklm-sync-report` artifact (dry-run: downloads
  and fingerprints the corpus, touches nothing).

## Common incidents

| Symptom | Cause | Fix |
|---|---|---|
| Apps Script errors on `Drive.Files` | the advanced Drive v2 service is not enabled in the project | Editor → Services (+) → add **Drive API** |
| "updated" on every run for one file | remote MD5 unavailable or a Drive sync conflict | open the Drive file, check version history, re-upload once manually |
| a document fails to download | source repo moved/renamed the file | fix the `url` in the manifest (ids must NOT change) |
| Apps Script and Actions report different fingerprints | `notebooklm-manifest.json` out of sync with the YAML | regenerate the JSON twin and commit both |
| NotebookLM shows an old version | Drive → NotebookLM refresh is Google-side | open the source in the notebook and confirm the Drive file version; give it a few minutes |
| authorization expired / access error in Apps Script | OAuth grant revoked | run once manually and re-authorize |

## Recovery

- A bad document in Drive: fix the source on GitHub, re-run
  `syncNotebookLm` (in-place update) — do not delete the Drive file (it
  would break the notebook source id).
- A broken manifest (syntax, duplicate ids): the Apps Script fails
  before touching Drive; fix and re-run.
- Rollback of the site page: `git revert` — the gateway does not touch
  the site HTML.
- Suspected script compromise: script.google.com → project settings →
  revoke access (Google account → Security → Third-party access), delete
  the project, re-create from `docs/NotebookLM-AppsScript.gs`.

## Current limits (documented honestly)

- NotebookLM composition is manual (no official API).
- The Apps Script runs under the owner's Google identity and only
  touches the `NotebookLM-Corpus/` folder; its OAuth grant can be
  revoked anytime from the Google account security page.
- Only PDF/MD/YAML formats are declared today; the GitHub Actions lane
  also knows `docx`, but no such document is in the corpus yet.
