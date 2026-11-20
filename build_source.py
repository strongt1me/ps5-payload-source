"""Builds payloads.json for the PS5 Payload Manager (itsPLK) from the individual manifests.

Usage:  python build_source.py   -> writes payloads.json next to this script.
The GitHub Action .github/workflows/update-source.yml runs this every hour
and commits payloads.json only when something has changed.
If a manifest fails, the script aborts and the old payloads.json stays in place.
"""
import json
import pathlib
import re
import urllib.request

SOURCE_NAME = "strongt1me PS5 Payloads"
AUTHOR = "strongt1me"
CATEGORY = "Utilities & Tools"

MANIFESTS = [
    # (URL, fallback ID for entries without "id")
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
            p["category"] = CATEGORY  # one common group in the manager
            for key in ("name", "filename", "url"):
                if not p.get(key):
                    raise SystemExit(f"{url}: required field '{key}' missing")
            if not re.fullmatch(r"[a-z0-9._-]+", p["id"]):
                raise SystemExit(f"invalid id: {p['id']}")
            if p["id"] in seen:
                raise SystemExit(f"duplicate id: {p['id']}")
            if p.get("checksum") and not re.fullmatch(r"[0-9a-fA-F]{64}", p["checksum"]):
                raise SystemExit(f"{p['id']}: checksum is not a SHA-256")
            seen.add(p["id"])
            payloads.append({k: p[k] for k in ORDER if k in p} |
                            {k: v for k, v in p.items() if k not in ORDER})

    out = pathlib.Path(__file__).with_name("payloads.json")
    # newline="\n": same file on Windows and in the GitHub Action (no spurious diffs)
    out.write_text(json.dumps({"name": SOURCE_NAME, "payloads": payloads},
                              indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8", newline="\n")
    print(f"{out.name}: {len(payloads)} payloads written")


if __name__ == "__main__":
    main()
