import json
import os
from flask import Flask, jsonify, render_template_string, Response, request

app = Flask(__name__)

OUTPUT_DIR = "output"

HTML = """
<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Football Live Scraper</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: sans-serif; background: #0d1117; color: #e6edf3; min-height: 100vh; }
    header { background: #161b22; border-bottom: 1px solid #30363d; padding: 16px 24px; display: flex; align-items: center; gap: 12px; }
    header h1 { font-size: 1.4rem; color: #58a6ff; }
    .tabs { display: flex; gap: 8px; padding: 16px 24px 0; border-bottom: 1px solid #30363d; background: #161b22; flex-wrap: wrap; }
    .tab { padding: 8px 18px; border-radius: 6px 6px 0 0; cursor: pointer; font-size: 0.9rem; border: 1px solid transparent; color: #8b949e; }
    .tab.active { background: #0d1117; border-color: #30363d; border-bottom-color: #0d1117; color: #e6edf3; }
    .tab:hover:not(.active) { color: #e6edf3; }
    .content { padding: 24px; }
    .source-info { margin-bottom: 16px; color: #8b949e; font-size: 0.85rem; }
    .group { margin-bottom: 24px; }
    .group-name { font-size: 1rem; font-weight: 600; color: #58a6ff; margin-bottom: 10px; padding: 8px 12px; background: #161b22; border-radius: 6px; border-left: 3px solid #58a6ff; }
    .match { display: flex; align-items: center; gap: 12px; padding: 10px 14px; background: #161b22; border-radius: 6px; margin-bottom: 6px; border: 1px solid #21262d; }
    .match img { width: 28px; height: 28px; object-fit: contain; border-radius: 4px; }
    .match-name { flex: 1; font-size: 0.9rem; }
    .match-info { font-size: 0.78rem; color: #8b949e; }
    .match-link a { font-size: 0.8rem; color: #58a6ff; text-decoration: none; padding: 4px 10px; border: 1px solid #58a6ff; border-radius: 4px; }
    .match-link a:hover { background: #58a6ff22; }
    .empty { color: #8b949e; font-size: 0.9rem; padding: 24px; text-align: center; }
    .badge { background: #21262d; color: #8b949e; font-size: 0.75rem; padding: 2px 8px; border-radius: 10px; margin-left: 8px; }
    #panels > div { display: none; }
    #panels > div.active { display: block; }

    /* Playlist panel */
    .playlist-section { margin-bottom: 32px; }
    .playlist-section h2 { font-size: 1rem; color: #e6edf3; margin-bottom: 12px; font-weight: 600; display: flex; align-items: center; gap: 8px; }
    .playlist-section h2 span { font-size: 0.75rem; color: #8b949e; font-weight: 400; background: #21262d; padding: 2px 8px; border-radius: 10px; }
    .playlist-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; background: #161b22; border: 1px solid #21262d; border-radius: 6px; padding: 10px 14px; }
    .playlist-label { font-size: 0.82rem; color: #8b949e; min-width: 120px; }
    .playlist-url { flex: 1; font-size: 0.78rem; color: #58a6ff; font-family: monospace; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .copy-btn { font-size: 0.78rem; padding: 4px 12px; border: 1px solid #30363d; border-radius: 4px; background: #21262d; color: #e6edf3; cursor: pointer; white-space: nowrap; }
    .copy-btn:hover { border-color: #58a6ff; color: #58a6ff; }
    .copy-btn.copied { border-color: #3fb950; color: #3fb950; }
    .player-note { font-size: 0.8rem; color: #8b949e; margin-bottom: 20px; line-height: 1.6; background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 12px 16px; }
    .player-note strong { color: #e6edf3; }
  </style>
</head>
<body>
  <header>
    <h1>⚽ Football Live Scraper</h1>
  </header>
  <div class="tabs" id="tabs">
    {% for key, src in sources.items() %}
    <div class="tab {% if loop.first %}active{% endif %}" onclick="switchTab('{{ key }}', event)">
      {{ src.label }}
      <span class="badge">{{ src.count }}</span>
    </div>
    {% endfor %}
    <div class="tab" onclick="switchTab('playlists', event)">Playlists</div>
  </div>
  <div class="content">
    <div id="panels">
      {% for key, src in sources.items() %}
      <div id="panel-{{ key }}" class="{% if loop.first %}active{% endif %}">
        <p class="source-info">{{ src.info }}</p>
        {% if src.groups %}
          {% for g in src.groups %}
          <div class="group">
            <div class="group-name">{{ g.name }}</div>
            {% set stations = g.stations if g.stations is defined else (g.groups if g.groups is defined else []) %}
            {% for m in stations %}
            <div class="match">
              {% if m.image %}<img src="{{ m.image }}" onerror="this.style.display='none'">{% endif %}
              <div class="match-name">
                {{ m.name }}
                {% if m.info %}<div class="match-info">{{ m.info }}</div>{% endif %}
              </div>
              {% if m.url %}
              <div class="match-link"><a href="{{ m.url }}" target="_blank">Watch</a></div>
              {% endif %}
            </div>
            {% endfor %}
          </div>
          {% endfor %}
        {% else %}
          <p class="empty">No data available. Run the scraper scripts to generate data.</p>
        {% endif %}
      </div>
      {% endfor %}

      <div id="panel-playlists">
        <p class="player-note">
          Copy a playlist URL and paste it into your IPTV player.<br>
          <strong>Wiseplay</strong> — use .w3u URLs &nbsp;|&nbsp;
          <strong>IPTV Smarters / OTT Navigator</strong> — use .m3u URLs &nbsp;|&nbsp;
          <strong>DBF</strong> has real stream links; B67 and KL link to match pages.
        </p>

        <div class="playlist-section">
          <h2>Ball67 <span>ball67.com</span></h2>
          <div class="playlist-row">
            <span class="playlist-label">M3U (Smarters / OTT)</span>
            <span class="playlist-url" id="u-b67-m3u">{{ base_url }}/playlist/b67.m3u</span>
            <button class="copy-btn" onclick="copyUrl('u-b67-m3u', this)">Copy</button>
          </div>
          <div class="playlist-row">
            <span class="playlist-label">W3U (Wiseplay)</span>
            <span class="playlist-url" id="u-b67-w3u">{{ base_url }}/playlist/b67.w3u</span>
            <button class="copy-btn" onclick="copyUrl('u-b67-w3u', this)">Copy</button>
          </div>
        </div>

        <div class="playlist-section">
          <h2>KL – Dookeela <span>dookeela4.live</span></h2>
          <div class="playlist-row">
            <span class="playlist-label">M3U (Smarters / OTT)</span>
            <span class="playlist-url" id="u-kl-m3u">{{ base_url }}/playlist/kl.m3u</span>
            <button class="copy-btn" onclick="copyUrl('u-kl-m3u', this)">Copy</button>
          </div>
          <div class="playlist-row">
            <span class="playlist-label">W3U (Wiseplay)</span>
            <span class="playlist-url" id="u-kl-w3u">{{ base_url }}/playlist/kl.w3u</span>
            <button class="copy-btn" onclick="copyUrl('u-kl-w3u', this)">Copy</button>
          </div>
        </div>

        <div class="playlist-section">
          <h2>DBF – Dooballfree <span>dooballfree.cam · real streams</span></h2>
          <div class="playlist-row">
            <span class="playlist-label">M3U (Smarters / OTT)</span>
            <span class="playlist-url" id="u-dbf-m3u">{{ base_url }}/playlist/dbf.m3u</span>
            <button class="copy-btn" onclick="copyUrl('u-dbf-m3u', this)">Copy</button>
          </div>
          <div class="playlist-row">
            <span class="playlist-label">W3U (Wiseplay)</span>
            <span class="playlist-url" id="u-dbf-w3u">{{ base_url }}/playlist/dbf.w3u</span>
            <button class="copy-btn" onclick="copyUrl('u-dbf-w3u', this)">Copy</button>
          </div>
        </div>

        <div class="playlist-section">
          <h2>All Sources Combined</h2>
          <div class="playlist-row">
            <span class="playlist-label">M3U (Smarters / OTT)</span>
            <span class="playlist-url" id="u-all-m3u">{{ base_url }}/playlist/all.m3u</span>
            <button class="copy-btn" onclick="copyUrl('u-all-m3u', this)">Copy</button>
          </div>
          <div class="playlist-row">
            <span class="playlist-label">W3U (Wiseplay)</span>
            <span class="playlist-url" id="u-all-w3u">{{ base_url }}/playlist/all.w3u</span>
            <button class="copy-btn" onclick="copyUrl('u-all-w3u', this)">Copy</button>
          </div>
        </div>
      </div>
    </div>
  </div>
  <script>
    function switchTab(key, event) {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('#panels > div').forEach(p => p.classList.remove('active'));
      event.target.closest('.tab').classList.add('active');
      document.getElementById('panel-' + key).classList.add('active');
    }
    function copyUrl(id, btn) {
      const text = document.getElementById(id).textContent.trim();
      navigator.clipboard.writeText(text).then(() => {
        btn.textContent = 'Copied!';
        btn.classList.add('copied');
        setTimeout(() => { btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 2000);
      });
    }
  </script>
</body>
</html>
"""


