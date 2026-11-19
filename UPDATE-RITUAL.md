# UPDATE RITUAL — how to publish a documentation change to the NotebookLM corpus

**Read this before touching the docs.** The NotebookLM notebook
(15→13 sources, public link, wired to the *NotebookLM* button of the
site) does NOT update itself. The whole chain is:

```
source repository (the PDF's own repo: covtl-pipeline / covtl-console /
  covtl-sandhi)  ←  commit the corrected document THERE first
        ↓
THIS repository: notebooklm-manifest.yaml (+ its JSON twin)
        ↓
Google Apps Script: syncNotebookLm   (script.google.com → notebooklm-sync)
        ↓
Drive NotebookLM-Corpus/  →  NotebookLM sources  →  the public notebook
```

## The ritual (5 steps, ~10 minutes)

1. **Fix the document in its own repository** and push. The URL in the
   manifest points at `main`, so the mirror always serves the latest.
2. **Update the manifest here** — `notebooklm-manifest.yaml` AND
   `notebooklm-manifest.json` (the Apps Script reads the JSON; always
   commit BOTH together):
   - `version:` and `last_modified:` on the affected entry;
   - nothing else: **ids and `path` never change** (that is what keeps
     the Drive file — and therefore the NotebookLM source — identical).
3. **Regenerate/verify the JSON twin** if you edited the YAML by hand
   (same documents list, same order).
4. **Run the sync**: script.google.com → project `notebooklm-sync` →
   select `syncNotebookLm` → **Run**. Expected report on a normal
   update: `updated: 1, unchanged: 12` (or `unchanged: 12, dry-run` list
   complete). Google then refreshes the Drive-based source in the
   notebook on its own — give it a few minutes.
5. **Spot-check the notebook**: open the source in NotebookLM, confirm
   it shows the new content. The public link never changes.

## Variants

- **New document** → add a manifest entry with a NEW stable id
  (`manual_016`, `manual_017`, … never reuse an id), run the sync
  (report: `added: 1`), then add the source in the NotebookLM UI
  (manual, no API).
- **Retire a document** → move its entry from `documents:` to
  `excluded:` (with a reason; never delete the entry), run the sync
  (report: `removedFromManifest`, file left in place), then remove the
  source in the NotebookLM UI; delete the Drive file by hand afterwards
  if you want a strict mirror.
- **Verification only, no write** → GitHub Actions → `notebooklm-sync`
  → Run workflow with `dry_run = true`: downloads and fingerprints the
  corpus, touches nothing.

## Full procedures

`docs/NOTEBOOKLM-ARCHITECTURE.md` · `docs/NOTEBOOKLM-SETUP.md` ·
`docs/NOTEBOOKLM-MAINTENANCE.md` (reports, incidents, recovery).
