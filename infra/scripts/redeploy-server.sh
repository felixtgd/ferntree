#!/bin/bash

source s3.env

tofu -chdir=infra/main init
tofu -chdir=infra/main apply -replace=module.server[\"dev-server-felix\"].hcloud_server.server

SERVER_IP=$(
    tofu -chdir=infra/main show -json |
    jq -r '.values.root_module.child_modules[] |
        select(.address == "module.server[\"dev-server-felix\"]") |
        .resources[] |
        select(.address == "module.server[\"dev-server-felix\"].hcloud_primary_ip.primary_ip") |
        .values.ip_address'
    )
echo "Server IP: $SERVER_IP"
ssh-keygen -R "[$SERVER_IP]:2222"

# sleep 10
# ssh -v tyche-server-root

# check cloud-init status
# sudo cloud-init schema --system --annotate
# cloud-init status --long
