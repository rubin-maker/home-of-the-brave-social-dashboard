#!/bin/bash
# One-command rebuild. Override the interpreter with PYTHON=/path/to/python.
set -e
cd "$(dirname "$0")"
PYTHON_BIN="${PYTHON:-python3}"

if ! "$PYTHON_BIN" -c "import openpyxl" >/dev/null 2>&1; then
  echo "Missing dependency: openpyxl"
  echo "Run: $PYTHON_BIN -m pip install -r requirements.txt"
  exit 1
fi

echo "==> 1/3  Normalize four HOTB workbooks"
"$PYTHON_BIN" scripts/analyze.py
echo "==> 2/3  Build self-contained dashboard.html"
"$PYTHON_BIN" scripts/build_dashboard.py
echo "==> 3/3  Build printable summary.pdf (when reportlab is installed)"
"$PYTHON_BIN" scripts/build_pdf.py
echo "Done. Open dashboard.html in a browser."
