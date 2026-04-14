#!/bin/bash
set -euo pipefail

# git pull for automatic intraday updates
git pull origin $(git branch --show-current)

# Pre-commit hooks
pip install pre-commit
pre-commit install
