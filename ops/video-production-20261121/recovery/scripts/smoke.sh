#!/bin/sh
# Short layout smoke. The mp4 files are composites on the low-bitrate reference
# plate. They are not a recovered master and they do not replace final_v1.mp4.
set -eu
cd "$(dirname "$0")/.."
python3 -m recovery_us3day validate
python3 -m recovery_us3day gaps --md --out GAPS.md
python3 -m recovery_us3day smoke \
  --reference inputs/reference/master_full_lowbitrate_REFERENCE_NOT_RERENDER.mp4 \
  --ass inputs/source-docs/final_v1.ass \
  --cover inputs/reference/cover_1080x1920.jpg \
  --allow-reference-plate \
  --out out/smoke
echo "smoke exit is not acceptance; 3 means Noto is missing, 2 means a reference diagnostic was written and is not qualified"
