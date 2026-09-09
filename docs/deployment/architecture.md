# Ferntree Deployment Architecture

This document records the intended production architecture and deployment process for Ferntree. It is the basis for implementing the first deployment to a Hetzner Cloud server.

## Goals

- Deploy the frontend, backend, and database to one Hetzner Cloud server.
- Use Docker Compose rather than Kubernetes.
- Serve the application securely at `https://ferntree.dev`.
- Keep only the reverse proxy publicly reachable.
- Automate deployment from the local development machine; no manual SSH sessions should be required.
- Keep production secrets out of the public Git repository.

## Application Components

Ferntree has three application tiers.

| Component | Technology | Responsibility |
| --- | --- | --- |
| Frontend | Vite SPA, TypeScript | User interface, browser-side interaction, charts, and API requests. |
| Backend | FastAPI served by uvicorn | Simulation logic, application API, and database access. |
| Database | PostgreSQL 16 | Persistent application data, initialized from `backend/schema.sql`. |

The frontend is a Vite single-page application (SPA), not a Next.js application. The Dockerfile currently contains an outdated Next.js comment and a broken production command (`npm run start` does not exist in `frontend/package.json`). The production image must be changed accordingly.

## SPA Model

Running `npm run build` in `frontend/` produces a `dist/` directory containing static assets, including:

- `index.html`
- JavaScript bundles
- CSS bundles
- static images and other assets

The output does not contain a separate server-rendered HTML document for each application screen and does not contain simulation results. A browser initially downloads the static application shell, then its JavaScript renders screens and reacts to user interaction.

Dynamic simulation data follows a separate request flow:

1. A user loads `https://ferntree.dev` and receives the static SPA files.
2. The SPA JavaScript runs in that user's browser.
3. The user triggers a simulation or requests existing data.
4. The browser sends a request to `/api/...`.
5. The backend executes the relevant FastAPI handler, accesses PostgreSQL as needed, and returns JSON.
6. The SPA receives the JSON and renders results, including charts, in the browser.

The static SPA server does not directly communicate with FastAPI or PostgreSQL. The browser makes separate requests for static application files and API data.

## Production Architecture

The production stack will use three Docker Compose services:

- `caddy`: public web tier. It serves the SPA static files, terminates HTTPS, and proxies API requests.
- `backend`: private FastAPI/uvicorn service.
- `postgres`: private PostgreSQL service with a persistent Docker named volume.

