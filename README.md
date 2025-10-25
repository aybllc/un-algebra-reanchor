# un-algebra-reanchor

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17444740.svg)](https://doi.org/10.5281/zenodo.17444740)

Reproducible retro-validation of metrology datasets against UN-Algebra invariants and ISO 14253-1 decision rules.

## Overview

This package provides a test battery (`UN-T1` through `UN-T6`) for assessing measurement datasets under dual-reference-frame uncertainty quantification principles:

- **UN-T1** — Inequality coverage: `|measured - true_value| ≤ tolerance + U`
- **UN-T2** — ISO 14253-1 guard-band decisions (conform/nonconform/indeterminate)
- **UN-T3** — Cross-instrument coherence (same part measured by different instruments)
- **UN-T4** — Temporal drift detection (before/after calibration cut)
- **UN-T5** — Edge-of-spec behavior (indeterminate-rate near LSL/USL)
- **UN-T6** — Interval coverage: `true_value ∈ [measured - U, measured + U]`

All tests align with GUM (Guide to Uncertainty in Measurement) and ISO 14253-1 principles without requiring distributional assumptions.

## Install

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Usage

### CLI

```bash
# Generate synthetic dataset
python scripts/make_synthetic.py --out data/demo.csv

# Run validation
unreanchor run --data data/demo.csv --config configs/config.sample.yaml --out reports

# Outputs:
#   reports/report.json      — test results (UN-T1 through UN-T6)
#   reports/decisions.csv    — per-row guard-band decisions
```

### Makefile Shortcuts

```bash
make setup        # Install dependencies
make test         # Run pytest
make demo         # Generate synthetic data + run validation
make lint         # Run ruff linter (optional)
```

### Docker

```bash
make docker-build
make docker-run
```

Or manually:

```bash
docker build -t un-algebra-reanchor:0.1.0 .
docker run --rm -v $PWD:/work -w /work un-algebra-reanchor:0.1.0 \
  unreanchor run --data data/demo.csv --config configs/config.sample.yaml --out /work/reports
```

## Configuration

See `configs/config.sample.yaml` for column mappings. The tool supports:

- **Expanded uncertainty** (`uncertainty_U` column) OR
- **Standard uncertainty + coverage factor** (`sigma` column + `coverage_k` param, default k=2)

Parameters:
- `gamma`: Guard-band multiplier (default 1.0)
- `edge_delta`: Proximity threshold for edge-of-spec tests (default 0.1)
- `calibration_cut`: ISO timestamp for temporal drift (UN-T4)

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`):
1. Runs unit tests
2. Executes demo on synthetic data
3. Uploads `report.json` and `decisions.csv` as artifacts

## Minting a DOI

1. **Enable Zenodo integration** for your GitHub repository at https://zenodo.org/account/settings/github/
2. **Create a GitHub Release** (e.g., `v0.1.0`)
3. Zenodo auto-archives and assigns a DOI
4. **Update** `CITATION.cff` and `.zenodo.json` with the real DOI

## ISO/GUM Alignment

- **ISO 14253-1** guard-band decisions avoid false accept/reject
- **GUM** expanded uncertainty with coverage factor k
- **PAC bounds** (Probably Approximately Correct) without distributional assumptions

## Citation

```bibtex
@software{unalgebra_reanchor,
  title = {un-algebra-reanchor: UN-Algebra retro-validation tests},
  author = {Martin, Eric D.},
  year = {2025},
  version = {0.1.0},
  doi = {10.5281/zenodo.TBD},
  url = {https://github.com/aybllc/un-algebra-reanchor}
}
```

See `CITATION.cff` for full metadata.

## License

MIT License — See `LICENSE` file.

## Support

- **Issues:** https://github.com/aybllc/un-algebra-reanchor/issues
- **Documentation:** This README + inline docstrings in `src/un_reanchor/`

---

**All Your Baseline LLC**
*Reproducible metrology validation under UN-Algebra principles*
