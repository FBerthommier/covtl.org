/**
 * NotebookLM-AppsScript.gs - COVTL GitHub -> Google Drive mirror agent.
 *
 * Free variant of the gateway: runs inside your own Google account via
 * Apps Script (no Google Cloud project, no billing account, no service
 * account, no GitHub secrets). Paste this file at script.google.com,
 * enable the advanced Drive v2 service, run syncNotebookLm once
 * (authorize), optionally add a weekly time trigger.
 *
 * Reads https://covtl.org/notebooklm-manifest.json (JSON twin of the
 * manifest, maintained in the covtl.org repository), downloads each
 * document from its authoritative GitHub raw URL, and mirrors it into
 * the Drive folder NotebookLM-Corpus/:
 *   - missing file  -> created;
 *   - changed file  -> updated IN PLACE (Drive file id preserved, so the
 *     NotebookLM sources keep pointing at the same file);
 *   - identical file -> untouched;
 *   - file present in Drive but absent from the manifest -> LEFT IN
 *     PLACE and reported (never deleted automatically).
 *
 * GitHub remains the source of truth; Drive is only an operational
 * mirror; the NotebookLM notebook itself is never touched by this script.
 */

var MANIFEST_URL = 'https://covtl.org/notebooklm-manifest.json';
var FOLDER_NAME = 'NotebookLM-Corpus';

function syncNotebookLm() {
  var report = { startedAt: new Date().toISOString(), added: [],
                 updated: [], unchanged: [], removedFromManifest: [],
                 errors: [] };
  var manifest = JSON.parse(UrlFetchApp.fetch(MANIFEST_URL,
      { muteHttpExceptions: false }).getContentText());
  var docs = manifest.documents || [];
  Logger.log('manifest: ' + docs.length + ' documents, notebook_url=' +
      (manifest.notebook_url ? 'set' : 'PENDING (not created yet)'));

  var folder = ensureFolder_(FOLDER_NAME);
  var existing = listFolderFiles_(folder);

  docs.forEach(function (doc) {
    try {
      var blob = UrlFetchApp.fetch(doc.url)
          .getBlob().setName(doc.path);
      var md5 = md5Of_(blob);
      var current = existing[doc.path];
      if (!current) {
        folder.createFile(blob);
        report.added.push(doc.path);
        Logger.log(doc.id + ': added');
      } else if (current.md5 && current.md5 === md5) {
        report.unchanged.push(doc.path);
        Logger.log(doc.id + ': unchanged');
      } else {
        updateInPlace_(current.id, blob);
        report.updated.push(doc.path);
        Logger.log(doc.id + ': updated (id preserved: ' + current.id + ')');
      }
    } catch (e) {
      report.errors.push(doc.id + ': ' + e);
      Logger.log(doc.id + ': ERROR ' + e);
    }
  });

  // Present in Drive but gone from the manifest: report, never delete.
  var inManifest = {};
  docs.forEach(function (d) { inManifest[d.path] = true; });
  Object.keys(existing).forEach(function (name) {
    if (!inManifest[name]) {
      report.removedFromManifest.push(
          { name: name, id: existing[name].id,
            action: 'left in place - manual validation required' });
    }
  });

  report.finishedAt = new Date().toISOString();
  Logger.log(JSON.stringify(report, null, 1));
  return report;
}

/** Set a weekly time trigger from the editor (or run manually anytime). */
function installWeeklyTrigger() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'syncNotebookLm') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('syncNotebookLm').timeBased()
      .onWeekDay(ScriptApp.WeekDay.MONDAY).atHour(5).create();
  Logger.log('weekly trigger installed (Monday 05:00)');
}

function ensureFolder_(name) {
  var it = DriveApp.getFoldersByName(name);
  return it.hasNext() ? it.next() : DriveApp.createFolder(name);
}

function listFolderFiles_(folder) {
  var out = {};
  var it = folder.getFiles();
  while (it.hasNext()) {
    var f = it.next();
    var md5 = '';
    try { md5 = Drive.Files.get(f.getId(), { fields: 'md5Hash' }).md5Hash || ''; }
    catch (e) { /* advanced Drive service disabled: md5 unavailable */ }
    out[f.getName()] = { id: f.getId(), md5: md5 };
  }
  return out;
}

function md5Of_(blob) {
  return Utilities.computeDigest(Utilities.DigestAlgorithm.MD5,
      blob.getBytes()).map(function (b) {
        return ('0' + (b & 0xff).toString(16)).slice(-2);
      }).join('');
}

function updateInPlace_(fileId, blob) {
  // Advanced Drive v2 service: same file id, new content.
  Drive.Files.update({ title: blob.getName() }, fileId, blob);
}
