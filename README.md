# _Sharly Chess Cloud_

_Sharly Chess - © Sharly Chess project 2013-2025_

## Cloud / VPS deployment

This fork adds support for running Sharly Chess on a VPS behind a reverse proxy (Traefik, nginx, etc.) so the admin can log in from anywhere and players can access public screens via a subdomain.

### What was changed

- **`CLOUD_MODE` env var** - disables the localhost admin bypass (which auto-grants admin to `127.0.0.1` requests) and enables secure session cookies.
- **Global admin password** - set `ADMIN_PASSWORD` in your environment; the hash is stored in the config database on every startup. Log in at `/admin-login`.
- **`src/server_cloud.py`** - headless server entrypoint that skips the Toga GUI import so the app starts on systems without a display (Docker, VPS).
- **`Dockerfile` + `docker-compose.yml`** - container setup pre-configured for Traefik with Let's Encrypt TLS.
- **Proxy headers** - Uvicorn is configured to trust `X-Forwarded-For` from the reverse proxy so real client IPs are logged correctly.

### Quick start (local test)

```bash
CLOUD_MODE=true ADMIN_PASSWORD=yourpassword python src/server_cloud.py --port 8080
```

Open [http://127.0.0.1:8080](http://127.0.0.1:8080), click **Admin login** in the sidebar (or go to `/admin-login`), and enter your password.

### Docker + Traefik deployment

**1. Configure `.env`**

```bash
cp .env.example .env
# Edit .env:
#   CLOUD_MODE=true
#   ADMIN_PASSWORD=<strong password>
```

**2. Adjust `docker-compose.yml`**

Edit the two Traefik labels to match your setup:

```yaml
- "traefik.http.routers.sharly-chess.rule=Host(`chess.example.com`)"   # your subdomain
- "traefik.http.routers.sharly-chess.tls.certresolver=letsencrypt"     # your resolver name
```

Also verify the `networks.traefik-public` name matches the external network your Traefik instance uses.

**3. Build and run**

```bash
docker compose build
docker compose up -d
```

**4. First login**

Navigate to `https://chess.example.com/admin-login` and enter your `ADMIN_PASSWORD`. You will have full admin access to create events, manage settings, and invite arbiters.

### How authentication works

| Situation | Access granted |
|-----------|---------------|
| `CLOUD_MODE=false`, request from `127.0.0.1` | Admin (original localhost bypass) |
| `CLOUD_MODE=true`, valid `ADMIN_PASSWORD` entered at `/admin-login` | Admin (all events) |
| `CLOUD_MODE=true`, valid per-event account + password | That event's access level |
| Everything else | Anonymous (public screens only) |

Per-event accounts (arbiters, result-entry operators, etc.) are unaffected. They continue to log in through the **Profile** button inside each event.

### Data persistence

Event databases and temporary files are stored in Docker named volumes (`sharly-chess-events`, `sharly-chess-tmp`). They survive container restarts and rebuilds. To back up, copy the volume data or use `docker cp`.

---

## CSV player import improvements

The player import (`Players → Import from file`) accepts CSVs exported from federation websites and other sources with minimal manual cleanup required.

### What is handled automatically

- **Encoding detection** - UTF-8, UTF-8 BOM, and other encodings are detected via `chardet`; BOM is stripped transparently.
- **Delimiter sniffing** - semicolon, tab, and comma delimiters are detected automatically; falls back to standard comma if sniffing fails.
- **Preamble rows** - leading single-column metadata rows (e.g. "Export date: 2024-01-01") before the actual table are skipped.
- **Header normalisation** - column names are lowercased and converted to `snake_case`.
- **Column aliases**
  - Any column whose name contains `rating` (e.g. `Elo Rating`, `FIDE Rating`, `national_rating`) is mapped to `rating`.
  - `Email` / `email` is mapped to `mail`.
- **Rating value cleaning** - values like `"1 850"`, `"Elo: 2034 (nat)"`, or `"2 034 (national)"` are reduced to a bare integer.
- **Ignored columns** - columns that Sharly Chess has no field for are dropped silently:
  - `registration_date`, `date_of_registration`, `registered`, `signup_date`, and any column whose name contains `registr`.

### Running unit tests

Unit tests do not require a running server or Playwright browsers:

```bash
python3 -m pytest tests/unit/ -v
```

---

## User documentation

**Please visit [sharly-chess.com](https://sharly-chess.com)** (installation guide [here](https://sharly-chess.com/installation)).

## Developer documentation

### Contributing

- [Contributing guide](docs/contributing/contributing-guide.md)
- [Translation guide](docs/contributing/translation-guide.md)
- [Internationalization](docs/contributing/i18n.md)
- [Maintainers, contributors and translators](/docs/contributing/contributors.md)
- [Copyright](https://sharly-chess.com/copyright)
- [License](https://sharly-chess.com/license)

### Technical appendices

- [Roadmap](https://discord.gg/gE4Y7DVxdY) (on Discord)
- [Files and folders](docs/technical-appendices/files.md)
- [Interfacing _Sharly Chess_ with _ChessEvent_](docs/technical-appendices/chessevent-interfacing.md)
- [Setting up a development environment](docs/technical-appendices/dev-setup.md)
- [Description of the databases](docs/technical-appendices/databases.md)
- [Network](docs/technical-appendices/network.md)
- [FIDE endorsement](docs/technical-appendices/fide-endorsement.md)

### Sandbox

- [Communication to players](docs/sandbox/communication-to-players.md)
- [Pairing actions](docs/sandbox/pairing-actions.md)
