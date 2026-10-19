#!/usr/bin/env python3
"""Fetch every Sniper Duels weapon value (gems) and write config files.

Outputs:
  values.json      full config (every weapon, gem value, per-condition values)
  gem_prices.json  flat map: weapon code -> gem value
  values.lua       the same config as a Lua module (loadstring-able)

Source: GET https://sniperduels.org/api/v1/items   (public, no auth needed)
"""

import json
import urllib.request
from datetime import datetime, timezone

API = "https://sniperduels.org/api/v1/items"
UA = "sniperduels-values/1.0"


def fetch_items():
    req = urllib.request.Request(API, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if not isinstance(data, list):
        raise SystemExit("unexpected payload: expected a list of items")
    return data


def clean(item):
    conditions = {}
    for c in item.get("conditionValues") or []:
        code = c.get("condition")
        if code and c.get("value") is not None:
            conditions[code] = c["value"]
    entry = {
        "name": item.get("name"),
        "type": item.get("type"),
        "weapon": item.get("weaponType") or None,
        "rarity": item.get("rarity"),
        "value": item.get("value"),
        "currency": item.get("valueCurrency") or "gems",
        "robux": item.get("robuxValue"),
        "demand": item.get("demandLevel"),
        "status": item.get("marketStatus"),
    }
    if conditions:
        entry["conditions"] = conditions
    return entry


def lua_str(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def lua_num(n):
    if isinstance(n, bool):
        return lua_str(str(n))
    if isinstance(n, (int, float)):
        return repr(n) if isinstance(n, float) else str(n)
    return lua_str(n)


def to_lua(cfg, generated):
    lines = [
        "-- Sniper Duels weapon gem values",
        f"-- generated: {generated}",
        "-- source: GET https://sniperduels.org/api/v1/items",
        "-- refresh: python3 fetch_values.py",
        "",
        "return {",
    ]
    for code, e in cfg.items():
        parts = [f'name = {lua_str(e["name"])}', f'type = {lua_str(e["type"])}']
        if e.get("weapon"):
            parts.append(f'weapon = {lua_str(e["weapon"])}')
        if e.get("rarity"):
            parts.append(f'rarity = {lua_str(e["rarity"])}')
        if e.get("value") is not None:
            parts.append(f'value = {lua_num(e["value"])}')
            parts.append(f'currency = {lua_str(e["currency"])}')
        if e.get("robux") is not None:
            parts.append(f'robux = {lua_num(e["robux"])}')
        if e.get("demand"):
            parts.append(f'demand = {lua_str(e["demand"])}')
        if e.get("status"):
            parts.append(f'status = {lua_str(e["status"])}')
        if e.get("conditions"):
            conds = ", ".join(f"{k} = {lua_num(v)}" for k, v in e["conditions"].items())
            parts.append(f"conditions = {{ {conds} }}")
        lines.append(f"\t[{lua_str(code)}] = {{ {', '.join(parts)} }},")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def main():
    raw = fetch_items()
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    cfg = {}
    for item in raw:
        code = item.get("code") or item.get("id")
        if not code:
            continue
        cfg[code] = clean(item)

    order = {"Sniper": 0, "Knife": 1, "Misc": 2}
    cfg = dict(
        sorted(
            cfg.items(),
            key=lambda kv: (order.get(kv[1]["type"], 9), -(kv[1]["value"] or 0), kv[0]),
        )
    )

    counts = {}
    for e in cfg.values():
        counts[e["type"]] = counts.get(e["type"], 0) + 1
    doc = {"generated": generated, "source": API, "counts": counts, "items": cfg}
    with open("values.json", "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")

    flat = {c: e["value"] for c, e in cfg.items() if e["value"] is not None and e["currency"] == "gems"}
    with open("gem_prices.json", "w", encoding="utf-8") as f:
        json.dump(flat, f, indent=1)
        f.write("\n")

    with open("values.lua", "w", encoding="utf-8") as f:
        f.write(to_lua(cfg, generated))

    print(f"[{generated}] wrote values.json ({len(cfg)} items), gem_prices.json ({len(flat)}), values.lua")


if __name__ == "__main__":
    main()
