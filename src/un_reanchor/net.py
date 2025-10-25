import os, urllib.parse, urllib.request, pathlib

_CACHE_DIR = os.path.expanduser("~/.unreanchor_cache")

def _ensure_cache():
    os.makedirs(_CACHE_DIR, exist_ok=True)
    return _CACHE_DIR

def _build_auth_headers_for_url(url: str):
    # Re-use the same env-based scheme as in uha.py for consistency
    import os, urllib.parse
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc.lower()
    dom = os.getenv("AYBLLC_API_DOMAIN", "aybllc.org").lower()
    key = os.getenv("AYBLLC_API_KEY", "").strip()
    style = os.getenv("AYBLLC_API_AUTH_STYLE", "bearer").strip().lower()
    headers = {}
    qparams = {}

    if dom and host.endswith(dom) and key:
        if style == "bearer":
            headers["Authorization"] = f"Bearer {key}"
        elif style == "x-api-key":
            headers["X-API-Key"] = key
        elif style.startswith("header:"):
            name = style.split(":",1)[1].strip() or os.getenv("AYBLLC_API_HEADER_NAME","X-API-Key")
            headers[name] = key
        elif style.startswith("query"):
            pname = os.getenv("AYBLLC_API_QUERY_NAME","api_key")
            qparams[pname] = key
        else:
            headers["Authorization"] = f"Bearer {key}"
    return headers, qparams

def fetch_to_cache(url: str) -> str:
    """
    Download a remote resource (CSV/JSON/etc.) to cache, attaching API key
    headers/query params for AYBLLC_API_DOMAIN if configured.
    Returns the local cached file path.
    """
    _ensure_cache()
    import hashlib
    headers, q = _build_auth_headers_for_url(url)
    if q:
        parsed = urllib.parse.urlparse(url)
        current = dict(urllib.parse.parse_qsl(parsed.query))
        current.update(q)
        new_q = urllib.parse.urlencode(current)
        url = urllib.parse.urlunparse(parsed._replace(query=new_q))

    # deterministic cache file name
    h = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    name = os.path.basename(urllib.parse.urlparse(url).path) or "payload.bin"
    local = os.path.join(_CACHE_DIR, f"{h}_{name}")
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req) as r:
        data = r.read()
    with open(local, "wb") as f:
        f.write(data)
    return local
