"""Baut payloads.json fuer den PS5 Payload Manager (itsPLK) aus den Einzel-Manifesten.

Aufruf:  python build_source.py   -> schreibt payloads.json neben dieses Skript.
Die GitHub Action .github/workflows/update-source.yml fuehrt das stuendlich aus
und committet payloads.json nur, wenn sich etwas geaendert hat.
Faellt ein Manifest aus, bricht das Skript ab und die alte payloads.json bleibt stehen.
"""
import json
import pathlib
import re
import urllib.request

SOURCE_NAME = "strongt1me PS5 Payloads"
AUTHOR = "strongt1me"
CATEGORY = "Utilities & Tools"

MANIFESTS = [
    # (URL, Ersatz-ID fuer Eintraege ohne "id")
    ("https://github.com/strongt1me/ps5-cooling-system-center-pro/releases/latest/download/payload-manager.json",
     "ps5-cooling-system-center-pro"),
    ("https://github.com/strongt1me/ps5-usb-formatierer/releases/latest/download/payload-manager.json",
     "usb-formatierer"),
    ("https://raw.githubusercontent.com/strongt1me/ps5-medic-ui-tool/main/payload-manager/ps5-medic.json",
     "ps5medic"),
]

ORDER = ["id", "name", "filename", "url", "description", "version", "last_update",
         "category", "checksum", "author", "details_url", "source"]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "payload-source-builder"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def main():
    payloads, seen = [], set()
    for url, fallback_id in MANIFESTS:
        data = fetch(url)
        items = data["payloads"] if isinstance(data, dict) else data
        for p in items:
            p = dict(p)
            p.setdefault("id", fallback_id)
            p.setdefault("author", AUTHOR)
            p["category"] = CATEGORY  # einheitliche Gruppe im Manager
            for key in ("name", "filename", "url"):
                if not p.get(key):
                    raise SystemExit(f"{url}: Pflichtfeld '{key}' fehlt")
            if not re.fullmatch(r"[a-z0-9._-]+", p["id"]):
                raise SystemExit(f"Ungueltige id: {p['id']}")
            if p["id"] in seen:
                raise SystemExit(f"Doppelte id: {p['id']}")
            if p.get("checksum") and not re.fullmatch(r"[0-9a-fA-F]{64}", p["checksum"]):
                raise SystemExit(f"{p['id']}: checksum ist kein SHA-256")
            seen.add(p["id"])
            payloads.append({k: p[k] for k in ORDER if k in p} |
                            {k: v for k, v in p.items() if k not in ORDER})

    out = pathlib.Path(__file__).with_name("payloads.json")
    # newline="\n": gleiche Datei unter Windows und in der GitHub Action (keine Schein-Diffs)
    out.write_text(json.dumps({"name": SOURCE_NAME, "payloads": payloads},
                              indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8", newline="\n")
    print(f"{out.name}: {len(payloads)} Payloads geschrieben")


if __name__ == "__main__":
    main()
