import os, json, pathlib, urllib.parse, urllib.request

_CACHE_DIR = os.path.expanduser("~/.unreanchor_cache")

class UHAError(Exception): pass

def _ensure_cache():
    os.makedirs(_CACHE_DIR, exist_ok=True)
    return _CACHE_DIR

def _read_local(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _build_auth_headers_for_url(url: str):
    """
    Build optional auth headers for domains that require an API key.
    Controlled by environment variables (can also be mirrored by CLI flags in the caller):
      - AYBLLC_API_DOMAIN: domain to match (default 'aybllc.org')
      - AYBLLC_API_KEY: the secret key
      - AYBLLC_API_AUTH_STYLE: one of: bearer | x-api-key | header:Name | query:param  (default: bearer)
      - AYBLLC_API_HEADER_NAME: when using 'header:Name', choose the header (default 'X-API-Key')
      - AYBLLC_API_QUERY_NAME: when using 'query:param', choose the param (default 'api_key')
    """
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
            # default to bearer if unknown
            headers["Authorization"] = f"Bearer {key}"
    return headers, qparams

def _download(url, local_path):
    # Attach optional auth headers if domain matches AYBLLC_API_DOMAIN
    headers, extra_qs = _build_auth_headers_for_url(url)
    if extra_qs:
        # merge querystring
        parsed = urllib.parse.urlparse(url)
        current = dict(urllib.parse.parse_qsl(parsed.query))
        current.update(extra_qs)
        new_q = urllib.parse.urlencode(current)
        url = urllib.parse.urlunparse(parsed._replace(query=new_q))

    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req) as r:
        data = r.read()
    with open(local_path, "wb") as f:
        f.write(data)
    return local_path

def _zenodo_record_api_from_doi_or_zenodo(addr: str):
    parsed = urllib.parse.urlparse(addr)
    base = addr.split("?")[0]
    if "zenodo." not in base:
        raise UHAError("Address must contain 'zenodo.<record_id>' for zenodo/doi schemes.")
    rec_id = base.split("zenodo.")[-1]
    if "/" in rec_id:
        rec_id = rec_id.split("/")[-1]
    if not rec_id.isdigit():
        raise UHAError(f"Could not parse Zenodo record id from: {addr}")
    return f"https://zenodo.org/api/records/{rec_id}"

def resolve_uha_address(address: str) -> dict:
    """
    Resolve a UHA address to an anchor JSON dict and return it.
    Caches remote content into ~/.unreanchor_cache for reproducibility.
    Supported:
      - file:/path/to/uha_anchor.json  (or plain relative/absolute path)
      - https://.../uha_anchor.json    (API key automatically attached for AYBLLC_API_DOMAIN)
      - zenodo:10.5281/zenodo.<id>?file=uha_anchor.json
      - doi:10.5281/zenodo.<id>?file=uha_anchor.json
    """
    if not address:
        raise UHAError("Empty UHA address.")
    _ensure_cache()

    # Local path or file: scheme
    if address.startswith("file:"):
        path = address[5:]
        return _read_local(path)

    if address.startswith("zenodo:") or address.startswith("doi:"):
        parsed = urllib.parse.urlparse(address)
        file_qs = dict(urllib.parse.parse_qsl(parsed.query))
        desired = file_qs.get("file", "uha_anchor.json")

        api = _zenodo_record_api_from_doi_or_zenodo(address)
        req = urllib.request.Request(api)
        with urllib.request.urlopen(req) as r:
            meta = json.load(r)
        # Try 'files' entry containing list of file dicts
        files = meta.get("files", [])
        if not isinstance(files, list):
            raise UHAError("Unexpected Zenodo API response; cannot locate files array.")
        match = next((f for f in files if f.get("key")==desired or f.get("key")==os.path.basename(desired)), None)
        if not match or "links" not in match or "self" not in match["links"]:
            raise UHAError(f"File '{desired}' not found in Zenodo record.")
        url = match["links"]["self"]
        local = os.path.join(_CACHE_DIR, f"zenodo_{os.path.basename(desired)}")
        _download(url, local)
        return _read_local(local)

    if address.startswith("http://") or address.startswith("https://"):
        name = os.path.basename(urllib.parse.urlparse(address).path) or "uha_anchor.json"
        local = os.path.join(_CACHE_DIR, name)
        _download(address, local)
        return _read_local(local)

    # Plain path
    p = pathlib.Path(address)
    if p.exists():
        return _read_local(str(p))

    raise UHAError(f"Unsupported UHA address or path not found: {address}")
