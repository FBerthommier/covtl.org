# covtl.org — the COVTL website repository

This repository publishes **https://covtl.org** (GitHub Pages,
custom domain, HTTPS enforced): the download page for the COVTL
articulatory speech-synthesis console (Windows / Linux / macOS
standalone bundles, pip install, QR codes, SHA-256 and Sigstore
verification guidance).

Site contents: `index.html` + 4 QR codes + `notebooklm-manifest.yaml`
+ this documentation. `index.html` is a single self-contained file
(HTML/CSS, no build step); the QR codes are a desktop feature — do not
shrink or regenerate them.

Repositories of the COVTL chain:
[engine covtl-pipeline](https://github.com/FBerthommier/covtl-pipeline) ·
[console covtl-console](https://github.com/FBerthommier/covtl-console) ·
[covtl-sandhi](https://github.com/FBerthommier/covtl-sandhi) ·
[PyPI covtl](https://pypi.org/project/covtl/)

The documentation corpus is licensed CC BY-SA 4.0 (see
`LICENSE-DOCS.md` in each repository); the software is
GPL-3.0-or-later.

## Explorer le corpus avec NotebookLM

**NotebookLM** est l'interface interactive de Google qui permet
d'interroger un corpus documentaire comme un assistant conversationnel :
on pose des questions, il répond en citant les sources. Un notebook
public COVTL est en préparation pour explorer toute la documentation
(modèle COVTL, VocalTractLab 2.4 — Peter Birkholz —, manuels utilisateur
et technique, guide sandhi, synthèse de couverture).

- **Lien du notebook** : à venir — le bouton *NotebookLM* de la page
  d'accueil s'activera dès que le notebook sera créé et partagé
  (lien public stable, « anyone with the link »).
- **Corpus GitHub (source de référence)** :
  [covtl-pipeline](https://github.com/FBerthommier/covtl-pipeline) ·
  [covtl-console](https://github.com/FBerthommier/covtl-console) ·
  [covtl-sandhi](https://github.com/FBerthommier/covtl-sandhi).
- **Licence du corpus** : CC BY-SA 4.0 — attribution requise, parts
  partagées à l'identique. Construit sur **VocalTractLab 2.4** de Peter
  Birkholz (vocaltractlab.de), crédit à conserver dans toute production
  dérivée.
- **Fonctionnement de la synchronisation** : `notebooklm-manifest.yaml`
  (ce dépôt, racine) liste les documents destinés au notebook ; le
  workflow `notebooklm-sync` copie automatiquement les documents listés
  vers le dossier Drive `NotebookLM-Corpus/` (mise à jour en place,
  empreintes SHA-256 comparées, jamais de suppression automatique) ;
  NotebookLM lit ensuite ces sources Drive.
- **GitHub reste la source documentaire de référence** : Drive n'est
  qu'un miroir opérationnel et NotebookLM une interface d'exploration.

Procédure complète : `docs/NOTEBOOKLM-ARCHITECTURE.md` (architecture),
`docs/NOTEBOOKLM-SETUP.md` (installation pas à pas),
`docs/NOTEBOOKLM-MAINTENANCE.md` (maintenance, incidents, reprise).
