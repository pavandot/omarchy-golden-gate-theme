#!/usr/bin/env bash
# Enable Golden Gate's Liquid Glass look (blur, shadows, hairline borders, rounding).
set -euo pipefail

src="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/golden-gate-glass.lua"
dest="$HOME/.config/hypr/golden-gate-glass.lua"
conf="$HOME/.config/hypr/hyprland.lua"
line='require("hypr.golden-gate-glass")'

cp -- "$src" "$dest"
if ! grep -qF "$line" "$conf"; then
  printf '\n-- Golden Gate theme: Liquid Glass blur, shadows, hairline borders.\n%s\n' "$line" >>"$conf"
fi

hyprctl reload >/dev/null
errors=$(hyprctl configerrors)
if [[ -n ${errors//[[:space:]]/} ]]; then
  echo "$errors" >&2
  exit 1
fi

# The Omarchy shell reads corner rounding at startup.
omarchy restart shell >/dev/null 2>&1 || true
echo "Liquid Glass enabled."
