#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd -- "$SCRIPT_DIR/../.." && pwd)
ENV_FILE="$REPO_ROOT/.env"
SSH_KEY="$HOME/.ssh/hetzner_key"
SSH_PORT=2222
SSH_USER=admin
DEPLOY_BRANCH=develop
REPOSITORY_URL=https://github.com/felixtgd/ferntree.git
SSH_RETRIES=60
SSH_RETRY_DELAY=5

if [[ ! -f "$ENV_FILE" ]]; then
    printf 'Missing local credentials file: %s\n' "$ENV_FILE" >&2
    exit 1
fi

if [[ ! -f "$SSH_KEY" ]]; then
    printf 'Missing SSH key: %s\n' "$SSH_KEY" >&2
    exit 1
fi

cleanup_ssh_agent() {
    ssh-agent -k >/dev/null
}

eval "$(ssh-agent -s)" >/dev/null
trap cleanup_ssh_agent EXIT

printf 'Enter the passphrase for %s:\n' "$SSH_KEY"
ssh-add "$SSH_KEY"

source "$ENV_FILE"

SERVER_IP=$(
    tofu -chdir="$REPO_ROOT/infra/main" show -json |
        jq -r '.values.root_module.child_modules[] |
            select(.address == "module.server[\"dev-server-felix\"]") |
            .resources[] |
            select(.address == "module.server[\"dev-server-felix\"].hcloud_primary_ip.primary_ip") |
            .values.ip_address'
)

if [[ -z "$SERVER_IP" || "$SERVER_IP" == "null" ]]; then
    printf 'Unable to resolve the server IP from OpenTofu state.\n' >&2
    exit 1
fi

# Intentional TOFU for first deployment; pin the server host key before enabling unattended production deploys.
SSH_OPTIONS=(
    -i "$SSH_KEY"
    -p "$SSH_PORT"
    -o ConnectTimeout=5
    -o IdentitiesOnly=yes
    -o StrictHostKeyChecking=accept-new
)

printf 'Waiting for SSH on %s:%s...\n' "$SERVER_IP" "$SSH_PORT"
for ((attempt = 1; attempt <= SSH_RETRIES; attempt++)); do
    if ssh "${SSH_OPTIONS[@]}" "$SSH_USER@$SERVER_IP" true; then
        break
    fi

    if ((attempt == SSH_RETRIES)); then
        printf 'SSH did not become available after %s attempts.\n' "$SSH_RETRIES" >&2
        exit 1
    fi

    sleep "$SSH_RETRY_DELAY"
done

printf 'Deploying branch %s to %s...\n' "$DEPLOY_BRANCH" "$SERVER_IP"
ssh "${SSH_OPTIONS[@]}" "$SSH_USER@$SERVER_IP" \
    "REPO_DIR=\$HOME/ferntree DEPLOY_BRANCH='$DEPLOY_BRANCH' REPOSITORY_URL='$REPOSITORY_URL' bash -s" <<'REMOTE_SCRIPT'
set -euo pipefail

if [[ ! -e "$REPO_DIR" ]]; then
    git clone --branch "$DEPLOY_BRANCH" "$REPOSITORY_URL" "$REPO_DIR"
elif [[ ! -d "$REPO_DIR/.git" ]]; then
    printf 'Deployment directory exists but is not a Git repository: %s\n' "$REPO_DIR" >&2
    exit 1
fi

cd "$REPO_DIR"
git fetch origin "$DEPLOY_BRANCH"
git checkout -B "$DEPLOY_BRANCH" "origin/$DEPLOY_BRANCH"

if [[ ! -f .env ]]; then
    database_password=$(openssl rand -hex 24)
    umask 077
    {
        printf 'POSTGRES_PASSWORD=%s\n' "$database_password"
        printf 'DATABASE_URL=postgresql://ferntree:%s@postgres:5432/ferntree_db\n' "$database_password"
    } >.env
fi

if docker compose version >/dev/null 2>&1; then
    docker compose -f compose.prod.yml up -d --build
else
    docker-compose -f compose.prod.yml up -d --build
fi
REMOTE_SCRIPT

printf 'Application deployment completed.\n'
