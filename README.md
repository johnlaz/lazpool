# LAZPOOL

**A dark luxury PWA dashboard for Jandy AquaLink RS pool systems.**

Built for the AquaLink RS-4 Combo (REV T.2) with AqualinkD as the local backend. Runs entirely on your local network — no cloud, no subscriptions.

---

## Features

- Circuit control (pool pump, spa, lights, cleaner, waterfall, aux 1–8, and more)
- Variable speed pump slider with presets
- Heater setpoint control
- Spa mode toggle
- Water chemistry display (SWG %, pH, ORP)
- Sonos music control via Home Assistant REST API
- Fully configurable — no hardcoded values
- Export / Import config as JSON (portable across devices)
- Installable PWA — works offline, adds to home screen

---


## Hosting Options

LAZPOOL has three access modes, selectable in Settings → Access & Hosting:

**🏠 Local Serve (default — recommended)**  
Serve from the same machine as HA. No CORS issues.
```bash
python3 -m http.server 3000 --directory lazpool
```
Then access at `http://10.0.0.51:3000` (use your HA machine's IP).

**🐙 GitHub Pages**  
Host publicly on GitHub. Requires adding your Pages URL to HA's CORS config:
```yaml
# configuration.yaml
http:
  cors_allowed_origins:
    - https://yourusername.github.io
```

**🌐 HA CORS Allowed**  
You've already configured CORS in HA — all external origins work.

## Setup

### 1. Hardware needed
- USB to RS485 adapter (~$12 on Amazon, FTDI chip recommended)
- 2 wires from your AquaLink panel's RS485 terminals to the adapter
- A PC/mini-PC/Raspberry Pi on your home network

### 2. Install AqualinkD
See [AqualinkD on GitHub](https://github.com/aqualinkd/AqualinkD).  
Default port: `8080`. The app expects endpoints at `http://[your-ip]:8080/api/`.

### 3. Deploy this app
**Option A — GitHub Pages (recommended)**
1. Fork or upload this repo
2. Go to Settings → Pages → Source: main branch / root
3. Access at `https://[yourusername].github.io/lazpool/`

**Option B — Local**
Serve from any static file server:
```bash
npx serve .
# or
python3 -m http.server 8000
```

### 4. First-run setup
Open the app — the setup wizard will appear automatically.  
Enter:
- AqualinkD server IP + port
- Home Assistant IP, port, and Long-Lived Access Token (for Sonos)
- Pool name and panel info

All settings are saved to `localStorage` and exportable as a JSON config file.

---

## File Structure

```
lazpool/
├── index.html          ← Full app (single file, ~100KB)
├── manifest.json       ← PWA manifest
├── sw.js               ← Service worker (offline support)
├── favicon.ico
├── favicon-16.png
├── favicon-32.png
├── apple-touch-icon.png
├── icon-192.png
└── icon-512.png
```

---

## AqualinkD API Mapping

| Feature | AqualinkD endpoint |
|---|---|
| Circuit on/off | `/api/{circuit_id}/{0\|1}` |
| Status poll | `/api/status` |
| Heater setpoint | `/api/pool_heat_sp/{temp}` |
| Pump RPM | `/api/pump_speed/{rpm}` |

---

## Sonos via Home Assistant

The Music panel calls the HA REST API directly:
- `POST /api/services/media_player/media_play`
- `POST /api/services/media_player/media_pause`
- `POST /api/services/media_player/play_media`
- `POST /api/services/media_player/volume_set`

Generate a Long-Lived Access Token in HA → Profile → Security.

---

## Version History

| Version | Changes |
|---|---|
| v1.3 | Access mode selector (Local/GitHub/CORS), version bump |
| v1.2 | Settings system, setup wizard, Music Assistant auto-discovery, export/import, PWA |
| v1.1 | Circuit registry, pin/hide/rename/reorder, hidden drawer |
| v1.0 | Initial release |

---

*LAZPOOL is not affiliated with Jandy, Zodiac, or Sonos.*
