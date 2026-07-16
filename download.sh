#!/usr/bin/env bash
set -eu

REPO="CropModelingPlatform/AgriscaleContainer"
TAG="v1.2.4"
API_URL="https://api.github.com/repos/${REPO}/releases/tags/${TAG}"

# Prefer jq if available; otherwise use a text fallback.
if command -v jq >/dev/null 2>&1; then
  download_url="$(
    curl -fsSL "$API_URL" \
      | jq -r '.assets[] | select(.name | (contains("datamill") and contains(".sif"))) | .browser_download_url' \
      | head -n 1
  )"
else
  echo "jq not found, using fallback parser..."
  download_url="$(
    curl -fsSL "$API_URL" \
      | grep -oE '"browser_download_url":\s*"[^"]+"' \
      | cut -d '"' -f 4 \
      | grep -E 'datamill.*\.sif$' \
      | head -n 1
  )"
fi

if [[ -z "$download_url" ]]; then
  echo "No matching asset found for tag ${TAG}."
  exit 1
fi

echo "Downloading: $download_url"
curl -fL -O "$download_url"
echo "Done."
