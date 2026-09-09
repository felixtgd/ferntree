#!/bin/bash
set -euo pipefail

# git pull for automatic intraday updates
git pull origin $(git branch --show-current)

# Install dependencies and update packages
cd backend && uv sync
pre-commit install
