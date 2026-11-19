# NOTEBOOKLM-ARCHITECTURE.md — the GitHub → Google Drive → NotebookLM gateway

## Goal

Give the COVTL documentation corpus two complementary, durable doors:

- **GitHub** (this repository) — master corpus: versioned, public,
  freely reusable, source of truth.
- **NotebookLM** — interactive interface to explore and query the corpus,
  whose public sharing link stays stable even as documents evolve.

**Google Drive is only an operational mirror** between the two: a folder
(`NotebookLM-Corpus/`) holding fresh copies of exactly the documents
selected by `notebooklm-manifest.yaml`.

## Data flow

```
GitHub (master corpus, manifest)
        │  Google Apps Script (docs/NotebookLM-AppsScript.gs)
        │    1. read manifest JSON twin (ids stable across editions)
        │    2. download each document from its raw.githubusercontent URL
        │    3. fingerprint (MD5) and compare with the Drive folder
        │    4. create missing files, update changed files IN PLACE
        │       (Drive file ids preserved), never delete
        ▼
Google Drive  NotebookLM-Corpus/   (mirror only)
        │  Google's own "Drive source" synchronisation
        ▼
NotebookLM notebook  (public share link, stable)
```

The agent runs as an **Apps Script in the site owner's own Google
account** — no Google Cloud project, no billing, no service account, no
GitHub secrets. A GitHub Actions workflow (`notebooklm-sync.yml`) remains
available as a **read-only verification/report** lane (it downloads the
corpus and fingerprints it without touching Drive).

## What synchronises automatically — and what does not

- **GitHub → Drive**: automatic (this workflow), fingerprint-diffed,
  in-place updates.
- **Drive → NotebookLM (file contents)**: handled natively by Google
  when sources are added as Drive files.
- **Notebook composition** (adding/removing sources in the notebook):
  a MANUAL procedure, distinct from the sync — see
  `NOTEBOOKLM-MAINTENANCE.md`. There is no official NotebookLM API;
  nothing in this repository touches the notebook programmatically.

## Corpus and manifest

`notebooklm-manifest.yaml` (repository root) lists the 7 selected
documents (`manual_001`–`manual_007`), each with: stable `id`, stable
`path` (= filename in the Drive mirror), `repository` + `url` (the
authoritative raw URL), `title`, `category`, `format`, `version`,
`license` (all CC-BY-SA-4.0, see LICENSE-DOCS.md in each repository),
`last_modified`, and the VocalTractLab 2.4 / Peter Birkholz credit where
it applies (not on covtl-sandhi). An `excluded:` list reserves room for
documents intentionally kept out of the notebook. `notebook_url` is
reserved for the public share link of the notebook.

The documents themselves live in the source repositories
(covtl-pipeline, covtl-console, covtl-sandhi) — this site repository
hosts only the manifest. This may evolve: if documents are later copied
into this repository, their `path` becomes a repository-relative path and
the agent handles them identically.

## Components

| Component | Role |
|---|---|
| `notebooklm-manifest.yaml` | what belongs to the notebook; stable ids (reference source) |
| `notebooklm-manifest.json` | JSON twin of the manifest, read by the Apps Script (regenerate when the YAML changes) |
| `docs/NotebookLM-AppsScript.gs` | the agent (download → diff → mirror), runs in the owner's Google account |
| `.github/workflows/notebooklm-sync.yml` | read-only verification lane: downloads the corpus and reports fingerprints (dry-run) on manifest push, dispatch, weekly |
| `docs/NOTEBOOKLM-SETUP.md` | one-time configuration (Drive folder, Apps Script, notebook) |
| `docs/NOTEBOOKLM-MAINTENANCE.md` | day-to-day updates, incidents, recovery |

## Guarantees

- No deletion is ever automatic (removed-from-manifest files are
  reported and left in place, pending manual validation).
- Drive file ids are preserved (in-place update via the advanced Drive
  service).
- Ids/paths in the manifest are stable: editing a document never changes
  its identity in Drive or in the notebook.
- Git history is never rewritten; destructive operations require
  explicit validation.
- The Apps Script runs with the owner's identity and only touches the
  `NotebookLM-Corpus/` folder; the Actions lane is read-only and stays
  green with no credentials at all.
