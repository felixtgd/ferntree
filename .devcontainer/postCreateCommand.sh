#!/bin/bash
set -euo pipefail

# git pull for automatic intraday updates
git pull origin $(git branch --show-current)

# GitHub CLI extensions ISSUE
# gh extension install https://github.com/nektos/gh-act
# gh extension install github/gh-copilot

# Pre-commit hooks
pip install pre-commit
pre-commit install