def load_json(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def get_base_url():
    host = request.host_url.rstrip("/")
    return host


# ── Helpers to normalise each source into a flat list of groups ──────────────

def normalise_b67(data):
    """B67: groups → stations (flat)"""
    result = []
    for g in data.get("groups", []):
        stations = g.get("stations", [])
        if stations:
            result.append({"name": g.get("name", ""), "stations": stations})
    return result


def normalise_kl(data):
    """KL: groups → stations (flat)"""
    result = []
    for g in data.get("groups", []):
        stations = g.get("stations", [])
        if stations:
            result.append({"name": g.get("name", ""), "stations": stations})
    return result


def normalise_dbf(data):
    """DBF: groups (dates) → groups (leagues) → stations (streams)"""
    result = []
    for date_group in data.get("groups", []):
        date_name = date_group.get("name", "")
        for league_group in date_group.get("groups", []):
            league_name = league_group.get("name", "")
            info = league_group.get("info", "")
            image = league_group.get("image", "")
            stations = []
            for st in league_group.get("stations", []):
                stations.append({
                    "name": st.get("name", ""),
                    "image": st.get("image", image),
                    "url": st.get("url", ""),
                    "referer": st.get("referer", ""),
                    "userAgent": st.get("userAgent", ""),
                    "info": info,
                })
            if stations:
                group_name = f"{league_name} [{date_name}]" if date_name else league_name
                result.append({"name": group_name, "stations": stations})
    return result


def build_groups(sources):
    groups = []
    for key in sources:
        data = load_json(sources[key])
        if not data:
            continue
        if key == "b67":
            groups += normalise_b67(data)
        elif key == "kl":
            groups += normalise_kl(data)
        elif key == "dbf":
            groups += normalise_dbf(data)
    return groups


# ── M3U generator ────────────────────────────────────────────────────────────

def generate_m3u(groups, playlist_name="Football Live"):
    lines = [f"#EXTM3U x-tvg-url=\"\" playlist-name=\"{playlist_name}\""]
    for g in groups:
        group_name = g["name"]
        for st in g.get("stations", []):
            name = st.get("name", "")
            url = st.get("url", "")
            logo = st.get("image", "")
            referer = st.get("referer", "")
            ua = st.get("userAgent", "")
            if not url:
                continue
            extinf = f'#EXTINF:-1 group-title="{group_name}" tvg-logo="{logo}" tvg-name="{name}",{name}'
            lines.append(extinf)
            if referer:
                lines.append(f"#EXTVLCOPT:http-referrer={referer}")
            if ua:
                lines.append(f"#EXTVLCOPT:http-user-agent={ua}")
            lines.append(url)
    return "\n".join(lines)


# ── W3U (Wiseplay JSON) generator ────────────────────────────────────────────

def generate_w3u(groups, playlist_name="Football Live"):
    w3u_groups = []
    for g in groups:
        stations = []
        for st in g.get("stations", []):
            entry = {"name": st.get("name", ""), "url": st.get("url", "")}
            if st.get("image"):
                entry["image"] = st["image"]
            if st.get("referer"):
                entry["referer"] = st["referer"]
            if st.get("userAgent"):
                entry["userAgent"] = st["userAgent"]
            stations.append(entry)
        if stations:
            w3u_groups.append({"name": g["name"], "stations": stations})
    return json.dumps({"name": playlist_name, "groups": w3u_groups}, ensure_ascii=False, indent=2)


# ── Source map ───────────────────────────────────────────────────────────────

SOURCE_FILES = {
    "b67": os.path.join(OUTPUT_DIR, "b67m.txt"),
    "kl":  os.path.join(OUTPUT_DIR, "kl.txt"),
    "dbf": os.path.join(OUTPUT_DIR, "dbf.txt"),
}

SOURCE_NAMES = {
    "b67": "Ball67",
    "kl":  "KL Dookeela",
    "dbf": "DBF Dooballfree",
    "all": "Football Live",
}


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    files = {
        "b67": {"path": SOURCE_FILES["b67"], "label": "Ball67"},
        "kl":  {"path": SOURCE_FILES["kl"],  "label": "KL (Dookeela)"},
        "dbf": {"path": SOURCE_FILES["dbf"], "label": "DBF (Dooballfree)"},
    }

    sources = {}
    for key, meta in files.items():
        data = load_json(meta["path"])
        groups = []
        total = 0
        info = ""
        if data:
            info = data.get("info", data.get("name", ""))
            groups = data.get("groups", [])
            for g in groups:
                stations = g.get("stations", g.get("groups", []))
                total += len(stations)
        sources[key] = {
            "label": meta["label"],
            "info": info,
            "groups": groups,
            "count": total,
        }

    return render_template_string(HTML, sources=sources, base_url=get_base_url())


@app.route("/playlist/<name>")
def playlist(name):
    parts = name.rsplit(".", 1)
    if len(parts) != 2:
        return "Not found", 404

    source_key, fmt = parts[0], parts[1].lower()

    if fmt not in ("m3u", "w3u"):
        return "Unsupported format", 400

    if source_key == "all":
        sources = SOURCE_FILES
    elif source_key in SOURCE_FILES:
        sources = {source_key: SOURCE_FILES[source_key]}
    else:
        return "Unknown source", 404

    groups = build_groups(sources)
    playlist_name = SOURCE_NAMES.get(source_key, "Football Live")

    if fmt == "m3u":
        content = generate_m3u(groups, playlist_name)
        return Response(content, mimetype="audio/x-mpegurl",
                        headers={"Content-Disposition": f"attachment; filename={name}"})
    else:
        content = generate_w3u(groups, playlist_name)
        return Response(content, mimetype="application/json",
                        headers={"Content-Disposition": f"attachment; filename={name}"})


@app.route("/api/<source>")
def api(source):
    paths = {
        "b67": SOURCE_FILES["b67"],
        "kl":  SOURCE_FILES["kl"],
        "dbf": SOURCE_FILES["dbf"],
        "playlist": "playlist.json",
    }
    path = paths.get(source)
    if not path:
        return jsonify({"error": "Unknown source"}), 404
    data = load_json(path)
    if data is None:
        return jsonify({"error": "File not found or invalid"}), 404
    return jsonify(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
