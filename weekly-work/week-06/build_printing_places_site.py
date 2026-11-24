#!/usr/bin/env python3
"""
Build an interactive "Printing Places Dashboard" web page from the OpenRefine CSV.

Usage (pasted into a Jupyter cell, or in a terminal):
    python build_printing_places_site.py
    python build_printing_places_site.py my_input.csv my_output.html

What it does
    1. Reads the CSV WITHOUT changing it (every cell is read as plain text).
    2. Embeds the table in ONE self-contained HTML file (printing_places_dashboard.html).
    3. The finished page works in two ways:
         - it opens with the embedded CSV already loaded, and
         - it has a "Load a CSV from your computer" button (or drag and drop), so anyone can
           explore another CSV with the same kind of columns. The file never leaves the browser.
    4. The page uses Leaflet (map) and Chart.js (charts), loaded from the internet.

The original CSV is never modified or overwritten.
"""

import json
import math
import sys
from pathlib import Path

import pandas as pd

# ----------------------------------------------------------------------------
# Settings you may want to change
# ----------------------------------------------------------------------------
# Jupyter passes its own arguments (such as "-f"), so only arguments that look like
# file names are used.
_args = [a for a in sys.argv[1:] if not a.startswith("-")]
_csv_args = [a for a in _args if a.lower().endswith(".csv")]
_html_args = [a for a in _args if a.lower().endswith(".html")]

INPUT_CSV = _csv_args[0] if _csv_args else "book-places-wikidata.csv"
OUTPUT_HTML = _html_args[0] if _html_args else "printing_places_dashboard.html"

# The page repairs garbled accents (e.g. "NÃ¼rnberg" -> "Nürnberg") only if this is True
# or if the person ticks the box on the page. The CSV itself is never changed.
REPAIR_ACCENTS_BY_DEFAULT = False


# ----------------------------------------------------------------------------
# Helper: same coordinate rule as in the earlier validation steps ("latitude,longitude")
# ----------------------------------------------------------------------------
def parse_coordinate(value):
    """Return (latitude, longitude, status) for one original coordinate cell."""
    if value is None or str(value).strip() == "":
        return None, None, "missing"
    parts = str(value).split(",")
    if len(parts) != 2:
        return None, None, "format_error"
    try:
        lat = float(parts[0].strip())
        lon = float(parts[1].strip())
    except ValueError:
        return None, None, "format_error"
    if not (math.isfinite(lat) and math.isfinite(lon)):
        return None, None, "format_error"
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None, None, "out_of_range"
    return lat, lon, "ok"


# ----------------------------------------------------------------------------
# 1. Load the CSV (read-only, everything as text, nothing dropped)
# ----------------------------------------------------------------------------
embedded = None
try:
    books = pd.read_csv(INPUT_CSV, dtype=str, keep_default_na=False)
except FileNotFoundError:
    books = None
    print(f"WARNING: '{INPUT_CSV}' was not found. The page will be built without embedded data;")
    print("         use its 'Load a CSV from your computer' button to open a file.")

if books is not None:
    print(f"Loaded {len(books)} rows and {len(books.columns)} columns from {INPUT_CSV}")

    if "edition_id" in books.columns:
        if books["edition_id"].is_unique:
            print("edition_id is unique:", books["edition_id"].nunique(), "values")
        else:
            print("WARNING: edition_id is not unique. Please review the duplicates.")
    else:
        print("WARNING: no 'edition_id' column found; the page will use row numbers instead.")

    coord_col = "coordinate location"
    if coord_col in books.columns:
        statuses = [parse_coordinate(v)[2] for v in books[coord_col]]
        usable = statuses.count("ok")
        print(f"Usable coordinates: {usable} of {len(books)} ({usable / max(len(books), 1) * 100:.1f}%)")
    else:
        print(f"WARNING: no '{coord_col}' column found; the map will be empty.")

    embedded = {
        "name": Path(INPUT_CSV).name,
        "columns": [str(c) for c in books.columns],
        "rows": books.values.tolist(),
    }

payload = {"embedded": embedded, "repair": REPAIR_ACCENTS_BY_DEFAULT}
payload_json = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")

