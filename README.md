# Solar Report

[![CI](https://github.com/BrandonJamesEndrizzi/solar_app/actions/workflows/ci.yml/badge.svg)](https://github.com/BrandonJamesEndrizzi/solar_app/actions/workflows/ci.yml)

A daily space weather digest, delivered by email.

Every morning it pulls solar event and alert data from NOAA's Space Weather
Prediction Center, downloads the latest images of the Sun from NASA's Solar
Dynamics Observatory, counts the visible sunspots with OpenCV, has GPT-4 write a
plain-English summary, and emails the result. Recipients each get their own
schedule and their own mix of topics.

## How it works

```
NOAA SWPC  ─┐
            ├─► filter by date ─► format ─┐
NASA SDO   ─┘                              ├─► GPT-4 summary ─► HTML email
                └─► OpenCV sunspot count ─┘
NYT API    ─────────────────────────────────┘
```

The sunspot counter (`analyze_image.py`) thresholds the 193 Å image to isolate the
solar disc, closes small holes with a morphological operation, flood-fills the
background away, and counts the remaining dark regions — filtering out blobs below
a minimum area and contours near the right limb, where the disc edge otherwise
produces false positives.

## Setup

Requires Python 3.10+.

```bash
git clone https://github.com/BrandonJamesEndrizzi/solar_app.git
cd solar_app

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # add your API keys
cp config.ini.example config.ini # add your recipients
```

### Credentials

`.env` holds every secret and is gitignored:

| Variable | Where to get it |
|---|---|
| `EMAIL_ADDRESS` / `EMAIL_PASSWORD` | Your mailbox. Use an app-specific password, not your account password. |
| `OPENAI_API_KEY` | https://platform.openai.com/api-keys |
| `NYT_API_KEY` | https://developer.nytimes.com/ |
| `NOAA_CDO_TOKEN` | https://www.ncdc.noaa.gov/cdo-web/token (only for `weather.py`) |

NOAA SWPC and NASA SDO need no authentication.

### Recipients

Each recipient gets a section in `config.ini` named after their address:

```ini
[Email]
recipients = you@example.com, someone.else@example.com

[you@example.com]
frequency = 1          ; 1 = daily; 0 and 2-6 = weekly on that weekday
themes = solar, news

[someone.else@example.com]
frequency = 2          ; Wednesdays
themes = solar
```

## Running

```bash
python main.py
```

`main.py` decides who is due today, so run it once a day from cron or launchd:

```cron
0 7 * * *  cd /path/to/solar-report && .venv/bin/python main.py
```

Individual modules run standalone for testing:

```bash
python solar.py          # build a solar report, print the sunspot count
python analyze_image.py  # run the sunspot counter, save debug images
python events.py         # dump the raw NOAA feeds
python weather.py        # fetch the NCEI station list
```

## Layout

| File | Purpose |
|---|---|
| `main.py` | Entry point; per-recipient scheduling and delivery |
| `settings.py` | Paths, config loading, credential lookup |
| `solar.py` | Solar pipeline: download, filter, format, analyze |
| `analyze_image.py` | OpenCV sunspot detection |
| `news.py` / `news_NYT.py` | New York Times article retrieval |
| `weather.py` | NCEI weather station list |
| `data_downloading.py` | HTTP fetching and caching |
| `data_filtered.py` | Date-range filtering |
| `data_formatting.py` | JSON to readable text |
| `data_saving.py` | Writing text and JSON to disk |
| `email_formatting.py` | HTML email body |
| `email_sending.py` | SMTP delivery |
| `generate_response.py` | GPT-4 summarization |
| `events.py` | Helpers for dumping the raw feeds |
| `tests/` | Pytest suite for the scheduling, filtering, formatting, and image logic |
| `tokenizer/` | Experiments with a locally fine-tuned T5 model — see its README |

## Development

```bash
pip install pytest
pytest
```

The suite covers the pure logic — scheduling, date filtering, formatting, the
email body, and the sunspot detector (run against synthetic disc images) — and
needs no API keys or network access. CI runs it on every push.

## Data sources

- [NOAA SWPC](https://www.swpc.noaa.gov/) — solar events and space weather alerts
- [NASA SDO](https://sdo.gsfc.nasa.gov/) — solar imagery
- [NCEI Climate Data Online](https://www.ncdc.noaa.gov/cdo-web/) — weather stations
- [New York Times Article Search](https://developer.nytimes.com/) — news

## License

MIT — see [LICENSE](LICENSE).
