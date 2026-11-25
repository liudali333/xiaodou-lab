"""Discover explicitly shared public invite codes from X. Standard library only."""
import datetime as dt
import json
import os
import pathlib
import re
import urllib.error
import urllib.parse
import urllib.request

OUT = pathlib.Path("site/invite-radar/data.json")
QUERY = '("小豆" OR "Xiaodou") ("邀请码" OR "邀请碼" OR "invite code") -is:retweet'
LABEL = re.compile(r'(?:小豆\s*)?(?:邀请码|邀请碼|invite\s*code)\s*(?:是|为|為|[:：=])?\s*[\x60「『【"“]?\s*([A-Za-z0-9_-]{4,20})(?![A-Za-z0-9_-])', re.I)
EXCLUDE = re.compile(r'求码|求邀|求个|蹲码|收码|收购|出售|代购|代充|有偿|付费|闲鱼|私聊|私信|DM\s+me|selling|buying|¥|￥|\d+\s*元', re.I)
STOP = {"code", "invite", "xiaodou", "doubao", "http", "https", "free", "here", "share", "test", "none", "null", "please", "xxxx", "xxxxxx", "123456"}

def extract(text):
    if EXCLUDE.search(text) or not re.search(r'小豆|xiaodou', text, re.I):
        return []
    text = re.sub(r'https?://\S+', '', text)
    return [m.group(1) for m in LABEL.finditer(text)
            if m.group(1).lower() not in STOP and not re.fullmatch(r'[xX*]+', m.group(1))]

def collect(token):
    now = dt.datetime.now(dt.timezone.utc)
    params = {"query": QUERY, "max_results": 20, "tweet.fields": "created_at",
              "start_time": (now - dt.timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")}
    url = "https://api.x.com/2/tweets/search/recent?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token,
                                                "User-Agent": "XiaodouLabInviteRadar/0.1"})
    with urllib.request.urlopen(req, timeout=30) as response:
        payload = json.load(response)
    if payload.get("errors") and "data" not in payload:
        raise RuntimeError("X API returned errors")
    unique = {}
    for post in sorted(payload.get("data", []), key=lambda p: p.get("created_at", ""), reverse=True):
        pid = str(post.get("id", ""))
        if not pid.isdigit():
            continue
        for code in extract(post.get("text", "")):
            unique.setdefault(code.casefold(), {"code": code, "post_id": pid,
                              "url": "https://x.com/i/web/status/" + pid,
                              "created_at": post.get("created_at", ""), "status": "unverified"})
    return list(unique.values()), len(payload.get("data", []))

def main():
    token = os.environ.get("X_BEARER_TOKEN", "").strip()
    result = {"updated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
              "status": "not_configured", "scanned": 0, "items": []}
    if token:
        try:
            result["items"], result["scanned"] = collect(token)
            result["status"] = "ok"
        except urllib.error.HTTPError as exc:
            result["status"] = "api_error"
            result["http_status"] = exc.code
            print("X API HTTP status:", exc.code)
        except (urllib.error.URLError, TimeoutError, ValueError, RuntimeError) as exc:
            result["status"] = "api_error"
            print("Scan failed:", type(exc).__name__)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Scan status:", result["status"], "candidate count:", len(result["items"]))

if __name__ == "__main__":
    main()