```text
Internet
  |
  | HTTPS :443
  v
Caddy
  |-- /api/* --> backend (uvicorn :8000) --> postgres (:5432)
  `-- /*      --> static SPA files in /srv
```

### Caddy

Caddy is both the public reverse proxy and static file server.

Its responsibilities are:

- Listen on public ports 80 and 443.
- Obtain and renew TLS certificates from Let's Encrypt for `ferntree.dev` automatically.
- Redirect HTTP traffic to HTTPS.
- Route requests beginning with `/api/` to `backend:8000`.
- Serve the Vite `dist/` output for all other paths.
- Fall back to `index.html` for unknown frontend paths, allowing browser-side SPA routing to work after page refreshes or direct navigation.

The frontend build output will be copied into `/srv` in the final Caddy image. This creates one immutable public web image that contains both Caddy and the built SPA.

### Why Caddy Only, Rather Than Caddy Plus nginx

An earlier option included a separate nginx container that would only serve the static SPA, while Caddy would terminate TLS and route traffic to nginx or FastAPI. This would work, but was intentionally rejected.

nginx can provide highly customized static caching, rewrites, and standalone frontend-image portability. Ferntree does not currently need those capabilities. Caddy already provides sufficient static file serving, compression, SPA fallbacks, HTTPS automation, and reverse-proxy functionality.

Using Caddy only avoids an extra container and an extra configuration file. nginx can be introduced later if actual static-serving requirements justify it.

## Networking and Public Exposure

Docker Compose creates a private Docker network. Services resolve each other by Compose service name, for example `backend` and `postgres`.

| Service | Container port | Published to host | Intended reachability |
| --- | --- | --- | --- |
| `caddy` | 80, 443 | Yes: `80:80`, `443:443` | Public internet |
| `backend` | 8000 | No | Caddy over the Docker network |
| `postgres` | 5432 | No | Backend over the Docker network |

Only Caddy will use Compose `ports:` mappings. Omitting a port mapping does not prevent a service from being reachable by other containers; it prevents host and internet access.

At the server level, Hetzner Cloud Firewall and UFW will permit:

- TCP 2222 for SSH, restricted to the administrator's allowed IPs.
- TCP 80 for public HTTP and Let's Encrypt validation.
- TCP 443 for public HTTPS.

Port 443 must be changed from its current IP-restricted configuration to `0.0.0.0/0`. PostgreSQL and uvicorn will not be exposed publicly, and should have no host port mappings.

### Request Flows

Static application request:

```text
Browser -- HTTPS :443 --> Caddy -- HTTP over Docker network --> static files in Caddy image
```

API request:

```text
Browser -- HTTPS /api/... --> Caddy --> backend:8000 --> postgres:5432
                                                <-- JSON response --
```

Serving the SPA and API through the same domain creates a single origin. The production frontend will use `VITE_BACKEND_BASE_URI=/api`, so browser API requests target the same site that delivered the SPA. This avoids needing cross-origin browser requests. The backend's current permissive CORS configuration can be tightened later, but CORS is not required for this same-origin design.

## Secrets and Environment Configuration

The repository is public. Production secrets must not be committed.

The backend requires `DATABASE_URL`; it is read directly from the environment in `backend/src/db/config.py`. The only confidential value currently required for production is the PostgreSQL password embedded within that URL.

`FRONTEND_BASE_URI` in the existing backend `.env` is not read by the code and will not be used in the production configuration.

On the server, the application directory will contain a gitignored root `.env` file next to `compose.prod.yml`. Docker Compose loads this file automatically. It will contain values equivalent to:

```dotenv
POSTGRES_PASSWORD=<random-server-generated-password>
DATABASE_URL=postgresql://ferntree:<same-password>@postgres:5432/ferntree_db
```

The exact password must not be printed by deployment scripts or sent from the local machine. It will be generated on the server using a cryptographically secure command such as `openssl rand -hex 24`.

### Password Lifecycle

The password policy is generate-if-absent, reuse-otherwise:

- On a new server, no root `.env` exists. The deployment script creates it and generates a fresh random password.
- On a normal application redeploy, the `.env` already exists. The script leaves it unchanged, preserving compatibility with the existing PostgreSQL data volume.
- On an OpenTofu server replacement, both the server disk and Docker volumes disappear. A new `.env` and a matching fresh database are created automatically.

PostgreSQL only applies `POSTGRES_PASSWORD` when its data directory is initialized. Replacing the password while retaining the database volume would make the backend unable to authenticate, which is why unconditional password regeneration is not allowed.

## Deployment Pipeline

Provisioning is already managed by OpenTofu in `infra/`. The server is a Hetzner Cloud Debian 12 `cpx12` instance provisioned with Docker, Docker Compose, cloud-init hardening, and an `admin` user authenticated by SSH key on port 2222.

Application deployment will run entirely from the local development machine using SSH as `admin` on port 2222. The public repository can be cloned directly by the server; no container registry or GitHub Actions workflow is needed initially.

The standard application deployment pipeline is:

1. Resolve the Hetzner server primary IP from OpenTofu state using `tofu show -json` and `jq`.
2. Wait until SSH is reachable at `admin@<server-ip>:2222`. This accommodates cloud-init after a fresh server deployment.
3. Create `~/ferntree/.env` on the server only when it does not exist. Generate the database password on the server and write `POSTGRES_PASSWORD` plus its matching `DATABASE_URL`.
4. Clone the public repository to `~/ferntree` if it is absent; otherwise pull the latest committed branch.
5. Run `docker compose -f compose.prod.yml up -d --build` from `~/ferntree`.
6. Docker builds the Vite/Caddy image and FastAPI image on the server, starts or updates containers, and retains named volumes.

The server is small but sufficient for this initial application. If image builds become slow or resource-intensive later, the architecture can evolve to build in CI and pull images from a registry such as GHCR.

### OpenTofu Server Redeploy Integration

`infra/scripts/redeploy-server.sh` currently replaces the server and removes its stale SSH host-key entry. It will be extended to invoke the application deployment script after replacement.

This makes the complete fresh-server process:

```text
tofu apply -replace server
  -> obtain new server IP
  -> clear old known-host key
  -> wait for cloud-init and SSH
  -> generate server-local secret file
  -> clone repository
  -> build and start the Compose stack
```

PostgreSQL data is intentionally lost when the server is replaced because its Docker named volume is local to that server. Persistence across server replacement is not part of this first deployment architecture. It would later require a backup/restore flow, Hetzner volume, managed database, or another external data store.

## Detailed Implementation Plan

### 1. Update the firewall

Edit `infra/main/firewall.tf`:

- Change the TCP 443 rule from `local.allowed_ips` to `["0.0.0.0/0"]`.
- Keep TCP 80 public; it is required for HTTP-to-HTTPS handling and Let's Encrypt HTTP validation.
- Apply the resulting OpenTofu change before attempting public HTTPS deployment.

### 2. Correct the production frontend image

Edit `Dockerfile`:

- Retain development frontend stages as appropriate.
- Replace the invalid `frontend-prod` command (`npm run start`) with a multi-stage image.
- Build the Vite SPA with `npm ci` and `npm run build`.
- Accept a `VITE_BACKEND_BASE_URI` build argument with production value `/api`.
- Use `caddy:2-alpine` as the final `frontend-prod` stage.
- Copy Vite `dist/` into `/srv` in that final image.
- Leave the existing `backend-prod` uvicorn stage in place unless small production fixes are needed.

### 3. Add the Caddy configuration

Create `Caddyfile` at repository root. It must:

- Define `ferntree.dev` as the site address.
- Enable response compression.
- Handle `/api/*` before static-file handling and proxy it to `backend:8000`.
- Set the static root to `/srv`.
- Use a SPA fallback equivalent to `try_files {path} /index.html`.
- Serve files from the static root.

### 4. Add production Compose configuration

Create `compose.prod.yml` at repository root with three services:

- `caddy`: build `frontend-prod`; publish ports 80 and 443; mount `Caddyfile` read-only; use persistent named volumes for `/data` and `/config`; set `restart: unless-stopped`.
- `backend`: build `backend-prod`; receive `DATABASE_URL` from the root Compose environment; do not publish port 8000; wait for PostgreSQL health; set `restart: unless-stopped`.
- `postgres`: use `postgres:16`; receive `POSTGRES_PASSWORD` from the root Compose environment; retain its named data volume and schema initialization mount; do not publish port 5432; retain a healthcheck; set `restart: unless-stopped`.

The Compose file must not contain actual credentials. The Caddy storage volumes are required so certificates and account state persist across container recreation, avoiding unnecessary Let's Encrypt requests and rate-limit risk.

### 5. Add automated application deployment script

Create `infra/scripts/deploy-app.sh`:

- Run from the repository root or calculate paths robustly from the script location.
- Resolve the server IP from OpenTofu state, following the existing pattern in `infra/scripts/redeploy-server.sh`.
- Use SSH as `admin` on port 2222 with the configured Hetzner SSH key.
- Wait/retry until SSH is available.
- Execute a server-side idempotent bootstrap:
  - Clone the public repository if `~/ferntree` does not exist, otherwise pull it.
  - Create `~/ferntree/.env` only if absent.
  - Generate the random password on the server only when creating `.env`.
  - Run `docker compose -f compose.prod.yml up -d --build`.
- Avoid logging the generated password or contents of `.env`.
- Fail clearly when OpenTofu state cannot provide the server IP, SSH never becomes ready, or deployment fails.

### 6. Integrate server replacement and application deployment

Edit `infra/scripts/redeploy-server.sh`:

- Retain its existing OpenTofu replacement and stale known-host removal behavior.
- Invoke `deploy-app.sh` after the new server IP is available.
- Ensure the script fails rather than attempting deployment when the OpenTofu replacement does not succeed.

## Preconditions Before First Deployment

- Create a public DNS A record: `ferntree.dev` -> Hetzner server primary IPv4 address.
- Apply the OpenTofu firewall update that opens TCP 443 publicly.
- Ensure the local machine can authenticate using the SSH key provisioned in `infra/main/server.tf`, expected at `~/.ssh/hetzner_key` unless SSH configuration differs.
- Confirm the public repository clone URL used by the deployment script.

## Future Improvements

- Restrict FastAPI CORS from `*` to `https://ferntree.dev` if external cross-origin clients are not needed.
- Add database backup and restore procedures before PostgreSQL data becomes valuable.
- Move image building to CI and a container registry if server-side builds become slow.
- Add health checks and deployment validation to the deployment script.
- Add monitoring, log collection, alerting, and dependency/image update procedures.
