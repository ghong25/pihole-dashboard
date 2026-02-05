# Pi-hole Dashboard

A custom dashboard for [Pi-hole](https://pi-hole.net/) with real-time stats, device tracking, timed blocking, and query logs. Built with FastAPI and Vue 3.

## Features

- **Dashboard** — Real-time statistics with interactive charts
  - Total queries, blocked queries, block percentage
  - Query traffic over time (stacked area chart)
  - Top queried and blocked domains (bar charts)
  - Hourly query heatmap (7-day pattern)
  - Auto-refresh every 30 seconds

- **Device Tracking** — Monitor all devices on your network
  - View query stats per device
  - Custom nicknames and icons
  - Per-device top domains and blocked domains
  - Activity timeline

- **Domain Management** — Control your blocklists
  - Add/remove blacklist, whitelist, and regex entries
  - Toggle domains on/off
  - Preset groups (social media, video, news, gaming)

- **Timed Blocking** — Temporarily block distracting sites
  - Quick presets (Reddit 30m, Social Media 1h, etc.)
  - Custom domain + duration
  - Live countdown timers
  - Auto-unblock when time expires

- **Query Logs** — Search and filter DNS queries
  - Filter by status (blocked/allowed/cached)
  - Filter by client, domain, time range
  - One-click domain blocking

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser                               │
│                   Vue 3 SPA (port 8080)                     │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP API
┌─────────────────────────▼───────────────────────────────────┐
│                    FastAPI Backend                           │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Routers    │  │  Services   │  │     Scheduler       │  │
│  │ - dashboard │  │ - ftl_db    │  │ (timed block expiry)│  │
│  │ - devices   │  │ - gravity_db│  └─────────────────────┘  │
│  │ - domains   │  │ - device_db │                           │
│  │ - logs      │  │ - pihole.py │                           │
│  │ - blocking  │  └──────┬──────┘                           │
│  └─────────────┘         │                                  │
└──────────────────────────┼──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ pihole-FTL.db │  │  gravity.db   │  │  pihole CLI   │
│  (read-only)  │  │  (read-only)  │  │   (writes)    │
│               │  │               │  │               │
│ - queries     │  │ - domainlist  │  │ - pihole -b   │
│ - network     │  │ - adlist      │  │ - pihole -w   │
│ - clients     │  │               │  │ - pihole --wild│
└───────────────┘  └───────────────┘  └───────────────┘
```

**Data flow:**
- **Reads**: Query Pi-hole's SQLite databases directly (read-only mode)
- **Writes**: Use `pihole` CLI commands to modify blocklists (ensures cache is updated)
- **App state**: Separate `dashboard.db` for device nicknames and timed block tracking

## Project Structure

```
pihole-dashboard/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, static mount
│   │   ├── config.py            # Settings (env vars, paths)
│   │   ├── models.py            # Pydantic models, domain presets
│   │   ├── routers/
│   │   │   ├── dashboard.py     # GET /api/stats/*
│   │   │   ├── devices.py       # GET/PATCH /api/devices
│   │   │   ├── domains.py       # CRUD /api/domains
│   │   │   ├── logs.py          # GET /api/logs
│   │   │   └── blocking.py      # /api/timed-blocks
│   │   └── services/
│   │       ├── ftl_db.py        # pihole-FTL.db queries (cached)
│   │       ├── gravity_db.py    # gravity.db queries
│   │       ├── device_db.py     # App DB for nicknames
│   │       ├── pihole.py        # CLI wrapper (async subprocess)
│   │       └── scheduler.py     # Timed block expiry loop
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue              # Main layout, navigation
│   │   ├── main.js              # Vue app entry
│   │   ├── router/index.js      # Vue Router config
│   │   ├── api/client.js        # Fetch wrapper
│   │   ├── views/               # Page components
│   │   │   ├── Dashboard.vue
│   │   │   ├── Devices.vue
│   │   │   ├── DeviceDetail.vue
│   │   │   ├── Domains.vue
│   │   │   ├── TimedBlocking.vue
│   │   │   └── Logs.vue
│   │   └── components/          # Reusable components
│   │       ├── StatsCard.vue
│   │       ├── TimeChart.vue
│   │       ├── BlockedVsAllowedChart.vue
│   │       ├── HourlyHeatmap.vue
│   │       ├── QueryTable.vue
│   │       ├── DeviceCard.vue
│   │       ├── DomainList.vue
│   │       ├── AddDomainForm.vue
│   │       └── TimerCard.vue
│   ├── package.json
│   └── vite.config.js
├── deploy.sh                    # Build + deploy to Pi
├── pihole-dashboard.service     # systemd unit file
└── README.md
```

## Requirements

**Raspberry Pi (server):**
- Pi-hole v5.x installed and running
- Python 3.9+
- User with sudo access to run `pihole` commands

**Development machine:**
- Node.js 18+
- npm

## Installation

### Quick Deploy (from your Mac/PC to Pi)

1. Clone the repo:
   ```bash
   git clone https://github.com/ghong25/pihole-dashboard.git
   cd pihole-dashboard
   ```

2. Edit `deploy.sh` to set your Pi's address:
   ```bash
   PI_HOST="your-user@your-pi-ip"
   ```

3. Ensure SSH key auth is set up:
   ```bash
   ssh-copy-id your-user@your-pi-ip
   ```

4. Run the deploy script:
   ```bash
   ./deploy.sh
   ```

5. Access the dashboard at `http://your-pi-ip:8080`

### Manual Installation (on the Pi)

1. Clone to the Pi:
   ```bash
   git clone https://github.com/ghong25/pihole-dashboard.git
   cd pihole-dashboard
   ```

2. Set up the backend:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Build the frontend (requires Node.js):
   ```bash
   cd ../frontend
   npm install
   npm run build
   ```

4. Install the systemd service:
   ```bash
   sudo cp pihole-dashboard.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable pihole-dashboard
   sudo systemctl start pihole-dashboard
   ```

## Configuration

Environment variables (prefix: `PIHOLE_DASH_`):

| Variable | Default | Description |
|----------|---------|-------------|
| `PIHOLE_DASH_FTL_DB_PATH` | `/etc/pihole/pihole-FTL.db` | Path to FTL database |
| `PIHOLE_DASH_GRAVITY_DB_PATH` | `/etc/pihole/gravity.db` | Path to gravity database |
| `PIHOLE_DASH_PORT` | `8080` | Server port |
| `PIHOLE_DASH_USE_SUDO` | `true` | Use sudo for pihole commands |

Set these in the systemd service file or export them before running.

## Development

**Backend** (runs on Pi or locally with DB access):
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

**Frontend** (runs anywhere, proxies API to backend):
```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` requests to `localhost:8080`.

## API Endpoints

### Dashboard
- `GET /api/stats/summary?hours=24` — Query totals and percentages
- `GET /api/stats/top-domains?limit=10&hours=24` — Top queried domains
- `GET /api/stats/top-blocked?limit=10&hours=24` — Top blocked domains
- `GET /api/stats/over-time?hours=24` — Time series (10-min buckets)
- `GET /api/stats/hourly-pattern?days=7` — Hourly heatmap data

### Devices
- `GET /api/devices` — All network devices
- `PATCH /api/devices/{mac}` — Update nickname/icon
- `GET /api/devices/{mac}/stats` — Device query stats
- `GET /api/devices/{mac}/activity` — Device time series
- `GET /api/devices/{mac}/top-domains` — Device top domains
- `GET /api/devices/{mac}/top-blocked` — Device top blocked

### Domains
- `GET /api/domains?type=blacklist` — List domains
- `POST /api/domains` — Add domain `{domain, type, comment}`
- `DELETE /api/domains/{id}` — Remove domain
- `PATCH /api/domains/{id}` — Toggle enabled `{enabled}`
- `GET /api/domains/presets` — Get preset groups

### Timed Blocking
- `GET /api/timed-blocks` — Active timed blocks
- `POST /api/timed-blocks` — Create `{domains[], duration_minutes}`
- `DELETE /api/timed-blocks/{id}` — Cancel early

### Logs
- `GET /api/logs?page=1&per_page=50&status=&client=&from=&to=` — Query logs
- `GET /api/logs/search?q=reddit` — Search domains

## Tech Stack

**Backend:**
- [FastAPI](https://fastapi.tiangolo.com/) — Async Python web framework
- [aiosqlite](https://github.com/omnilib/aiosqlite) — Async SQLite
- [Pydantic](https://docs.pydantic.dev/) — Data validation
- [uvicorn](https://www.uvicorn.org/) — ASGI server

**Frontend:**
- [Vue 3](https://vuejs.org/) — Reactive UI framework
- [Vue Router](https://router.vuejs.org/) — Client-side routing
- [Chart.js](https://www.chartjs.org/) + [vue-chartjs](https://vue-chartjs.org/) — Charts
- [Tailwind CSS](https://tailwindcss.com/) (via CDN) — Styling
- [Vite](https://vitejs.dev/) — Build tool

## License

MIT
