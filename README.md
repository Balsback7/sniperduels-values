# sniperduels-values

Every Sniper Duels weapon and its gem value, as a config.

Source: `GET https://sniperduels.org/api/v1/items` (public, no auth).
Auto-refreshed by GitHub Actions every 6 hours — see `.github/workflows/update.yml`.

## Files

| file | what |
|---|---|
| `values.json` | full config: every weapon, gem value, per-condition values (Mint / Standard / WellWorn) |
| `gem_prices.json` | flat map `code -> gem value`, for quick lookups |
| `values.lua` | same config as a Lua module, `loadstring`-able |
| `fetch_values.py` | regenerates all three (stdlib only) |

## Entry schema

```json
"AWP_ArcticRecon": {
  "name": "Arctic Recon",
  "type": "Sniper",            // Sniper | Knife | Misc
  "weapon": "AWP",             // weapon platform
  "rarity": "Classified",
  "value": 900,                // base gem value
  "currency": "gems",          // or "robux"
  "robux": null,               // robux value when currency is robux
  "demand": "Medium",          // None | Low | Medium | High...
  "status": "Active",          // market status
  "conditions": {              // per-condition gem values (when the item has them)
    "MintCondition": 670,
    "StandardIssue": 500,
    "WellWorn": 400
  }
}
```

## Usage

Lua (executor, raw GitHub):

```lua
local values = loadstring(game:HttpGet("https://raw.githubusercontent.com/<you>/sniperduels-values/main/values.lua"))()
print(values.AWP_ArcticRecon.value)                      --> 900
print(values.AWP_ArcticRecon.conditions.MintCondition)   --> 670
```

Shell one-liner:

```bash
curl -s https://sniperduels.org/api/v1/items | jq -r '.[] | select(.value) | "\(.value)\t\(.code)"'
```

## Refresh manually

```bash
python3 fetch_values.py
```
