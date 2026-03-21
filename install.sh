#!/usr/bin/env bash
# install.sh — Midlothian Bin Collection HA Integration
#
# Run this from the Home Assistant Terminal add-on:
#   curl -fsSL https://raw.githubusercontent.com/ijcarson1/gearedapp-ai-os/claude/bin-collection-reminder-yxEn8/ha-midlothian-bin-collection/install.sh | bash

set -e

BASE_URL="https://raw.githubusercontent.com/ijcarson1/gearedapp-ai-os/claude/bin-collection-reminder-yxEn8/ha-midlothian-bin-collection"
DEST="/config/custom_components/midlothian_bins"

echo "Installing Midlothian Bin Collection integration..."
mkdir -p "$DEST"

for file in __init__.py sensor.py config_flow.py const.py manifest.json strings.json; do
  echo "  Downloading $file"
  curl -fsSL "$BASE_URL/custom_components/midlothian_bins/$file" -o "$DEST/$file"
done

echo ""
echo "Done! Files installed to $DEST"
echo ""
echo "Next steps:"
echo "  1. Restart Home Assistant (Settings → System → Restart)"
echo "  2. Add integration: Settings → Devices & Services → + Add Integration → 'Midlothian Bin Collection'"
echo "  3. Enter your postcode when prompted"
