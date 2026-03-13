import json
import os
from flask import Flask, jsonify, render_template_string

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
    .tabs { display: flex; gap: 8px; padding: 16px 24px 0; border-bottom: 1px solid #30363d; background: #161b22; }
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
  </style>
</head>
<body>
  <header>
    <h1>⚽ Football Live Scraper</h1>
  </header>
  <div class="tabs" id="tabs">
    {% for key, src in sources.items() %}
    <div class="tab {% if loop.first %}active{% endif %}" onclick="switchTab('{{ key }}')">
      {{ src.label }}
      <span class="badge">{{ src.count }}</span>
    </div>
    {% endfor %}
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
    </div>
  </div>
  <script>
    function switchTab(key) {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('#panels > div').forEach(p => p.classList.remove('active'));
      event.target.closest('.tab').classList.add('active');
      document.getElementById('panel-' + key).classList.add('active');
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


@app.route("/")
def index():
    files = {
        "b67": {"path": os.path.join(OUTPUT_DIR, "b67m.txt"), "label": "Ball67"},
        "kl":  {"path": os.path.join(OUTPUT_DIR, "kl.txt"),  "label": "KL (Dookeela)"},
        "dbf": {"path": os.path.join(OUTPUT_DIR, "dbf.txt"), "label": "DBF (Dooballfree)"},
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

    return render_template_string(HTML, sources=sources)


@app.route("/api/<source>")
def api(source):
    paths = {
        "b67": os.path.join(OUTPUT_DIR, "b67m.txt"),
        "kl":  os.path.join(OUTPUT_DIR, "kl.txt"),
        "dbf": os.path.join(OUTPUT_DIR, "dbf.txt"),
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