# ----------------------------------------------------------------------------
# 2. The web page (HTML + CSS + JavaScript)
# ----------------------------------------------------------------------------
HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Printing Places Dashboard</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">
<style>
:root{--bg:#f5f3ee;--card:#fff;--ink:#222;--muted:#6b6b6b;--accent:#8b1e3f;--line:#ddd6c8;}
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--ink);}
header{padding:18px 24px 4px}
h1{margin:0;font-size:1.5rem}
#subtitle{margin:4px 0 0;color:var(--muted);font-size:.9rem}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.srcbar{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;margin:12px 24px 0;font-size:.85rem}
#warn{flex-basis:100%;color:#8a4b00;font-size:.8rem}
#warn p{margin:2px 0}
body.dragging::after{content:"Drop a CSV file to load it";position:fixed;inset:0;background:rgba(139,30,63,.18);border:4px dashed var(--accent);display:flex;align-items:center;justify-content:center;font-size:1.6rem;font-weight:600;color:var(--accent);z-index:9999;pointer-events:none}
.filters{display:flex;flex-wrap:wrap;gap:10px 16px;align-items:flex-end;margin:12px 24px}
.filters label{display:flex;flex-direction:column;font-size:.75rem;color:var(--muted);gap:3px}
.filters input[type=search],.filters select{padding:6px 8px;border:1px solid var(--line);border-radius:6px;font-size:.85rem;min-width:140px}
.relbox{display:flex;flex-wrap:wrap;gap:4px 12px;font-size:.8rem;color:var(--ink)}
.relbox label{flex-direction:row;align-items:center;gap:4px;color:var(--ink);font-size:.8rem}
.swatch{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:5px;vertical-align:-1px}
button{padding:6px 12px;border:1px solid var(--line);background:#fff;border-radius:6px;cursor:pointer;font-size:.85rem}
button:hover{background:#faf6ea}
button.primary{background:var(--accent);color:#fff;border-color:var(--accent)}
button.primary:hover{background:#731834}
.chip{display:inline-block;background:#fde9ee;border:1px solid #e6b3c1;border-radius:14px;padding:3px 10px;font-size:.8rem;margin-left:6px;cursor:pointer}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:0 24px 14px}
.kpi b{display:block;font-size:1.4rem}
.kpi span{color:var(--muted);font-size:.78rem}
.main{display:grid;grid-template-columns:minmax(0,3fr) minmax(0,2fr);gap:14px;margin:0 24px 14px}
@media(max-width:1000px){.main{grid-template-columns:1fr}}
#map{height:560px;border-radius:10px;border:1px solid var(--line);background:#dfe9f0}
.timebar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-top:10px;font-size:.85rem}
.timebar input[type=range]{flex:1;min-width:160px}
.trail{margin-top:10px;font-size:.85rem}
.trail input[type=text]{padding:6px 8px;border:1px solid var(--line);border-radius:6px;min-width:260px}
.trail ol{margin:6px 0 0 18px;padding:0}
.ac{position:relative;display:inline-block}
.aclist{position:absolute;left:0;top:100%;z-index:2000;min-width:100%;width:max-content;max-width:420px;max-height:260px;overflow:auto;background:#fff;border:1px solid var(--line);border-radius:6px;box-shadow:0 4px 14px rgba(0,0,0,.2);margin-top:2px}
.aclist div{padding:6px 10px;cursor:pointer;display:flex;justify-content:space-between;gap:14px;font-size:.85rem}
.aclist div.act,.aclist div:hover{background:#fde9ee}
.aclist small{color:var(--muted);white-space:nowrap}
.aclist mark{background:#ffe08a;padding:0}
.aclist .acnone{cursor:default;color:var(--muted)}
.charts{display:grid;grid-template-columns:1fr 1fr;gap:12px;align-content:start}
.chartbox{height:230px;position:relative}
.span2{grid-column:1/-1}
.legend{background:rgba(255,255,255,.96);padding:8px 10px;border-radius:8px;box-shadow:0 1px 6px rgba(0,0,0,.25);font-size:12px;max-width:250px;line-height:1.55}
.trail-num{background:#1d4e89;color:#fff;border-radius:50%;width:20px;height:20px;text-align:center;line-height:16px;font-size:11px;font-weight:600;border:2px solid #fff}
.pie-icon{background:none;border:none;filter:drop-shadow(0 1px 3px rgba(0,0,0,.45))}
.tablecard{margin:0 24px 30px}
.tablebar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:8px;font-size:.85rem}
.tablewrap{overflow:auto;max-height:520px;border:1px solid var(--line);border-radius:6px}
table{border-collapse:collapse;width:max-content;min-width:100%;font-size:.8rem}
th{position:sticky;top:0;background:#efe9db;cursor:pointer;white-space:nowrap;text-align:left;padding:6px 8px;z-index:1}
td{padding:5px 8px;border-top:1px solid #eee;max-width:280px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
tr:hover td{background:#faf6ea}
tr.sel td{background:#fde9ee}
.plink{color:#1d4e89;text-decoration:underline;cursor:pointer}
details{font-size:.82rem}
details ul{margin:4px 0 8px 18px;padding:0}
</style>
</head>
<body>
<header>
  <h1>Printing Places Dashboard</h1>
  <p id="subtitle"></p>
</header>

<section class="card srcbar">
  <button class="primary" id="loadBtn">📂 Load a CSV from your computer</button>
  <input type="file" id="fileInput" accept=".csv,.tsv,.txt,text/csv" hidden>
  <button id="embeddedBtn" hidden>↩ Back to the embedded data</button>
  <label><input type="checkbox" id="repairChk"> Repair garbled accents (NÃ¼rnberg → Nürnberg)</label>
  <span id="srcInfo" style="color:#6b6b6b"></span>
  <span style="color:#6b6b6b">You can also drag a CSV file onto this page. Files stay in your browser and are not uploaded.</span>
  <div id="warn"></div>
</section>

<section class="card filters" id="filters">
  <label>Search all columns<input type="search" id="q" placeholder="title, printer, place…"></label>
  <label>Language<select id="fLang"></select></label>
  <label>Format<select id="fFmt"></select></label>
  <label>Match status<select id="fMs"></select></label>
  <label>Years: <span id="yLabel"></span>
    <span><input type="range" id="yMin"> <input type="range" id="yMax"></span></label>
  <label>Place relationship<span class="relbox" id="relBoxes"></span></label>
  <span><button id="resetBtn">Reset filters</button> <span id="chips"></span></span>
</section>

<section class="kpis" id="kpis"></section>

<section class="main">
  <div>
    <div id="map"></div>
    <div class="card timebar">
      <b>Time Machine</b>
      <select id="timeMode">
        <option value="off">Off</option>
        <option value="cum">Cumulative (up to a decade)</option>
        <option value="win">One decade at a time</option>
      </select>
      <button id="playBtn">▶ Play</button>
      <input type="range" id="timeSlider" step="10" disabled>
      <span id="timeLabel"></span>
    </div>
    <div class="card trail">
      <b>Printer Trails</b> – follow a printer from place to place, in date order<br>
      <span class="ac">
        <input id="printerInput" type="text" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="acList" placeholder="Start typing a printer name…">
        <div id="acList" class="aclist" role="listbox" hidden></div>
      </span>
      <button id="clearTrail">Clear trail</button>
      <div id="trailInfo" style="margin-top:6px;color:#6b6b6b"></div>
    </div>
  </div>
  <div class="charts">
    <div class="card chartbox span2"><canvas id="cDecade"></canvas></div>
    <div class="card chartbox"><canvas id="cRel"></canvas></div>
    <div class="card chartbox"><canvas id="cLang"></canvas></div>
    <div class="card chartbox span2"><canvas id="cPlaces"></canvas></div>
    <details class="card span2"><summary><b>Data quality review</b></summary><div id="quality"></div></details>
  </div>
</section>

<section class="card tablecard">
  <div class="tablebar">
    <b>Books</b>
    <span id="tableInfo"></span>
    <button id="zoomBtn">Zoom map to these records</button>
    <span style="flex:1"></span>
    <label>Rows per page <select id="pageSize"><option>25</option><option>50</option><option>100</option></select></label>
    <button id="prevPg">‹ Prev</button><span id="pgInfo"></span><button id="nextPg">Next ›</button>
  </div>
  <div class="tablewrap"><table><thead id="thead"></thead><tbody id="tbody"></tbody></table></div>
  <p style="color:#6b6b6b;font-size:.78rem;margin:6px 0 0">Click a row to select its place on the map. Click a column heading to sort. The last column is derived from the coordinate parsing; all other columns are the original CSV.</p>
</section>

<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<script>
(function(){
const PAYLOAD = __DATA__;
const PALETTE = ["#1f77b4","#e8743b","#2ca02c","#9467bd","#d4a017","#17a2b8","#d62728","#7f7f7f","#8c564b","#e377c2"];
const COORD_NAMES = ["coordinate location","coordinate_location","coordinates","coordinate"];

const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const norm = t => String(t).normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

// Data that changes whenever a dataset is loaded
let RAW = null, R = [], COLS = [], rels = [], relColor = {}, PRINTERS = [];
let Y0 = 1500, Y1 = 1700, D0 = 1500, D1 = 1700, PRINTER_COL = -1;

const S = { q:"", lang:"", fmt:"", ms:"", rels:new Set(), yMin:1500, yMax:1700,
            place:null, mode:"off", t:1500, sortCol:null, sortDir:1, page:0,
            groups:new Map(), scope:[], filtered:[] };

// ================================================================ CSV reading in the browser
function parseCSV(text){
  if (text.charCodeAt(0) === 0xFEFF) text = text.slice(1);
  const firstLine = text.split(/\r?\n/, 1)[0];
  const counts = { ",":0, ";":0, "\t":0 };
  let inQ = false;
  for (const ch of firstLine) {
    if (ch === '"') inQ = !inQ;
    else if (!inQ && ch in counts) counts[ch]++;
  }
  const delim = Object.keys(counts).sort((a, b) => counts[b] - counts[a])[0];
  const rows = []; let row = [], cell = "", q = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (q) {
      if (ch === '"') { if (text[i+1] === '"') { cell += '"'; i++; } else q = false; }
      else cell += ch;
    }
    else if (ch === '"') q = true;
    else if (ch === delim) { row.push(cell); cell = ""; }
    else if (ch === "\n" || ch === "\r") {
      if (ch === "\r" && text[i+1] === "\n") i++;
      row.push(cell); cell = ""; rows.push(row); row = [];
    }
    else cell += ch;
  }
  if (cell !== "" || row.length) { row.push(cell); rows.push(row); }
  return rows.filter(r => !(r.length === 1 && r[0] === ""));
}

function fixText(s){
  if (!/[\u0080-ÿ]/.test(s)) return s;
  const bytes = [];
  for (const ch of s) { const c = ch.codePointAt(0); if (c > 255) return s; bytes.push(c); }
  try { return new TextDecoder("utf-8", { fatal:true }).decode(Uint8Array.from(bytes)); }
  catch (e) { return s; }
}

function parseCoord(v){
  const t = String(v == null ? "" : v).trim();
  if (!t) return [null, null, "missing"];
  const parts = t.split(",");
  if (parts.length !== 2) return [null, null, "format_error"];
  const num = s => /^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$/.test(s.trim()) ? Number(s) : NaN;
  const lat = num(parts[0]), lon = num(parts[1]);
  if (!isFinite(lat) || !isFinite(lon)) return [null, null, "format_error"];
  if (Math.abs(lat) > 90 || Math.abs(lon) > 180) return [null, null, "out_of_range"];
  return [lat, lon, "ok"];
}

function readYear(get){
  for (const name of ["year_numeric", "year"]) {
    const t = get(name);
    if (!t) continue;
    const n = Number(t);
    if (isFinite(n)) return Math.round(n);
    const m = t.match(/\d{4}/);
    if (m) return +m[0];
  }
  return null;
}
const lab = v => { v = String(v).trim(); return v ? v : "(blank)"; };

// ================================================================ build the working dataset
function setDataset(raw){
  RAW = raw;
  stopPlay();
  const repair = $("repairChk").checked;
  const cols = raw.columns.map(c => String(c).trim());
  const ix = n => cols.indexOf(n);
  const warnings = [];

  let iCoord = -1;
  COORD_NAMES.forEach(n => { if (iCoord < 0 && ix(n) >= 0) iCoord = ix(n); });
  if (iCoord < 0) warnings.push("No coordinate column found (expected \"coordinate location\"). The map stays empty.");
  if (ix("edition_id") < 0) warnings.push("No edition_id column found. Row numbers are used instead.");
  ["place_interpreted", "place_relationship", "printer"].forEach(n => {
    if (ix(n) < 0) warnings.push("Column \"" + n + "\" was not found; features that need it are limited.");
  });

  COLS = cols;
  PRINTER_COL = ix("printer");
  const havePI = ix("place_interpreted") >= 0;

  R = raw.rows.map((row, i) => {
    const cells = cols.map((_, j) => { const v = row[j] == null ? "" : String(row[j]); return repair ? fixText(v) : v; });
    const g = n => { const j = ix(n); return j < 0 ? "" : cells[j].trim(); };
    const c = iCoord < 0 ? [null, null, "missing"] : parseCoord(cells[iCoord]);
    const r = {
      i: i,
      id: ix("edition_id") < 0 ? String(i + 1) : g("edition_id"),
      place: g("place"),
      pi: havePI ? g("place_interpreted") : (g("place_norm") || g("place")),
      rel: lab(g("place_relationship")),
      ms: lab(g("match_status")),
      lang: lab(g("language")),
      fmt: lab(g("format")),
      printer: g("printer"),
      year: readYear(g),
      lat: c[0], lon: c[1], st: c[2],
      cells: cells
    };
    r.hay = cells.join(" ").toLowerCase();
    r.key = r.lat == null ? null : (r.pi || "(no place name)") + "|" + r.lat + "|" + r.lon;
    return r;
  });

  if (ix("edition_id") >= 0) {
    const ids = new Set(R.map(r => r.id));
    if (ids.size !== R.length) warnings.push("edition_id is not unique (" + ids.size + " different values in " + R.length + " rows).");
  }
  if (!repair && R.some(r => r.cells.some(v => /Ã[\u0080-¿]/.test(v)))) {
    warnings.push("Some text looks garbled (e.g. NÃ¼rnberg). Tick \"Repair garbled accents\" to display it correctly.");
  }

  // relationships and colours
  const rc = {};
  R.forEach(r => { rc[r.rel] = (rc[r.rel] || 0) + 1; });
  rels = Object.keys(rc).sort((a, b) => rc[b] - rc[a]);
  relColor = {};
  rels.forEach((v, i) => { relColor[v] = PALETTE[i % PALETTE.length]; });

  // years
  const ys = R.map(r => r.year).filter(y => y != null);
  Y0 = ys.length ? Math.min.apply(null, ys) : 1500;
  Y1 = ys.length ? Math.max.apply(null, ys) : 1700;
  D0 = Math.floor(Y0 / 10) * 10; D1 = Math.floor(Y1 / 10) * 10;

  // controls
  const fill = (id, vals) => { $(id).innerHTML = '<option value="">All</option>' + vals.map(v => '<option>' + esc(v) + '</option>').join(""); };
  const uniq = k => Array.from(new Set(R.map(r => r[k]))).sort();
  fill("fLang", uniq("lang")); fill("fFmt", uniq("fmt")); fill("fMs", uniq("ms"));
  ["yMin", "yMax"].forEach(id => { $(id).min = Y0; $(id).max = Y1; });
  $("timeSlider").min = D0; $("timeSlider").max = D1;
  $("relBoxes").innerHTML = rels.map(k =>
    '<label><input type="checkbox" data-rel="' + esc(k) + '" checked><span class="swatch" style="background:' + relColor[k] + '"></span>' + esc(k) + '</label>').join("");

  // printers for predictive search
  const pm = {};
  R.forEach(r => {
    if (!r.printer) return;
    const p = pm[r.printer] || (pm[r.printer] = { name:r.printer, norm:norm(r.printer), n:0, keys:new Set() });
    p.n++;
    if (r.key) p.keys.add(r.key);
  });
  PRINTERS = Object.keys(pm).map(k => { const p = pm[k]; p.places = p.keys.size; return p; });

  buildQuality();
  $("warn").innerHTML = warnings.map(w => "<p>⚠ " + esc(w) + "</p>").join("");
  $("srcInfo").textContent = (raw.name || "CSV") + ": " + R.length + " rows × " + cols.length + " columns";
  $("embeddedBtn").hidden = !(PAYLOAD.embedded && raw !== PAYLOAD.embedded);

  const usable = R.filter(r => r.lat != null).length;
  $("subtitle").textContent = R.length + " records · " + usable + " with usable coordinates (" +
    (R.length ? (usable / R.length * 100).toFixed(1) : 0) + "%)" + (ys.length ? " · years " + Y0 + "–" + Y1 : "");

  resetFilters(true);
  $("printerInput").value = ""; acClose(); showTrail("");
  render();
  fitToRows(R);
}

function resetFilters(silent){
  stopPlay();
  S.q = ""; S.lang = ""; S.fmt = ""; S.ms = ""; S.rels = new Set(rels);
  S.yMin = Y0; S.yMax = Y1; S.place = null; S.mode = "off"; S.t = D0; S.page = 0;
  $("q").value = ""; $("fLang").value = ""; $("fFmt").value = ""; $("fMs").value = "";
  $("yMin").value = Y0; $("yMax").value = Y1; $("timeMode").value = "off"; $("timeSlider").value = D0;
  document.querySelectorAll("#relBoxes input").forEach(b => { b.checked = true; });
  if (!silent) render();
}

// ================================================================ file loading (local CSV)
function loadFile(file){
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    const rows = parseCSV(String(reader.result));
    if (rows.length < 2) { $("warn").innerHTML = "<p>⚠ \"" + esc(file.name) + "\" has no data rows.</p>"; return; }
    const header = rows[0], width = header.length;
    const body = rows.slice(1).map(r => {
      if (r.length > width) return r.slice(0, width);
      while (r.length < width) r.push("");
      return r;
    });
    setDataset({ name:file.name, columns:header, rows:body });
  };
  reader.onerror = () => { $("warn").innerHTML = "<p>⚠ The file could not be read.</p>"; };
  reader.readAsText(file, "utf-8");
}
$("loadBtn").addEventListener("click", () => $("fileInput").click());
$("fileInput").addEventListener("change", () => { loadFile($("fileInput").files[0]); $("fileInput").value = ""; });
$("embeddedBtn").addEventListener("click", () => { if (PAYLOAD.embedded) setDataset(PAYLOAD.embedded); });
$("repairChk").addEventListener("change", () => { if (RAW) setDataset(RAW); });
let dragDepth = 0;
window.addEventListener("dragenter", e => { e.preventDefault(); dragDepth++; document.body.classList.add("dragging"); });
window.addEventListener("dragleave", e => { e.preventDefault(); dragDepth = Math.max(0, dragDepth - 1); if (!dragDepth) document.body.classList.remove("dragging"); });
window.addEventListener("dragover", e => e.preventDefault());
window.addEventListener("drop", e => {
  e.preventDefault(); dragDepth = 0; document.body.classList.remove("dragging");
  if (e.dataTransfer && e.dataTransfer.files.length) loadFile(e.dataTransfer.files[0]);
});

// ================================================================ filter controls
$("q").addEventListener("input", () => { S.q = $("q").value; S.page = 0; render(); });
$("fLang").addEventListener("change", () => { S.lang = $("fLang").value; S.page = 0; render(); });
$("fFmt").addEventListener("change", () => { S.fmt = $("fFmt").value; S.page = 0; render(); });
$("fMs").addEventListener("change", () => { S.ms = $("fMs").value; S.page = 0; render(); });
$("relBoxes").addEventListener("change", e => {
  const k = e.target.getAttribute("data-rel");
  if (k == null) return;
  if (e.target.checked) S.rels.add(k); else S.rels.delete(k);
  S.page = 0; render();
});
$("yMin").addEventListener("input", () => {
  S.yMin = +$("yMin").value;
  if (S.yMin > S.yMax) { S.yMax = S.yMin; $("yMax").value = S.yMax; }
  S.page = 0; render();
});
$("yMax").addEventListener("input", () => {
  S.yMax = +$("yMax").value;
  if (S.yMax < S.yMin) { S.yMin = S.yMax; $("yMin").value = S.yMin; }
  S.page = 0; render();
});
$("resetBtn").addEventListener("click", () => resetFilters(false));

function currentRange(){
  if (S.mode === "cum") return [Y0, S.t + 9];
  if (S.mode === "win") return [S.t, S.t + 9];
  return [S.yMin, S.yMax];
}
function fullRange(){ return S.mode === "off" && S.yMin === Y0 && S.yMax === Y1; }

function filterRows(){
  const range = currentRange(), lo = range[0], hi = range[1];
  const full = fullRange();
  const q = S.q.trim().toLowerCase();
  return R.filter(r => {
    if (q && !r.hay.includes(q)) return false;
    if (S.lang && r.lang !== S.lang) return false;
    if (S.fmt && r.fmt !== S.fmt) return false;
    if (S.ms && r.ms !== S.ms) return false;
    if (!S.rels.has(r.rel)) return false;
    if (r.year == null) { if (!full) return false; }
    else if (r.year < lo || r.year > hi) return false;
    return true;
  });
}

function groupPlaces(rows){
  const m = new Map();
  rows.forEach(r => {
    if (!r.key) return;
    let g = m.get(r.key);
    if (!g) { g = { key:r.key, name:r.pi || "(no place name)", lat:r.lat, lon:r.lon, n:0, rc:{} }; m.set(r.key, g); }
    g.n++;
    g.rc[r.rel] = (g.rc[r.rel] || 0) + 1;
  });
  return m;
}

// ================================================================ map
const map = L.map("map", { center:[50,10], zoom:4, minZoom:3, maxZoom:6 });
const tiles = L.tileLayer("https://tiles.openfreemap.org/natural_earth/ne2sr/{z}/{x}/{y}.png", {
  maxZoom: 6, maxNativeZoom: 6,
  attribution: '&copy; <a href="https://openfreemap.org">OpenFreeMap</a> &amp; <a href="https://www.naturalearthdata.com">Natural Earth</a>'
}).addTo(map);
const circles = L.layerGroup().addTo(map);
const trailLayer = L.layerGroup().addTo(map);
L.control.layers({ "OpenFreeMap Natural Earth": tiles }, { "Printer trail": trailLayer }, { collapsed:true }).addTo(map);

const legend = L.control({ position: "bottomleft" });
legend.onAdd = function(){
  const div = L.DomUtil.create("div", "legend");
  L.DomEvent.disableClickPropagation(div);
  return div;
};
legend.addTo(map);

map.on("click", () => { if (S.place) { S.place = null; render(); } });

function pieSVG(g, d){
  const c = d/2, r = c - 2, total = g.n;
  const ents = rels.filter(k => g.rc[k]).map(k => [k, g.rc[k]]);
  let out = '<svg width="'+d+'" height="'+d+'" viewBox="0 0 '+d+' '+d+'" xmlns="http://www.w3.org/2000/svg">';
  if (ents.length === 1) {
    out += '<circle cx="'+c+'" cy="'+c+'" r="'+r+'" fill="'+relColor[ents[0][0]]+'" stroke="#fff" stroke-width="2"><title>'+esc(ents[0][0])+': '+ents[0][1]+'</title></circle>';
  } else {
    let a0 = -Math.PI/2;
    ents.forEach(e => {
      const k = e[0], n = e[1];
      const a1 = a0 + 2*Math.PI*n/total;
      const x0 = c + r*Math.cos(a0), y0 = c + r*Math.sin(a0);
      const x1 = c + r*Math.cos(a1), y1 = c + r*Math.sin(a1);
      const large = (a1 - a0) > Math.PI ? 1 : 0;
      out += '<path d="M'+c+' '+c+' L'+x0+' '+y0+' A'+r+' '+r+' 0 '+large+' 1 '+x1+' '+y1+' Z" fill="'+relColor[k]+'" stroke="#fff" stroke-width="2"><title>'+esc(k)+': '+n+'</title></path>';
      a0 = a1;
    });
  }
  out += '<circle cx="'+c+'" cy="'+c+'" r="'+(r*0.42)+'" fill="#fff"/><text x="'+c+'" y="'+(c+4)+'" text-anchor="middle" font-size="12" font-weight="700" fill="#222">'+total+'</text></svg>';
  return out;
}

function drawMap(){
  circles.clearLayers();
  S.groups.forEach(g => {
    const rad = 3 + 2.2*Math.sqrt(g.n);
    const tip = esc(g.name) + ": " + g.n + " edition" + (g.n === 1 ? "" : "s");
    if (g.key === S.place) {
      const d = Math.max(64, 2*rad + 18);
      const icon = L.divIcon({ className:"pie-icon", html:pieSVG(g, d), iconSize:[d,d], iconAnchor:[d/2,d/2] });
      L.marker([g.lat, g.lon], { icon:icon, zIndexOffset:1000 })
        .bindTooltip(tip)
        .on("click", e => { L.DomEvent.stopPropagation(e); S.place = null; render(); })
        .addTo(circles);
    } else {
      L.circleMarker([g.lat, g.lon], { radius:rad, color:"#6d1230", weight:1, fillColor:"#c0392b", fillOpacity:0.6 })
        .bindTooltip(tip)
        .on("click", e => { L.DomEvent.stopPropagation(e); selectPlace(g.key, false); })
        .addTo(circles);
    }
  });
}

function updateLegend(filtered){
  const el = legend.getContainer();
  const sw = k => '<span class="swatch" style="background:'+relColor[k]+'"></span>';
  if (S.place && S.groups.has(S.place)) {
    const g = S.groups.get(S.place);
    el.innerHTML = '<b>'+esc(g.name)+'</b><br>'+g.n+' edition'+(g.n===1?'':'s')+
      '<br><small>lat '+g.lat.toFixed(4)+', lon '+g.lon.toFixed(4)+'</small><hr style="margin:4px 0">'+
      rels.filter(k => g.rc[k]).map(k => sw(k)+esc(k)+': <b>'+g.rc[k]+'</b> ('+Math.round(g.rc[k]/g.n*100)+'%)').join("<br>")+
      '<br><small style="color:#6b6b6b">Click the pie or the map to close.</small>';
  } else {
    const counts = {};
    filtered.forEach(r => { counts[r.rel] = (counts[r.rel] || 0) + 1; });
    el.innerHTML = '<b>Place relationships</b><br><small style="color:#6b6b6b">Click a circle to turn it into a pie chart.</small><hr style="margin:4px 0">'+
      rels.map(k => sw(k)+esc(k)+': '+(counts[k] || 0)).join("<br>");
  }
}

function selectPlace(key, fly){
  S.place = key;
  S.page = 0;
  render();
  if (fly && S.groups.has(key)) {
    const g = S.groups.get(key);
    map.flyTo([g.lat, g.lon], Math.max(5, Math.min(6, map.getZoom())), { duration:0.6 });
  }
}

function fitToRows(rows){
  const pts = rows.filter(r => r.lat != null).map(r => [r.lat, r.lon]);
  if (pts.length) map.fitBounds(pts, { padding:[30,30], maxZoom:5 });
}

// ================================================================ KPIs
function renderKPIs(scope){
  const mapped = scope.filter(r => r.lat != null);
  const places = new Set(mapped.map(r => r.key)).size;
  const printers = new Set(scope.map(r => r.printer).filter(Boolean)).size;
  const ys = scope.map(r => r.year).filter(y => y != null);
  const yr = ys.length ? Math.min.apply(null, ys) + "–" + Math.max.apply(null, ys) : "–";
  const cov = scope.length ? (mapped.length/scope.length*100).toFixed(0) + "%" : "–";
  const card = (v, t) => '<div class="card kpi"><b>'+v+'</b><span>'+t+'</span></div>';
  $("kpis").innerHTML = card(scope.length + " / " + R.length, "records shown") +
    card(places, "places on the map") + card(cov, "records with coordinates") +
    card(printers, "distinct printers") + card(yr, "years covered");
}

// ================================================================ charts
Chart.defaults.font.size = 11;
const charts = {};
const ctitle = t => ({ display:true, text:t });
charts.decade = new Chart($("cDecade"), { type:"bar", data:{ labels:[], datasets:[] },
  options:{ responsive:true, maintainAspectRatio:false, animation:{ duration:200 },
    scales:{ x:{ stacked:true }, y:{ stacked:true, beginAtZero:true } },
    plugins:{ legend:{ display:false }, title:ctitle("Editions by decade (colour = place relationship)") } } });
charts.rel = new Chart($("cRel"), { type:"doughnut", data:{ labels:[], datasets:[{ data:[], backgroundColor:[] }] },
  options:{ responsive:true, maintainAspectRatio:false, animation:{ duration:200 },
    plugins:{ legend:{ position:"right", labels:{ boxWidth:10 } }, title:ctitle("Place relationships") } } });
charts.lang = new Chart($("cLang"), { type:"bar", data:{ labels:[], datasets:[{ data:[], backgroundColor:"#8b1e3f" }] },
  options:{ responsive:true, maintainAspectRatio:false, animation:{ duration:200 },
    plugins:{ legend:{ display:false }, title:ctitle("Languages") }, scales:{ y:{ beginAtZero:true } } } });
charts.places = new Chart($("cPlaces"), { type:"bar", data:{ labels:[], datasets:[{ data:[], backgroundColor:"#c0392b" }] },
  options:{ indexAxis:"y", responsive:true, maintainAspectRatio:false, animation:{ duration:200 },
    plugins:{ legend:{ display:false }, title:ctitle("Top 10 places by number of editions") }, scales:{ x:{ beginAtZero:true } } } });

function tally(rows, fn){
  const m = {};
  rows.forEach(r => { const k = fn(r); if (k) m[k] = (m[k] || 0) + 1; });
  return Object.entries(m).sort((a, b) => b[1] - a[1]);
}

function renderCharts(scope){
  const decades = [];
  for (let d = D0; d <= D1; d += 10) decades.push(d);
  const grid = {};
  rels.forEach(k => { grid[k] = {}; });
  scope.forEach(r => {
    if (r.year == null) return;
    const d = Math.floor(r.year/10)*10;
    grid[r.rel][d] = (grid[r.rel][d] || 0) + 1;
  });
  charts.decade.data.labels = decades.map(d => d + "s");
  charts.decade.data.datasets = rels.map(k => ({ label:k, backgroundColor:relColor[k], data:decades.map(d => grid[k][d] || 0) }));
  charts.decade.update();

  const rt = tally(scope, r => r.rel);
  charts.rel.data.labels = rt.map(x => x[0]);
  charts.rel.data.datasets[0].data = rt.map(x => x[1]);
  charts.rel.data.datasets[0].backgroundColor = rt.map(x => relColor[x[0]]);
  charts.rel.update();

  const lt = tally(scope, r => r.lang).slice(0, 8);
  charts.lang.data.labels = lt.map(x => x[0]);
  charts.lang.data.datasets[0].data = lt.map(x => x[1]);
  charts.lang.update();

  const pt = tally(scope, r => r.pi).slice(0, 10);
  charts.places.data.labels = pt.map(x => x[0]);
  charts.places.data.datasets[0].data = pt.map(x => x[1]);
  charts.places.update();
}

// ================================================================ table
function cellVal(r, i){ return i < COLS.length ? r.cells[i] : r.st; }

function renderTable(scope){
  const rows = scope.slice();
  if (S.sortCol != null) {
    const i = S.sortCol, dir = S.sortDir;
    rows.sort((a, b) => {
      const x = cellVal(a, i), y = cellVal(b, i);
      const nx = Number(x), ny = Number(y);
      if (x !== "" && y !== "" && !isNaN(nx) && !isNaN(ny)) return (nx - ny) * dir;
      return String(x).localeCompare(String(y)) * dir;
    });
  }
  const size = +$("pageSize").value;
  const pages = Math.max(1, Math.ceil(rows.length / size));
  if (S.page >= pages) S.page = pages - 1;
  const start = S.page * size;
  const slice = rows.slice(start, start + size);

  $("thead").innerHTML = COLS.length ? "<tr>" + COLS.concat(["map status (derived)"]).map((c, i) =>
    '<th data-i="'+i+'">'+esc(c)+(S.sortCol === i ? (S.sortDir === 1 ? " ▲" : " ▼") : "")+'</th>').join("") + "</tr>" : "";

  $("tbody").innerHTML = slice.map(r => {
    const tds = r.cells.map((v, i) => {
      if (i === PRINTER_COL && v) return '<td title="'+esc(v)+'"><span class="plink" data-printer="'+esc(v.trim())+'">'+esc(v)+'</span></td>';
      return '<td title="'+esc(v)+'">'+esc(v)+'</td>';
    }).join("");
    const st = r.st === "ok" ? "on map" : r.st;
    return '<tr data-i="'+r.i+'" class="'+(r.key && r.key === S.place ? "sel" : "")+'">'+tds+'<td>'+esc(st)+'</td></tr>';
  }).join("");

  $("tableInfo").textContent = !R.length
    ? "No data loaded yet. Use \"Load a CSV from your computer\"."
    : rows.length
      ? "Showing " + (start + 1) + "–" + (start + slice.length) + " of " + rows.length + " records" +
        (rows.length !== R.length ? " (filtered from " + R.length + ")" : "")
      : "No records match the current filters.";
  $("pgInfo").textContent = " page " + (S.page + 1) + " / " + pages + " ";
  $("prevPg").disabled = S.page === 0;
  $("nextPg").disabled = S.page >= pages - 1;
}

$("thead").addEventListener("click", e => {
  const th = e.target.closest("th");
  if (!th) return;
  const i = +th.getAttribute("data-i");
  if (S.sortCol === i) S.sortDir = -S.sortDir; else { S.sortCol = i; S.sortDir = 1; }
  render();
});
$("tbody").addEventListener("click", e => {
  const link = e.target.closest(".plink");
  if (link) {
    const name = link.getAttribute("data-printer");
    $("printerInput").value = name; acClose();
    showTrail(name);
    return;
  }
  const tr = e.target.closest("tr");
  if (!tr) return;
  const r = R[+tr.getAttribute("data-i")];
  if (r && r.key) selectPlace(r.key, true);
});
$("pageSize").addEventListener("change", () => { S.page = 0; render(); });
$("prevPg").addEventListener("click", () => { S.page = Math.max(0, S.page - 1); render(); });
$("nextPg").addEventListener("click", () => { S.page += 1; render(); });
$("zoomBtn").addEventListener("click", () => fitToRows(S.scope));

// ================================================================ Time Machine
let timer = null;
function stopPlay(){
  if (timer) { clearInterval(timer); timer = null; }
  $("playBtn").textContent = "▶ Play";
}
$("timeMode").addEventListener("change", () => {
  S.mode = $("timeMode").value;
  if (S.mode === "off") stopPlay();
  S.page = 0; render();
});
$("timeSlider").addEventListener("input", () => { S.t = +$("timeSlider").value; S.page = 0; render(); });
$("playBtn").addEventListener("click", () => {
  if (timer) { stopPlay(); return; }
  if (S.mode === "off") { S.mode = "cum"; $("timeMode").value = "cum"; }
  if (S.t >= D1) S.t = D0;
  $("timeSlider").value = S.t;
  $("playBtn").textContent = "⏸ Pause";
  render();
  timer = setInterval(() => {
    if (S.t >= D1) { stopPlay(); return; }
    S.t += 10;
    $("timeSlider").value = S.t;
    S.page = 0;
    render();
  }, 800);
});

// ================================================================ Printer Trails
const TRAIL_HELP = "Suggestions appear as you type (capitals and accents are ignored) and show each printer's editions and places. You can also click a printer name in the table.";

function showTrail(name){
  trailLayer.clearLayers();
  const box = $("trailInfo");
  if (!name) { box.textContent = TRAIL_HELP; return; }
  const rows = R.filter(r => r.printer === name && r.lat != null && r.year != null).sort((a, b) => a.year - b.year);
  const stops = [];
  rows.forEach(r => {
    const last = stops[stops.length - 1];
    if (last && last.key === r.key) { last.y1 = r.year; last.n++; }
    else stops.push({ key:r.key, name:r.pi || r.place || "(no place name)", lat:r.lat, lon:r.lon, y0:r.year, y1:r.year, n:1 });
  });
  if (!stops.length) { box.textContent = "No dated editions with usable coordinates for this printer."; return; }
  if (stops.length >= 2) {
    L.polyline(stops.map(s => [s.lat, s.lon]), { color:"#1d4e89", weight:3, dashArray:"6 6", opacity:0.85 }).addTo(trailLayer);
  }
  stops.forEach((s, i) => {
    L.marker([s.lat, s.lon], { icon:L.divIcon({ className:"", html:'<div class="trail-num">'+(i+1)+'</div>', iconSize:[20,20], iconAnchor:[10,10] }), zIndexOffset:2000 })
      .bindTooltip((i+1)+". "+esc(s.name)+" ("+s.y0+(s.y1 !== s.y0 ? "–"+s.y1 : "")+")")
      .addTo(trailLayer);
  });
  box.innerHTML = "<b>"+esc(name)+"</b>"+(stops.length < 2 ? " – recorded at one place only." : "")+
    "<ol>"+stops.map(s => "<li>"+esc(s.name)+", "+s.y0+(s.y1 !== s.y0 ? "–"+s.y1 : "")+" ("+s.n+" edition"+(s.n === 1 ? "" : "s")+")</li>").join("")+"</ol>";
  map.fitBounds(L.latLngBounds(stops.map(s => [s.lat, s.lon])), { padding:[40,40], maxZoom:5 });
}
$("clearTrail").addEventListener("click", () => { $("printerInput").value = ""; acClose(); showTrail(""); });

// ---- predictive search: suggestions built from the loaded CSV
const acInput = $("printerInput"), acList = $("acList");
let acItems = [], acActive = -1;

function hilite(name, q){
  if (!q) return esc(name);
  const nn = norm(name), i = nn.indexOf(q);
  if (i < 0 || nn.length !== name.length) return esc(name);
  return esc(name.slice(0, i)) + "<mark>" + esc(name.slice(i, i + q.length)) + "</mark>" + esc(name.slice(i + q.length));
}
function acSuggest(raw){
  const q = norm(raw.trim());
  let hits;
  if (!q) {
    hits = PRINTERS.filter(p => p.places >= 2).sort((a, b) => b.places - a.places || b.n - a.n);
  } else {
    const found = [];
    PRINTERS.forEach(p => {
      const i = p.norm.indexOf(q);
      if (i < 0) return;
      found.push({ p:p, rank: i === 0 ? 0 : (p.norm[i - 1] === " " ? 1 : 2) });
    });
    found.sort((a, b) => a.rank - b.rank || b.p.places - a.p.places || b.p.n - a.p.n || a.p.name.localeCompare(b.p.name));
    hits = found.map(h => h.p);
  }
  return { q:q, hits:hits.slice(0, 8), total:hits.length };
}
function acRender(){
  const res = acSuggest(acInput.value);
  acItems = res.hits; acActive = -1;
  if (!acItems.length) {
    acList.innerHTML = '<div class="acnone">' + (PRINTERS.length ? 'No printer matches "' + esc(acInput.value) + '"' : 'No printer column loaded') + '</div>';
  } else {
    acList.innerHTML = acItems.map((p, i) =>
      '<div role="option" data-i="'+i+'"><span>'+hilite(p.name, res.q)+'</span><small>'+p.n+' edition'+(p.n === 1 ? "" : "s")+' · '+p.places+' place'+(p.places === 1 ? "" : "s")+'</small></div>').join("") +
      (res.total > acItems.length ? '<div class="acnone">+ ' + (res.total - acItems.length) + ' more – keep typing</div>' : "");
  }
  acList.hidden = false;
  acInput.setAttribute("aria-expanded", "true");
}
function acClose(){ acList.hidden = true; acActive = -1; acInput.setAttribute("aria-expanded", "false"); }
function acPick(i){
  const p = acItems[i];
  if (!p) return;
  acInput.value = p.name;
  acClose();
  showTrail(p.name);
}
function acHighlight(){
  Array.from(acList.children).forEach((el, i) => el.classList.toggle("act", i === acActive));
  const el = acList.children[acActive];
  if (el && el.scrollIntoView) el.scrollIntoView({ block:"nearest" });
}
acInput.addEventListener("input", acRender);
acInput.addEventListener("focus", acRender);
acInput.addEventListener("keydown", e => {
  if (e.key === "ArrowDown") {
    e.preventDefault(); if (acList.hidden) acRender();
    if (acItems.length) { acActive = (acActive + 1) % acItems.length; acHighlight(); }
  } else if (e.key === "ArrowUp") {
    e.preventDefault();
    if (acItems.length) { acActive = (acActive - 1 + acItems.length) % acItems.length; acHighlight(); }
  } else if (e.key === "Enter") {
    e.preventDefault();
    if (acActive >= 0) acPick(acActive);
    else {
      const typed = norm(acInput.value.trim());
      const exact = PRINTERS.find(p => p.norm === typed);
      if (exact) { acInput.value = exact.name; acClose(); showTrail(exact.name); }
      else if (acItems.length === 1) acPick(0);
    }
  } else if (e.key === "Escape") acClose();
});
acList.addEventListener("mousedown", e => {
  const el = e.target.closest("[data-i]");
  if (el) { e.preventDefault(); acPick(+el.getAttribute("data-i")); }
});
document.addEventListener("click", e => { if (!e.target.closest(".ac")) acClose(); });

// ================================================================ data quality
function buildQuality(){
  const statusCounts = {}, perPlace = {}, perPair = {};
  R.forEach(r => {
    statusCounts[r.st] = (statusCounts[r.st] || 0) + 1;
    if (r.lat != null && r.pi) {
      const pair = r.lat + "," + r.lon;
      (perPlace[r.pi] = perPlace[r.pi] || new Set()).add(pair);
      (perPair[pair] = perPair[pair] || new Set()).add(r.pi);
    }
  });
  const multi = Object.keys(perPlace).filter(k => perPlace[k].size > 1).sort();
  const shared = Object.keys(perPair).filter(k => perPair[k].size > 1).sort();
  let h = "<p>Coordinate parsing: " + (Object.keys(statusCounts).map(k => esc(k) + " " + statusCounts[k]).join(" · ") || "no data") + "</p>";
  h += "<p><b>Places with more than one coordinate pair</b></p>";
  h += multi.length ? "<ul>" + multi.map(k => "<li>" + esc(k) + ": " + Array.from(perPlace[k]).map(esc).join(" | ") + "</li>").join("") + "</ul>" : "<p>None</p>";
  h += "<p><b>Coordinate pairs shared by more than one place</b></p>";
  h += shared.length ? "<ul>" + shared.map(k => "<li>" + esc(k) + ": " + Array.from(perPair[k]).map(esc).join(" | ") + "</li>").join("") + "</ul>" : "<p>None</p>";
  $("quality").innerHTML = h;
}

// ================================================================ main render
function syncControls(){
  const timeOn = S.mode !== "off";
  $("yMin").disabled = timeOn; $("yMax").disabled = timeOn;
  $("timeSlider").disabled = !timeOn;
  $("yLabel").textContent = S.yMin + "–" + S.yMax;
  $("timeLabel").textContent = S.mode === "cum" ? "Up to " + (S.t + 9)
                              : S.mode === "win" ? S.t + "s only" : "Time Machine is off";
  $("chips").innerHTML = S.place && S.groups.has(S.place)
    ? '<span class="chip" id="chipPlace" title="Click to remove">Place: '+esc(S.groups.get(S.place).name)+' ✕</span>' : "";
  const chip = $("chipPlace");
  if (chip) chip.addEventListener("click", () => { S.place = null; render(); });
}

function render(){
  const filtered = filterRows();
  S.groups = groupPlaces(filtered);
  if (S.place && !S.groups.has(S.place)) S.place = null;
  const scope = S.place ? filtered.filter(r => r.key === S.place) : filtered;
  S.filtered = filtered;
  S.scope = scope;
  syncControls();
  drawMap();
  updateLegend(filtered);
  renderKPIs(scope);
  renderCharts(scope);
  renderTable(scope);
}

// ================================================================ start
$("repairChk").checked = !!PAYLOAD.repair;
$("trailInfo").textContent = TRAIL_HELP;
if (PAYLOAD.embedded) setDataset(PAYLOAD.embedded);
else {
  $("subtitle").textContent = "No data embedded. Load a CSV file to begin.";
  render();
}
})();
</script>
</body>
</html>
"""

html_text = HTML.replace("__DATA__", payload_json)
Path(OUTPUT_HTML).write_text(html_text, encoding="utf-8")

print(f"Created {OUTPUT_HTML}. Open it in a web browser (an internet connection is needed for the map tiles and libraries).")

# In Jupyter, show a clickable download link for the finished file.
# (Outside Jupyter this part is skipped quietly.)
try:
    from IPython.display import FileLink, display
    display(FileLink(OUTPUT_HTML, result_html_prefix="Download: "))
except Exception:
    pass
