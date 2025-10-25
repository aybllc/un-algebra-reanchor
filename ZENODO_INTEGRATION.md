# Zenodo DOI Integration Guide

## Status: ✅ Release Created, Waiting for Zenodo

**GitHub Release:** https://github.com/aybllc/un-algebra-reanchor/releases/tag/v0.2.0
**Created:** 2025-10-25
**Zenodo Integration:** Enabled by repository owner

---

## How to Check Zenodo Status

### 1. Visit Your Zenodo GitHub Dashboard

Go to: **https://zenodo.org/account/settings/github/**

You should see:
- `aybllc/un-algebra-reanchor` listed with a toggle switch (ON)
- Recent webhook deliveries showing the v0.2.0 release

### 2. Check Webhook Delivery

Look for:
- **Status:** Green checkmark ✓ (successful delivery)
- **Trigger:** Release v0.2.0
- **Response:** 202 Accepted (Zenodo received the webhook)

### 3. Wait for DOI Assignment

Zenodo typically processes releases within **5-15 minutes**. You'll know it's complete when:

- A new entry appears in your Zenodo uploads: https://zenodo.org/uploads
- The DOI badge appears on the GitHub release page
- You receive an email from Zenodo (if notifications enabled)

---

## Once DOI is Assigned

### Option 1: Automated Update (Recommended)

We've created a helper script to update all files at once:

```bash
cd /got/un-algebra-reanchor

# Get your DOI number from Zenodo (example: 13957842)
# Full DOI will be: 10.5281/zenodo.13957842

./update_doi.sh 13957842  # Replace with your actual DOI number
```

This script will automatically update:
- `CITATION.cff`
- `.zenodo.json`
- `README.md`
- `README_API.md`
- `configs/uha_anchor.example.json`

Then commit and push:
```bash
git add -A
git commit -m "Update DOI to 10.5281/zenodo.XXXXXXX"
git push
```

### Option 2: Manual Update

**Find the DOI number** at: https://zenodo.org/account/settings/github/

**Update CITATION.cff:**
```bash
sed -i 's/doi: "10.5281\/zenodo.TBD"/doi: "10.5281\/zenodo.XXXXXXX"/' CITATION.cff
```

**Update .zenodo.json:**
```bash
sed -i 's/zenodo.TBD/zenodo.XXXXXXX/g' .zenodo.json
```

**Update other files:**
```bash
sed -i 's/zenodo.TBD/zenodo.XXXXXXX/g' configs/uha_anchor.example.json
```

---

## Add DOI Badge to README

Once DOI is assigned, add this badge to the top of `README.md`:

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
```

Place it near the top, after the title:

```markdown
# un-algebra-reanchor

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
[![CI](https://github.com/aybllc/un-algebra-reanchor/actions/workflows/ci.yml/badge.svg)](https://github.com/aybllc/un-algebra-reanchor/actions)

Reproducible retro-validation of metrology datasets...
```

---

## Verify DOI Integration

### 1. Check the DOI Resolves

Visit: `https://doi.org/10.5281/zenodo.XXXXXXX`

Should redirect to the Zenodo record page showing:
- Software title
- Version (0.2.0)
- Authors (Eric D. Martin)
- Files (source code archives)
- License (MIT)

### 2. Test Citation Download

On the Zenodo record page:
- Click "Citation" dropdown
- Verify BibTeX format matches CITATION.cff
- Download formats: APA, MLA, Chicago, etc.

### 3. Verify Badge Display

The DOI badge should display on:
- GitHub README.md (if badge added)
- Zenodo record page

---

## Troubleshooting

### Webhook Not Delivered

**Check:**
- Is the repository toggle ON at https://zenodo.org/account/settings/github/?
- Does your GitHub account have Zenodo OAuth access?
- Are webhooks allowed in GitHub repo settings?

**Fix:** Re-sync by toggling the repo OFF then ON again on Zenodo

### DOI Not Assigned After 30+ Minutes

**Possible Causes:**
- Zenodo server delay (check status: https://status.zenodo.org/)
- Large repository size (our repo is small, so unlikely)
- Metadata validation error

**Fix:** Contact Zenodo support with repository URL

### Wrong Metadata in Zenodo Record

**Fix:**
- Edit `.zenodo.json` with correct metadata
- Create a new release (v0.2.1) to trigger re-archival
- OR edit directly on Zenodo web interface

---

## Current File Status

**Files with DOI placeholders:**
```bash
$ grep -r "zenodo.TBD" .
./CITATION.cff:doi: "10.5281/zenodo.TBD"
./configs/uha_anchor.example.json:    "doi": "10.5281/zenodo.TBD",
```

**Files to update after DOI assignment:**
- [x] CITATION.cff (automated via `update_doi.sh`)
- [x] .zenodo.json (automated)
- [x] configs/uha_anchor.example.json (automated)
- [ ] README.md (add badge manually or via script)

---

## Expected DOI Format

**Full DOI:** `10.5281/zenodo.XXXXXXX`
**Where:** XXXXXXX is a 7-8 digit number assigned by Zenodo

**Examples:**
- 10.5281/zenodo.1234567
- 10.5281/zenodo.13957842

**DOI URL:** `https://doi.org/10.5281/zenodo.XXXXXXX`
**Zenodo Record:** `https://zenodo.org/records/XXXXXXX`

---

## Post-Integration Checklist

Once DOI is assigned and files are updated:

- [ ] DOI resolves correctly
- [ ] CITATION.cff updated with real DOI
- [ ] .zenodo.json updated
- [ ] configs/uha_anchor.example.json updated
- [ ] DOI badge added to README.md
- [ ] Changes committed and pushed
- [ ] Zenodo record metadata verified
- [ ] Citation downloads work (BibTeX, RIS, etc.)
- [ ] Updated session notes with final DOI

---

## Contact

**Zenodo Support:** https://zenodo.org/support
**GitHub:** https://github.com/aybllc/un-algebra-reanchor
**Documentation:** This file + README_API.md

---

**Created:** 2025-10-25
**Release:** v0.2.0
**Status:** Awaiting Zenodo DOI assignment
