# Football Live Scraper

## Overview
A Python-based football match scraper that collects live match data from multiple Thai football streaming websites. The scraped data is served via a Flask web dashboard.

## Project Structure

- `app.py` — Flask web server serving the dashboard on port 5000
- `scraper.py` — Simple requests-based scraper for dooball66d.com
- `b67_script.py` — Selenium scraper for ball67.com → `output/b67m.txt`
- `kl_script.py` — Selenium scraper for dookeela4.live → `output/kl.txt`
- `dbf_script.py` — Selenium scraper for dooballfree.cam → `output/dbf.txt`
- `playlist.json` — Dooball66 playlist in JSON format
- `website/playlist.w3u` — Architecture doc / W3U playlist
- `worker.js` — Cloudflare Worker for serving playlist.json as an API
- `requirements.txt` — Python dependencies (selenium, beautifulsoup4)
- `.github/workflows/daily_scrape.yml` — GitHub Actions scheduled scraper (runs daily)
- `output/` — Generated JSON output files from scrapers

## Architecture

1. Python scrapers (Selenium + BeautifulSoup) collect live match links from football websites
2. Data saved to `output/*.txt` as JSON
3. GitHub Actions runs scrapers on a daily cron schedule and commits output
4. Flask app (`app.py`) serves a web dashboard displaying scraped match data
5. Cloudflare Worker (`worker.js`) serves `playlist.json` as a proxied API for IPTV players

## Running Locally

The Flask app runs on port 5000:
```
python app.py
```

The Selenium scripts require Chrome and are designed for GitHub Actions / Linux environments.

## Dependencies

- Python 3.12
- Flask (web dashboard)
- selenium, beautifulsoup4, webdriver-manager (scrapers)
- gunicorn (production server)
- Node.js 20 (for Cloudflare Worker development)

## Deployment

Configured for autoscale deployment using gunicorn:
```
gunicorn --bind=0.0.0.0:5000 --reuse-port app:app
```
