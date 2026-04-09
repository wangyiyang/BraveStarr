#!/bin/bash
set -euo pipefail

cd /Users/wangyiyang/Documents/Github/BraveStarr
exec uv run brave-starr --transport http --host 0.0.0.0 --port 8000
