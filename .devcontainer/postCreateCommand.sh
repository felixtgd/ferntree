#!/bin/bash
set -euo pipefail

# git pull for automatic intraday updates
git pull origin $(git branch --show-current)

# Configure git user information
git config --global user.email "felix.tangerding@pm.me"
git config --global user.name "felixtgd"

# Install dependencies and update packages
uv --project backend sync --active
pre-commit install
