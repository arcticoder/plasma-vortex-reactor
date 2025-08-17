#!/usr/bin/env bash
# Manual helper: upload papers/phase3_stability.pdf to Zenodo using ZENODO_TOKEN
# Usage examples:
#   ZENODO_TOKEN=xxx ./scripts/publish_zenodo.sh
#   ./scripts/publish_zenodo.sh --token "$ZENODO_TOKEN" --title "Phase 3 Stability Paper" --creators "Alice Smith, Bob Jones" --publish
set -euo pipefail

progname=$(basename "$0")
usage() {
  cat <<EOF
Usage: $progname [options]

Environment:
  ZENODO_TOKEN         - API token (alternatively pass with --token)

Options:
  --token TOKEN        - Zenodo API token (overrides ZENODO_TOKEN)
  --file PATH          - PDF file to upload (default: papers/phase3_stability.pdf)
  --title STR          - Title for the deposition (default: "Phase 3 Stability Paper")
  --description STR    - Description text (default: a short repository description)
  --creators "A,B"     - Comma-separated creator names (default: git user or $USER)
  --publish            - Immediately publish the deposition (default: leave draft)
  --help               - show this help
EOF
  exit 1
}

# defaults
FILE="papers/phase3_stability.pdf"
TITLE="Phase 3 Stability Paper"
DESCRIPTION="Plasma Vortex Reactor: CI-validated Modeling with Stability KPI Gates and Dynamic Ripple Control"
CREATORS=""
PUBLISH=false
TOKEN="${ZENODO_TOKEN:-}"

# parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --token) TOKEN="$2"; shift 2;;
    --file) FILE="$2"; shift 2;;
    --title) TITLE="$2"; shift 2;;
    --description) DESCRIPTION="$2"; shift 2;;
    --creators) CREATORS="$2"; shift 2;;
    --publish) PUBLISH=true; shift;;
    -h|--help) usage;;
    *) echo "Unknown arg: $1"; usage;;
  esac
done

if [ -z "${TOKEN:-}" ]; then
  echo "Error: Zenodo token not provided. Set ZENODO_TOKEN or use --token." >&2
  exit 2
fi

if [ ! -f "$FILE" ]; then
  echo "Error: PDF not found at '$FILE'. Build it first." >&2
  exit 1
fi

# require curl and jq
if ! command -v curl >/dev/null 2>&1; then
  echo "Error: curl not found - please install curl and retry." >&2
  exit 2
fi
if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq not found - please install jq and retry." >&2
  exit 2
fi

# derive a default creator if none provided
if [ -z "$CREATORS" ]; then
  git_name=$(git config user.name || true)
  if [ -n "$git_name" ]; then
    CREATORS="$git_name"
  else
    CREATORS="${USER:-unknown}"
  fi
fi

# convert creators CSV to jq array
IFS=',' read -r -a carray <<< "$CREATORS"
creators_json=$(printf '%s\n' "${carray[@]}" | jq -R -s -c 'split("\n")[:-1] | map({name: .})')

meta=$(jq -n \
  --arg title "$TITLE" \
  --arg desc "$DESCRIPTION" \
  --argjson creators "$creators_json" \
  '{metadata: {title: $title, upload_type: "publication", publication_type: "article", description: $desc, creators: $creators}}')

echo "Creating deposition (draft)..."
dep=$(curl -sSf -H "Authorization: Bearer ${TOKEN}" -H "Content-Type: application/json" -d "$meta" "https://zenodo.org/api/deposit/depositions")
id=$(echo "$dep" | jq -r .id)
if [ -z "$id" ] || [ "$id" = "null" ]; then
  echo "Error: failed to create deposition (response: $dep)" >&2
  exit 3
fi
echo "Created deposition id: $id"

echo "Uploading file: $FILE"
upload_resp=$(curl -sSf -H "Authorization: Bearer ${TOKEN}" -F "file=@${FILE}" "https://zenodo.org/api/deposit/depositions/${id}/files" || true)
if [ -z "$upload_resp" ]; then
  echo "Warning: upload returned empty response (check network / token)";
else
  echo "Upload response: $(echo "$upload_resp" | jq -c '. | {status: (if .file_name then "ok" else "unknown" end), id: (.id // null)}')"
fi

if [ "$PUBLISH" = true ]; then
  echo "Publishing deposition ${id}..."
  pub_resp=$(curl -sSf -X POST -H "Authorization: Bearer ${TOKEN}" "https://zenodo.org/api/deposit/depositions/${id}/actions/publish" || true)
  if [ -n "$pub_resp" ]; then
    echo "Publish response: $pub_resp"
  else
    echo "Publish request returned empty response; check permissions/token."
  fi
  echo "Done. Deposition ${id} should be published (check Zenodo)."
else
  echo "Done. Deposition ${id} created in draft state. Use Zenodo web UI to review and publish, or re-run with --publish."
fi
