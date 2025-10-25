# API Key Integration (aybllc.org)

This patch enables **API-key authenticated** fetches for:
- **UHA anchors** (JSON) via `--uha` addresses (http/https/zenodo/doi/file)
- **Remote datasets** via `--data` URLs

## Configure secrets

**Local (.env or shell):**
```bash
export AYBLLC_API_DOMAIN=aybllc.org
export AYBLLC_API_KEY=YOUR_SECRET
export AYBLLC_API_AUTH_STYLE=bearer   # or: x-api-key | header:X-Auth-Token | query:api_key
# optional:
export AYBLLC_API_HEADER_NAME=X-API-Key
export AYBLLC_API_QUERY_NAME=api_key
```

**GitHub Actions (Settings → Secrets and variables → Actions):**
- Add `AYBLLC_API_KEY` (and others as needed).
- In CI, they are automatically used when present.

## Usage

**Cosmology (UN‑CT1) with UHA address**
```bash
unreanchor run \
  --data https://aybllc.org/api/v1/h0_pairs.csv \
  --config configs/config.sample.yaml \
  --out reports \
  --uha https://aybllc.org/api/v1/uha_anchor.json
```

The client will attach your API key to both URLs **only when the host ends with `aybllc.org`** and according to `AYBLLC_API_AUTH_STYLE`.

## Notes
- Secrets are never written to output files; only used as HTTP headers (or query if configured).
- Remote files are cached under `~/.unreanchor_cache/` for reproducibility.
- If your API requires a different header, set `AYBLLC_API_AUTH_STYLE=header:Your-Header`.
