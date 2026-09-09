#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd -- "$SCRIPT_DIR/../.." && pwd)
ENV_FILE="$REPO_ROOT/.env"

if [[ ! -f "$ENV_FILE" ]]; then
    printf 'Missing local credentials file: %s\n' "$ENV_FILE" >&2
    exit 1
fi

source "$ENV_FILE"

tofu -chdir="$REPO_ROOT/infra/main" init
tofu -chdir="$REPO_ROOT/infra/main" apply -auto-approve -replace=module.server[\"dev-server-felix\"].hcloud_server.server

SERVER_IP=$(
    tofu -chdir="$REPO_ROOT/infra/main" show -json |
    jq -r '.values.root_module.child_modules[] |
        select(.address == "module.server[\"dev-server-felix\"]") |
        .resources[] |
        select(.address == "module.server[\"dev-server-felix\"].hcloud_primary_ip.primary_ip") |
        .values.ip_address'
    )
echo "Server IP: $SERVER_IP"
ssh-keygen -R "[$SERVER_IP]:2222"

"$REPO_ROOT/infra/scripts/deploy-app.sh"
