// Google Apps Script — query-log mirror for the ABC JDE Assistant.
//
// Setup: create a Google Sheet, rename its first tab to exactly  QueryLog
// (case-sensitive), then Extensions -> Apps Script, paste this in, and
// Deploy -> New deployment -> Web app -> Execute as: Me -> Who has access: ANYONE
// (not "Anyone with a Google account" — the server isn't a Google identity).
// Put the web app URL in GOOGLE_SHEETS_LOG_URL and the secret below in
// GOOGLE_SHEETS_LOG_SECRET on the server. After EVERY edit to this script,
// create a NEW deployment version or the URL keeps serving the old code.
//
// Row order:  timestamp, deployment, device_id, status, row_count, tables, question, sql, error, ip
// Header row to type in A1:J1: Timestamp, User, Device ID, Status, Rows, List of Tables, User Prompt, SQL, Error, IP

// Generate your own long random value. Do NOT reuse another deployment's secret.
const SHARED_SECRET = "REPLACE_WITH_A_LONG_RANDOM_SECRET";
const SHEET_NAME = "QueryLog";

// The user prompt is free text. A value starting with = + - @ would be run as a
// spreadsheet formula, so prefix it with an apostrophe to keep it plain text.
function safe(v) {
  v = v == null ? "" : String(v);
  return /^[=+\-@]/.test(v) ? "'" + v : v;
}

function doPost(e) {
  try {
    const body = JSON.parse(e.postData.contents);

    if (SHARED_SECRET && body.secret !== SHARED_SECRET) {
      return ContentService.createTextOutput("ignored");
    }

    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
    if (!sheet) {
      return ContentService.createTextOutput("no sheet");
    }

    sheet.appendRow([
      body.timestamp || "",
      body.deployment || "",
      body.device_id || "",
      body.status || "",
      body.row_count != null ? body.row_count : "",
      body.tables || "",
      safe(body.question),
      body.sql || "",
      body.error || "",
      body.ip || "",
    ]);

    return ContentService.createTextOutput("ok");
  } catch (err) {
    // If rows never show up, open Apps Script -> Executions and add
    // console.log(...) lines here; the server swallows webhook errors on purpose.
    return ContentService.createTextOutput("error");
  }
}
