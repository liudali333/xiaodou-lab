"""Import the public good1uck snapshot; never redeem or verify codes."""
import json
import pathlib
import re
import urllib.request

URL = "https://good1uck.github.io/xiaodou-codes/codes.json"
OUT = pathlib.Path("site/invite-radar/community.json")

def convert(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get("codes"), list):
        raise ValueError("invalid source format")
    items, seen = [], set()
    for row in payload["codes"]:
        if not isinstance(row, dict):
            continue
        code, post = row.get("code"), row.get("postId")
        if not isinstance(code, str) or not re.fullmatch(r"[A-Za-z0-9_-]{4,20}", code):
            continue
        if not isinstance(post, str) or not re.fullmatch(r"[0-9]{1,25}", post):
            continue
        if code.casefold() in seen:
            continue
        seen.add(code.casefold())
        items.append({"code": code, "post_id": post, "created_at": row.get("postedAtUtc") if isinstance(row.get("postedAtUtc"), str) else "", "source": "community"})
    return {"source_updated_at": payload.get("lastUpdated"), "items": items}

def main():
    try:
        req = urllib.request.Request(URL, headers={"User-Agent": "XiaodouLabRadar/1.0"})
        with urllib.request.urlopen(req, timeout=20) as response:
            raw = response.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError("source too large")
        data = convert(json.loads(raw))
        OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("Community candidates:", len(data["items"]))
    except (OSError, ValueError, TypeError) as exc:
        print("Community source unavailable:", type(exc).__name__)

if __name__ == "__main__":
    main()
