#!/usr/bin/env bash
set -euo pipefail

python -m PyInstaller --noconfirm eve_explore_helper_app.spec

echo "Build complete. Output executable is under dist/EVE-Explore-Helper/ (or dist/ on onefile setups)."
echo "settings.json and visited.json are external runtime files and will be created beside the executable."
